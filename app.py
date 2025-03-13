import os
import subprocess
import streamlit as st
import tempfile
import re
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

CHECKSTYLE_PATH = "C:\\Users\\shree\\Downloads\\checkstyle-10.21.4-all (1).jar"

def check_code_conventions(file_path, language):
    if language == "java":
        if not os.path.exists(CHECKSTYLE_PATH):
            return "Checkstyle not found. Please install and configure it properly."

        try:
            result = subprocess.run(
                ["java", "-jar", CHECKSTYLE_PATH, "-c", "google_checks.xml", file_path],
                capture_output=True,
                text=True
            )
            return format_checkstyle_output(result.stdout) if result.stdout else "No style issues found."
        except FileNotFoundError:
            return "Java not found. Ensure Java is installed and added to PATH."

    return "Convention checks are currently only available for Java."

def format_checkstyle_output(raw_output):
    issues = []
    indentation_issues = {}

    for line in raw_output.split("\n"):
        match = re.match(r"\[WARN\] (.+?):(\d+):(\d+): (.+)", line)
        if match:
            _, line_no, col_no, message = match.groups()
            
            if "indentation" in message.lower():
                if line_no in indentation_issues:
                    indentation_issues[line_no].append(message)
                else:
                    indentation_issues[line_no] = [message]
            else:
                issues.append(f"Line {line_no}, Column {col_no}: {message}")

    if indentation_issues:
        issues.append("Indentation Issues:")
        for line_no, messages in indentation_issues.items():
            issues.append(f"   - Line {line_no}: {', '.join(set(messages))}")

    return "\n".join(issues) if issues else "No style issues found."

def best_practices_review(code, language):
    if language != "java":
        return "Best practice checks are currently only available for Java.", code, 100

    suggestions = []
    improved_code = code

    guideline_explanations = {
        "1": "Follow Java naming conventions.",
        "2": "Use Java Streams and Lambdas instead of imperative loops.",
        "3": "Use Optional<T> to avoid NullPointerException.",
        "4": "Use defensive copying for collections.",
        "5": "Catch specific exceptions before generic ones.",
        "6": "Use appropriate data structures.",
        "7": "Use private methods unless necessary.",
        "8": "Code to interfaces instead of concrete implementations.",
        "9": "Avoid unnecessary interfaces.",
        "10": "Override hashCode() when overriding equals().",
    }

    if re.search(r'\b[A-Z_]+\b', code):
        suggestions.append("Guideline 1. " + guideline_explanations["1"])

    if re.search(r'for\s*\(.*:.*\)', code):
        suggestions.append("Guideline 2. " + guideline_explanations["2"])
        improved_code = re.sub(r'for\s*\((.*):(.*)\)\s*\{(.*?)\}', r'\2.stream().forEach(\1 -> {\3})', improved_code, flags=re.DOTALL)

    if "== null" in code:
        suggestions.append("Guideline 3. " + guideline_explanations["3"])
        improved_code = re.sub(r'(\w+)\s*==\s*null', r'Optional.ofNullable(\1).isEmpty()', improved_code)

    if re.search(r'private\s+final\s+List<\w+>\s+\w+;', code):
        suggestions.append("Guideline 4. " + guideline_explanations["4"])

    if re.search(r'catch\s*\(\s*Exception\s+', code):
        suggestions.append("Guideline 5. " + guideline_explanations["5"])

    if "Vector<" in code:
        suggestions.append("Guideline 6. " + guideline_explanations["6"])

    if re.search(r'public\s+\w+\s+\w+\(', code):
        suggestions.append("Guideline 7. " + guideline_explanations["7"])
        improved_code = re.sub(r'public\s+(\w+\s+\w+\()', r'private \1', improved_code)

    result_text = "\n".join(suggestions) if suggestions else "No best practice violations found."
    
    total_guidelines = len(guideline_explanations)
    deductions = len(suggestions)
    compliance_score = max(0, 100 - (deductions * (100 // total_guidelines)))

    return result_text, improved_code, compliance_score

def plot_compliance_score(score):
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(["Compliance Score"], [score], color="green" if score >= 75 else "orange" if score >= 50 else "red")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score (%)")
    ax.set_title("Code Compliance Score")
    return fig

st.set_page_config(page_title="Code Reviewer", layout="wide")
st.sidebar.title("Code Review")
option = st.sidebar.radio("Choose an option:", ["Review Code", "Ask a Question"])

st.title("Code Reviewer")

if option == "Review Code":
    st.write("Upload your code file below for review.")
    uploaded_file = st.file_uploader("Upload a code file", type=["java", "py", "cpp", "c", "js"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        with open(temp_file_path, "r", encoding="utf-8") as file:
            code_content = file.read()

        language = "java" if uploaded_file.name.endswith(".java") else "other"

        if st.button("Review Code"):
            if code_content.strip():
                convention_issues = check_code_conventions(temp_file_path, language)
                best_practice_suggestions, improved_code, compliance_score = best_practices_review(code_content, language)

                st.subheader(f"Compliance Score: {compliance_score}%")
                st.pyplot(plot_compliance_score(compliance_score))
                st.subheader("Code Convention Issues:")
                st.text_area("Issues Found:", value=convention_issues, height=200)
                st.subheader("Best Practices Suggestions:")
                st.text_area("Suggestions:", value=best_practice_suggestions, height=200)
                st.subheader("Improved Code:")
                st.code(improved_code, language=language)
            else:
                st.warning("Please upload a valid code file before reviewing.")

elif option == "Ask a Question":
    st.write("Ask a programming-related question below.")
    user_question = st.text_area("Your Question:")
    if st.button("Get Answer"):
        if user_question.strip():
            st.write("Searching for an answer...")
        else:
            st.warning("Please enter a question before proceeding.")
