from Gpt_Extractor import Gpt_Extractor, QuestionsAnswers
from bs4 import BeautifulSoup
from Html_File import Html_File


class Html_Parser:

    def __init__(self, html_file_object: Html_File, gpt_extractor: Gpt_Extractor):
        self.html_file = html_file_object.get_html()
        self.html_filename = html_file_object.get_html_filename()
        self.questions = {}
        self.answers = {}
        self.options = {}
        self.html_doc = self._set_soup_doc()

        self.gpt_extractor = gpt_extractor

    def __str__(self):
        doc_title = self.html_doc.title.text
        bucket_title = self.html_doc.h1.text
        return f"PMP Questions.\nFile Title: {doc_title}\nBucket: {bucket_title}"

    def _set_soup_doc(self):
        try:
            with open(self.html_filename, "r", encoding="utf-8") as file:
                return BeautifulSoup(file, "lxml")
        except FileNotFoundError as e:
            print("Not a local file")
            return BeautifulSoup(self.html_file, "lxml")
        
    
    def get_questions(self):
        for idx, question in enumerate(self.html_doc.find_all(class_ = "question"), 1):
            self.questions[f"{idx}"] = question.h4.text
        return self.questions

    def get_options(self):
        for idx, question in enumerate(self.html_doc.find_all(class_ = "question"), 1):
            self.options[f"{idx}"] = []
            self.options[f"{idx}"].extend([option.text for option in question.find_all("label")])
        return self.options

    def _extract_script_content(self):
        script_tags = self.html_doc.find_all("script")
        correct_answers_script = None

        for script in script_tags:
            if "const correctAnswers" in script.text:
                correct_answers_script = script.text
                break
        return correct_answers_script

    def _parse_extracted_answers(self, extracts: QuestionsAnswers):
        for idx, extract in enumerate(extracts.answer_extracts):
            question_number = extract.question_number[0]
            answer = extract.answer
            
            self.answers[f"{question_number}"] = []
            self.answers[f"{question_number}"].extend(answer)
        return self.answers
        
    def get_answers(self):
        script_content = self._extract_script_content()

        extracts = self.gpt_extractor.get_gpt_response(script_content)

        return self._parse_extracted_answers(extracts)
