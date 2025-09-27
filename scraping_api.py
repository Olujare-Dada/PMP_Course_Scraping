from flask import Flask, request, render_template
from flask_cors import CORS
import requests
import os
from Html_File import Html_File
from Html_Parser import Html_Parser
from Gpt_Extractor import Gpt_Extractor
from typing import Dict

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/upload": {"origins": "*"}})


# Supabase config
SUPABASE_URL = os.getenv("DATABASE_URL")  # Or hardcode for testing
SUPABASE_KEY = os.getenv("SECRET_KEY")
SUPABASE_TABLE = "questions"

@app.route("/")
def show_upload_form():
    return render_template("./scraping_front_end/index.html")

@app.route("/test")
def show_quiz_page():
    return render_template("PMP_Qstn_BUCKET_1-1.html")


def _check_file(milestone_id: str, uploaded_file):
    if not milestone_id or not uploaded_file:
        return "Missing data", 400

    content = uploaded_file.read().decode("utf-8")
    html_file = Html_File(content=content, filename=uploaded_file.filename)
    
    if not html_file.is_html():
        return "Invalid file type", 400

    return html_file, 200


def _parse_html(gpt_extractor: Gpt_Extractor, html_file):
    # Parse HTML
    html_parser = Html_Parser(html_file, gpt_extractor)

    # Get Questions, Options & Answers
    questions: Dict = html_parser.get_questions()
    answers: Dict = html_parser.get_answers()
    options: Dict = html_parser.get_options()

    return questions, answers, options

def _normalize_keys(questions, answers, options):
    new_questions = dict(zip(answers.keys(), questions.values()))
    new_options = dict(zip(answers.keys(), options.values()))
    return new_questions, answers, new_options

@app.route("/upload", methods=["POST", "OPTIONS"])
def upload():
    if request.method == "OPTIONS":
        return "", 204
    milestone_id = request.form.get("milestone_id")
    uploaded_file = request.files["file"]

    html_file, response_code = _check_file(milestone_id, uploaded_file)

    gpt_extractor = Gpt_Extractor()
    questions, answers, options = _parse_html(gpt_extractor, html_file)

    questions, answers, options = _normalize_keys(questions, answers, options)

    if not (len(questions) == len(answers) == len(options)):
        return "Uneven number of question elements.\nQuestions={len(questions)}\nAnswers={len(answers)}\nOptions={len(options)}", 500

    # Post to Supabase
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    data = []
    for question_num in questions:
        data.append({
            "milestone_id": int(milestone_id),
            "question_text": questions[question_num],
            "options": options[question_num],
            "correct_answer": answers[question_num],
            "explanation": ""
        })

    response = requests.post(f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}", headers=headers, json=data)

    if response.status_code in (200, 201):
        return "Upload successful!"
    else:
        return f"Upload failed: {response.text}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5222))
    app.run(host="0.0.0.0", port=port, debug=False)
