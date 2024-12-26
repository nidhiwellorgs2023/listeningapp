import streamlit as st
import requests

# Set the base URL for the Flask API
BASE_URL = "http://127.0.0.1:5000"

st.title("IELTS Listening Exam")

# Fetch the exam data
st.subheader("Exam")
response = requests.get(f"{BASE_URL}/fetch_exam")
if response.status_code == 200:
    exam_data = response.json()
    user_answers = {}

    for part_name, part_data in exam_data[0].items():
        if part_name.startswith("Part"):
            st.write(f"### {part_name}")

            # Handle audio playback
            if part_data.get('audio'):
                st.audio(part_data['audio'], format="audio/mp3")  # Provide audio player
            else:
                st.error("Audio file not available for this part.")

            for question in part_data['questions']:
                qid = question['question']
                st.write(f"**{qid}**")

                if question.get('type') == 'diagram':
                    # Display the diagram
                    if question.get('image'):
                        st.image(question['image'], caption="Label the diagram")  # Show the image
                    else:
                        st.error("Diagram not available for this question.")

                    # Collect labels for each diagram point
                    diagram_labels = {}
                    for label in question['labels']:
                        label_id = label['id']
                        diagram_labels[label_id] = st.selectbox(
                            f"Label for {label_id}:",
                            question['options'],
                            key=f"diagram_{part_name}_{qid}_{label_id}"
                        )
                    user_answers[qid] = diagram_labels

                elif 'options' in question:
                    # Multiple Choice Questions
                    user_answers[qid] = st.radio(
                        "Select your answer:",
                        question['options'],
                        key=f"mcq_{part_name}_{qid}"
                    )

                elif 'matches' in question:
                    # Match the Following Questions
                    dropdown_answers = {}
                    for idx, item in enumerate(question['matches']):
                        # Determine match type dynamically based on keys
                        left = item.get('apartment', item.get('person', item.get('strategy', item.get('feature'))))
                        options = item.get('facility', item.get('work', item.get('benefit', item.get('description'))))

                        dropdown_answers[left] = st.selectbox(
                            f"Match for {left}:",
                            [options],
                            key=f"match_{part_name}_{qid}_{idx}"
                        )
                    user_answers[qid] = dropdown_answers

                else:
                    # Fill in the Blanks Questions
                    user_answers[qid] = st.text_input(
                        "Your answer:", key=f"fill_{part_name}_{qid}"
                    )

    # Submit the answers
    if st.button("Submit Exam"):
        payload = {"answers": user_answers}
        submit_response = requests.post(f"{BASE_URL}/submit_exam", json=payload)

        if submit_response.status_code == 200:
            result = submit_response.json()
            st.subheader("Results")
            for res in result['results']:
                st.write(f"Question {res['id']}: {res['status'].capitalize()}")
                if res['status'] != "correct":
                    st.write(f"Correct Answer: {res['correct_answer']}")

            summary = result['summary']
            st.write("---")
            st.write(f"**Correct:** {summary['correct']}")
            st.write(f"**Incorrect:** {summary['incorrect']}")
            st.write(f"**Unanswered:** {summary['unanswered']}")
            st.write(f"**Band Score:** {summary['band_score']}")
            st.write(f"**Skill Level:** {summary['skill_level']}")
            st.write(f"**Description:** {summary['description']}")
else:
    st.error("Failed to fetch exam data. Please ensure the Flask API is running.")
