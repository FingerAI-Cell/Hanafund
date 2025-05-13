from flask import Flask, send_file, request, jsonify, Response
from src import MyFileHandler, FrontProcessor, PostProcessor
from src import OCRPipe, ExtractPipe
from dotenv import load_dotenv
import requests
import time
import logging
import tempfile
import json
import os

app = Flask(__name__)    

logger = logging.getLogger('stt_logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('stt-result.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

load_dotenv()
upstage_api_key = os.getenv('UPSTAGE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
llm_openai = LLMOpenAI()
llm_openai.set_response_guideline()

ocr_pipe = OCRPipe(upstage_api_key)
extract_pipe = ExtractPipe()

@app.route('/ocr/', methods=['GET'])
def get_ocr():
    data = request.get_json()
    pdf_file = data['pdf_file_name']
    file_path = './dataset/ocr/'
    