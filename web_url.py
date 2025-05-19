from flask import Flask, send_file, request, jsonify, Response
from src import MyFileHandler, FrontProcessor, PostProcessor
from src import OCRPipe, ExtractPipe
from src import LLMOpenAI
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
file_path = './dataset'


@app.route('/ocr', methods=['POST'])
def get_ocr():
    '''
    input: file_name 
    output: ocr result  
    '''
    try:
        data = request.json
        pdf_file = data['pdf_file_name']
        
        ocr_result = ocr_pipe.get_ocr(os.path.join(file_path, pdf_file))
        processed_ocr = ocr_pipe.process_ocr(ocr_result)
        return jsonify({"status": "ocr completed"}), 200 
    except Exception as e: 
        return jsonify({"error": str(e)}), 400 

@app.route('/requirement', methods=['POST'])
def get_requirement():
    '''
    input: file_name, sheet name, row idx 
    output: user requirement 
    '''
    try:
        data = request.json
        file_name = data['file_name']
        excel_sheet = data['sheet_name'] 
        row_idx = data['row_idx'] 
        user_requirements = extract_pipe.extract_requirements(os.path.join(file_path, 'requirements', file_name), excel_sheet, row_idx)
        return jsonify({"status": "requirement extracted"}), 200 
    except Exception as e: 
        return jsonify({"error": str(e)}), 400 

@app.route('/model_reponse', methods=['POST'])
def get_model_response():
    '''
    input: ocr result (.json), user requirement (.json)
    output: model response (.json)
    '''
    try: 
        data = request.json  # JSON 본문을 받음
        print(data)
        ocr_file = data['ocr_result']
        req_file = data['user_requirement']
        print(os.path.join(file_path, 'ocr'))
        processed_ocr = ocr_pipe.load_ocr(os.path.join(file_path, 'ocr'), ocr_file)
        # print(processed_ocr)
        user_requirements = extract_pipe.load_requirements(os.path.join(file_path, 'requirements'), req_file)
        model_response = extract_pipe.get_model_response(ocr_result=processed_ocr, user_requirements=user_requirements)
        return jsonify({"status": "model response received"}), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 400 

@app.route('/run', methods=['POST'])
def run_process():
    try:
        data = request.json
        file_name = data['pdf_file_name']
        excel_file_name = data['excel_file_name'] 
        excel_sheet = data['sheet_name']
        row_idx = data['row_idx'] 

        # ocr_result = ocr_pipe.get_ocr(os.path.join(file_path, 'ocr', file_name))
        # processed_ocr = ocr_pipe.process_ocr(ocr_result)
        # print(f'ocr load: {file_name}')
        processed_ocr = ocr_pipe.load_ocr(os.path.join(file_path, 'ocr'), file_name)
        
        user_requirements = extract_pipe.extract_requirements(os.path.join(file_path, 'requirements', excel_file_name), excel_sheet, row_idx)
        model_response = extract_pipe.get_model_response(ocr_result=processed_ocr, user_requirements=user_requirements)
        return jsonify({"status": "process succeed", "model_response": model_response}), 200 
    except Exception as e: 
        return jsonify({"error": str(e)}), 404 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)