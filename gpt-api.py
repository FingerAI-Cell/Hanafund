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
    processed_ocr = ocr_pipe.load_ocr('./dataset/ocr', args.pdf_file.split('/')[-1].split('.')[0] + '.txt')
    # print(processed_ocr)
    
    # myfile_handler = MyFileHandler()
    # user_requirements = myfile_handler.open_file(os.path.join(args.data_path, args.req_file), file_type='.json')
    extract_pipe = ExtractPipe()
    excel_file_path = './dataset/requirements/하나펀드서비스_신탁계약서.xlsx'
    user_requirements = extract_pipe.extract_requirements(excel_file_path, args.sheet_name, args.row_idx)
    file_name = args.pdf_file.replace('.', '_').split('/')[-1].split('_')[0] + '_' + args.pdf_file.split('.')[-2] + '.json'
    extract_pipe.get_model_response(ocr_result=processed_ocr, user_requirements=user_requirements, 
                                    save_path='./dataset/output/model_response', file_name=file_name)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--data_path', type=str, default='./dataset/output')
    cli_parser.add_argument('--sheet_name', type=str, default='컴플', help='컴플, 회계')
    cli_parser.add_argument('--row_idx', type=int, required=True, help='0, 1, 2')
    cli_parser.add_argument('--pdf_file', type=str, default=None)
    # cli_parser.add_argument('--req_file', type=str, required=True)
    cli_args = cli_parser.parse_args()
    main(cli_args)