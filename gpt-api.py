from dotenv import load_dotenv
from src import MyFileHandler
from src import LLMOpenAI
from src import PostProcessor, FrontProcessor
from src import OCRPipe, ExtractPipe
import argparse
import json
import os 


def main(args):
    load_dotenv()
    upstage_api_key = os.getenv('UPSTAGE_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm_openai = LLMOpenAI()
    llm_openai.set_response_guideline()

    ocr_pipe = OCRPipe(upstage_api_key)
    # ocr_result = ocr_pipe.get_ocr(args.pdf_file)
    # processed_ocr = ocr_pipe.process_ocr(ocr_result, './dataset/output/', args.pdf_file.split('/')[-1].split('.')[0] + '.txt')
    processed_ocr = ocr_pipe.load_ocr('./dataset/output', args.pdf_file.split('/')[-1].split('.')[0] + '.txt')
    # print(processed_ocr)
    
    myfile_handler = MyFileHandler()
    user_requirements = myfile_handler.open_file(os.path.join(args.data_path, args.req_file), file_type='.json')
    extract_pipe = ExtractPipe()
    extract_pipe.get_model_response(ocr_result=processed_ocr, user_requirements=user_requirements)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--data_path', type=str, default='./dataset/output')
    cli_parser.add_argument('--pdf_file', type=str, default=None)
    cli_parser.add_argument('--req_file', type=str, required=True)
    cli_args = cli_parser.parse_args()
    main(cli_args)