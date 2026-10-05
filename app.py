import streamlit as st
from pypdf import PdfReader
from rapidfuzz import fuzz
from collections import Counter
import re

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="AI Exam Paper Analyzer",
    page_icon="📚",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📚 AI Exam Paper Analyzer")

st.write(
    "Upload previous-year exam papers to find repeated, "
    "similar, and important questions."
)

# --------------------------------------------------
# PDF UPLOAD
# --------------------------------------------------

uploaded_files = st.file_uploader(
    "📄 Upload PDF question papers",
    type=["pdf"],
    accept_multiple_files=True
)

# --------------------------------------------------
# PROCESS FILES
# --------------------------------------------------

if uploaded_files:

    st.success(
        f"Successfully uploaded {len(uploaded_files)} paper(s)."
    )

    all_questions = []

    # --------------------------------------------------
    # READ EACH PDF
    # --------------------------------------------------

    for file in uploaded_files:

        st.subheader(f"📄 {file.name}")

        reader = PdfReader(file)

        st.write(
            f"📑 Number of pages: {len(reader.pages)}"
        )

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        # --------------------------------------------------
        # SHOW EXTRACTED TEXT
        # --------------------------------------------------

        with st.expander("🔍 View extracted text"):

            st.text(text[:10000])

        # --------------------------------------------------
        # EXTRACT QUESTIONS
        # --------------------------------------------------

        lines = text.split("\n")

        for line in lines:

            line = line.strip()

            if len(line) >= 30:

                all_questions.append(
                    {
                        "question": line,
                        "paper": file.name
                    }
                )

    st.divider()

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    st.header("📊 Analysis Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📄 Papers",
            len(uploaded_files)
        )

    with col2:
        st.metric(
            "❓ Questions Found",
            len(all_questions)
        )

    # --------------------------------------------------
    # FIND SIMILAR QUESTIONS
    # --------------------------------------------------

    repeated_questions = []

    if len(all_questions) >= 2:

        for i in range(len(all_questions)):

            for j in range(i + 1, len(all_questions)):

                q1 = all_questions[i]["question"]
                q2 = all_questions[j]["question"]

                # Calculate similarity
                similarity = fuzz.token_set_ratio(
                    q1,
                    q2
                )

                # Similarity threshold
                if similarity >= 75:

                    repeated_questions.append(
                        {
                            "Question 1": q1,
                            "Paper 1": all_questions[i]["paper"],
                            "Question 2": q2,
                            "Paper 2": all_questions[j]["paper"],
                            "Similarity": similarity
                        }
                    )

    with col3:

        st.metric(
            "🔁 Similar Questions",
            len(repeated_questions)
        )

    st.divider()

    # --------------------------------------------------
    # SIMILAR QUESTIONS
    # --------------------------------------------------

    st.header("🔁 Repeated / Similar Questions")

    if repeated_questions:

        st.success(
            f"Found {len(repeated_questions)} similar/repeated questions!"
        )

        for item in repeated_questions:

            st.write("### 🔁 Similar Question")

            st.write(
                f"**Paper 1:** {item['Paper 1']}"
            )

            st.write(
                f"**Question:** {item['Question 1']}"
            )

            st.write(
                f"**Paper 2:** {item['Paper 2']}"
            )

            st.write(
                f"**Similar Question:** {item['Question 2']}"
            )

            st.write(
                f"**Similarity:** "
                f"{item['Similarity']:.2f}%"
            )

            st.divider()

    else:

        st.info(
            "No repeated or highly similar questions were found."
        )

    # --------------------------------------------------
    # IMPORTANT QUESTIONS
    # --------------------------------------------------

    st.header("⭐ Important Questions")

    if repeated_questions:

        # Count how many times each question appears
        question_frequency = Counter()

        for item in repeated_questions:

            question_frequency[
                item["Question 1"]
            ] += 1

            question_frequency[
                item["Question 2"]
            ] += 1

        # Sort questions by frequency
        important_questions = (
            question_frequency
            .most_common(10)
        )

        st.write(
            "Questions appearing repeatedly across "
            "previous papers are considered important."
        )

        for index, (question, count) in enumerate(
            important_questions,
            start=1
        ):

            st.write(
                f"**{index}. {question}**"
            )

            st.write(
                f"🔁 Similar/repeated occurrences: {count}"
            )

            st.divider()

    else:

        st.info(
            "Important questions will appear when "
            "similar questions are detected."
        )
            # --------------------------------------------------
    # TOPIC ANALYSIS
    # --------------------------------------------------

    st.header("📚 Topic Analysis")

    topic_keywords = {
        "Python": ["python", "pandas", "numpy"],
        "Java / OOP": ["java", "class", "object", "inheritance", "polymorphism"],
        "DBMS": ["database", "dbms", "sql", "normalization", "transaction"],
        "Computer Networks": ["network", "tcp", "ip", "routing", "protocol"],
        "Operating Systems": ["operating system", "os", "process", "deadlock", "memory"],
        "Data Structures": ["array", "stack", "queue", "tree", "graph", "linked list"],
    }

    topic_counts = Counter()

    for item in all_questions:

        question_text = item["question"].lower()

        for topic, keywords in topic_keywords.items():

            for keyword in keywords:

                if keyword in question_text:

                    topic_counts[topic] += 1

                    break

    if topic_counts:

        st.write(
            "The following topics were detected in the uploaded exam papers:"
        )

        for topic, count in topic_counts.most_common():

            st.write(
                f"📌 **{topic}** — {count} question(s)"
            )

    else:

        st.info(
            "No predefined topics were detected."
        )
            # --------------------------------------------------
    # MARKS ANALYSIS
    # --------------------------------------------------

    st.header("📊 Marks Analysis")

    total_marks = 0
    marks_found = []

    for item in all_questions:

        question_text = item["question"]

        # Find marks such as:
        # [5]
        # [10 marks]
        # 5 marks
        # 10M
        # 10 M

        matches = re.findall(
            r"\[\s*(\d+)\s*(?:marks?|M)?\s*\]"
            r"|\b(\d+)\s*(?:marks?|M)\b",
            question_text,
            flags=re.IGNORECASE
        )

        for match in matches:

            mark_value = match[0] or match[1]

            if mark_value:

                mark_value = int(mark_value)

                marks_found.append(mark_value)

                total_marks += mark_value

    if marks_found:

        st.success(
            f"Detected marks in {len(marks_found)} question(s)."
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "📊 Total Detected Marks",
                total_marks
            )

        with col2:

            st.metric(
                "❓ Questions With Marks",
                len(marks_found)
            )

        st.write("### 📋 Marks Distribution")

        mark_counts = Counter(marks_found)

        for mark, count in sorted(mark_counts.items()):

            st.write(
                f"**{mark} marks** → {count} question(s)"
            )

    else:

        st.info(
            "No marks were detected. "
            "Make sure the PDF contains marks such as [5], [10 marks], or 10M."
        )
            # --------------------------------------------------
    # DIFFICULTY ANALYSIS
    # --------------------------------------------------

    st.header("🎯 Difficulty Analysis")

    easy_keywords = [
        "define",
        "what is",
        "list",
        "state",
        "name",
        "identify",
        "write short note"
    ]

    hard_keywords = [
        "derive",
        "prove",
        "analyze",
        "analyse",
        "design",
        "compare and justify",
        "evaluate",
        "implement",
        "optimize",
        "discuss in detail"
    ]

    difficulty_counts = Counter()

    difficulty_questions = {
        "Easy": [],
        "Medium": [],
        "Hard": []
    }

    for item in all_questions:

        question = item["question"]
        question_lower = question.lower()

        # Check for hard questions
        if any(
            keyword in question_lower
            for keyword in hard_keywords
        ):

            difficulty = "Hard"

        # Check for easy questions
        elif any(
            keyword in question_lower
            for keyword in easy_keywords
        ):

            difficulty = "Easy"

        # Everything else is considered medium
        else:

            difficulty = "Medium"

        difficulty_counts[difficulty] += 1

        difficulty_questions[difficulty].append(
            question
        )

    # --------------------------------------------------
    # DISPLAY DIFFICULTY SUMMARY
    # --------------------------------------------------

    if all_questions:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🟢 Easy",
                difficulty_counts["Easy"]
            )

        with col2:

            st.metric(
                "🟡 Medium",
                difficulty_counts["Medium"]
            )

        with col3:

            st.metric(
                "🔴 Hard",
                difficulty_counts["Hard"]
            )

        st.divider()

        # --------------------------------------------------
        # SHOW QUESTIONS BY DIFFICULTY
        # --------------------------------------------------

        st.subheader("📋 Questions by Difficulty")

        with st.expander("🟢 View Easy Questions"):

            if difficulty_questions["Easy"]:

                for question in difficulty_questions["Easy"]:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.info(
                    "No easy questions detected."
                )

        with st.expander("🟡 View Medium Questions"):

            if difficulty_questions["Medium"]:

                for question in difficulty_questions["Medium"]:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.info(
                    "No medium questions detected."
                )

        with st.expander("🔴 View Hard Questions"):

            if difficulty_questions["Hard"]:

                for question in difficulty_questions["Hard"]:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.info(
                    "No hard questions detected."
                )

    else:

        st.info(
            "Upload exam papers to perform difficulty analysis."
        )