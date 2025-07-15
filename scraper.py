import os
from Html_File import Html_File
from Html_Parser import Html_Parser
from Gpt_Extractor import Gpt_Extractor
from typing import Dict


html_filename = "PMP_Qstn_BUCKET_1-1.html"
html_file = Html_File(html_filename)

gpt_extractor = Gpt_Extractor()
html_parser = Html_Parser(html_file, gpt_extractor)

questions: Dict = html_parser.get_questions()
answers: Dict = html_parser.get_answers()
options: Dict = html_parser.get_options()



