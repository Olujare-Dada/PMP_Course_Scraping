from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict
from enum import Enum
import os

load_dotenv()


client = OpenAI()


class AnswerExtract(BaseModel):
    question_number: List[str]
    answer: List[str]

class QuestionsAnswers(BaseModel):
    answer_extracts: List[AnswerExtract]

    

class PromptTemplate(Enum):
    system_prompt = "You are a precise data extraction assistant."
    user_prompt = """Extract the correct answers from the JavaScript object called `correctAnswers` inside this HTML <script> tag.

For each entry, extract:
- The question number (as an integer, e.g., 1, 2, 3)
- The list of correct answer options (e.g., ["A"], ["B", "C"])
- Follow the exact numbering of the script 

Return the output as a JSON array following this Pydantic-compatible schema:

answer_extracts=[AnswerExtract(question_number=['1'], answer=['D']), AnswerExtract(question_number=['2'], answer=['C']), AnswerExtract(question_number=['3'], answer=['D']), AnswerExtract(question_number=['4'], answer=['B']), AnswerExtract(question_number=['5'], answer=['D']), AnswerExtract(question_number=['6'], answer=['C']), AnswerExtract(question_number=['7'], answer=['A']), AnswerExtract(question_number=['8'], answer=['A']), AnswerExtract(question_number=['9'], answer=['B']), AnswerExtract(question_number=['10'], answer=['A'])]

Here is the raw <script> content:
{script_content}
"""

class Gpt_Extractor:

    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL")

    def __str__(self):
        return f"Extractor Model: {self.model}"

    def get_gpt_response(self, script_content):
        system_prompt = PromptTemplate.system_prompt.value
        user_prompt = PromptTemplate.user_prompt.value
        
        response = client.responses.parse(
            model= self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt.format(script_content = script_content),
                },
            ],
            text_format=QuestionsAnswers,
        )

        return response.output_parsed

    
