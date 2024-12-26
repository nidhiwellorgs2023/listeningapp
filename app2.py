from flask import Flask, jsonify, request,render_template
import json

app = Flask(__name__)

# Load the IELTS exam data from JSON file
with open('backend\listening2.json', 'r') as file:
    ielts_data = json.load(file)
@app.route('/')
def home():
    """Render the IELTS exam HTML page."""
    return render_template('index.html', ielts_data=ielts_data)

# Function to calculate band score
def calculate_band_score(correct_count, total_questions):
    if total_questions == 0:
        return 0
    percentage = (correct_count / total_questions) * 100
    if percentage >= 85:
        return 9
    elif percentage >= 75:
        return 8
    elif percentage >= 65:
        return 7
    elif percentage >= 55:
        return 6
    elif percentage >= 45:
        return 5
    elif percentage >= 35:
        return 4
    elif percentage >= 25:
        return 3
    elif percentage >= 15:
        return 2
    elif percentage >= 5:
        return 1
    else:
        return 0

# Function to get band description
def get_band_description(band_score):
    band_descriptions = {
        9: {"skill_level": "Expert user", "description": "Fully operational command of the language: fluent, precise, and well-understood."},
        8: {"skill_level": "Very good user", "description": "Efficient in language use with minor inaccuracies or misunderstandings in unfamiliar contexts."},
        7: {"skill_level": "Good user", "description": "Handles language well with occasional lapses; understands detailed arguments effectively."},
        6: {"skill_level": "Competent user", "description": "Effective in familiar situations but prone to errors in complex language."},
        5: {"skill_level": "Modest user", "description": "Basic command of language, often requiring repetition or clarification for accuracy."},
        4: {"skill_level": "Limited user", "description": "Copes with simple situations but struggles with understanding or expressing detailed meaning."},
        3: {"skill_level": "Extremely limited user", "description": "Communicates basic needs but suffers frequent communication breakdowns."},
        2: {"skill_level": "Intermittent user", "description": "Uses isolated words and phrases to meet immediate needs; struggles with understanding."},
        1: {"skill_level": "Non-user", "description": "Unable to use language beyond isolated words."},
        0: {"skill_level": "Did not attempt test", "description": "No attempt to answer the test questions."}
    }
    return band_descriptions.get(band_score, {"skill_level": "Unknown", "description": "No description available."})

@app.route('/fetch_exam', methods=['GET'])
def fetch_exam():
    """Fetch the IELTS exam set."""
    return jsonify(ielts_data)

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    """Evaluate user's answers and return results."""
    user_answers = request.json.get('answers', {})
    results = []
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    for part_name, part_data in ielts_data[0].items():
        if part_name.startswith("Part"):
            for question in part_data['questions']:
                if question.get('type') == 'diagram':
                    # Evaluate diagram labeling questions
                    correct_labels = {label['id']: label['correct_label'] for label in question['labels']}
                    user_labels = user_answers.get(str(question['question']), {})
                    if user_labels == correct_labels:
                        results.append({
                            'id': question['question'],
                            'status': 'correct',
                            'correct_answer': correct_labels
                        })
                        correct_count += 1
                    elif not user_labels:
                        results.append({
                            'id': question['question'],
                            'status': 'unanswered',
                            'correct_answer': correct_labels
                        })
                        unanswered_count += 1
                    else:
                        results.append({
                            'id': question['question'],
                            'status': 'incorrect',
                            'correct_answer': correct_labels
                        })
                        incorrect_count += 1
                elif 'matches' in question:
                    # Evaluate match-the-following questions
                    correct_matches = {item.get('apartment', item.get('person')): item.get('facility', item.get('work')) for item in question['matches']}
                    user_matches = user_answers.get(str(question['question']), {})
                    if user_matches == correct_matches:
                        results.append({
                            'id': question['question'],
                            'status': 'correct',
                            'correct_answer': correct_matches
                        })
                        correct_count += 1
                    elif not user_matches:
                        results.append({
                            'id': question['question'],
                            'status': 'unanswered',
                            'correct_answer': correct_matches
                        })
                        unanswered_count += 1
                    else:
                        results.append({
                            'id': question['question'],
                            'status': 'incorrect',
                            'correct_answer': correct_matches
                        })
                        incorrect_count += 1
                else:
                    # Evaluate other question types
                    correct_answer = question['answer']
                    user_answer = user_answers.get(str(question['question']), None)

                    if user_answer is None or user_answer.strip() == "":
                        results.append({
                            'id': question['question'],
                            'status': 'unanswered',
                            'correct_answer': correct_answer
                        })
                        unanswered_count += 1
                    elif user_answer.strip().lower() == correct_answer.strip().lower():
                        results.append({
                            'id': question['question'],
                            'status': 'correct',
                            'correct_answer': correct_answer
                        })
                        correct_count += 1
                    else:
                        results.append({
                            'id': question['question'],
                            'status': 'incorrect',
                            'correct_answer': correct_answer
                        })
                        incorrect_count += 1

    total_questions = correct_count + incorrect_count + unanswered_count
    band_score = calculate_band_score(correct_count, total_questions)
    band_description = get_band_description(band_score)

    result_summary = {
        'correct': correct_count,
        'incorrect': incorrect_count,
        'unanswered': unanswered_count,
        'band_score': band_score,
        'skill_level': band_description["skill_level"],
        'description': band_description["description"]
    }

    return jsonify({
        'results': results,
        'summary': result_summary
    })

if __name__ == '__main__':
    app.run(debug=True)
