from .processors import FrontProcessor, PostProcessor
from .docs import MyFileHandler
from .models import LLMOpenAI
from .ocr import UPOCR
import json
import re
import os 

class OCRPipe:
    '''
    crop pdf, get ocr result, process ocr result  
    '''
    def __init__(self, upstage_api):
        self.set_env(upstage_api)

    def set_env(self, upstage_api):
        self.myfile_handler = MyFileHandler()
        self.front_processor = FrontProcessor()
        self.upocr = UPOCR(upstage_api)
        self.upocr.set_env()

    def get_ocr(self, pdf, save_path=None, file_name=None):
        cropped_pdf = self.front_processor.crop_pdf(pdf)
        return self.upocr.get_ocr_result(cropped_pdf)

    def process_ocr(self, ocr_result, save_path=None, file_name=None):
        # print(f'ocr result: {ocr_result[0]}')
        replaced_text = self.front_processor.replace_soft_newline(ocr_result[0])
        converted_text = self.front_processor.convert_text(replaced_text)
        full_text = '\n\n'.join(converted_text)
        if save_path != None: 
            self.upocr.save_result(full_text, save_path, file_name)
        return full_text
    
    def load_ocr(self, save_path, file_name):
        return self.upocr.load_result(save_path, file_name)


class ExtractPipe:
    '''
    ocr 결과에서 사용자 요구 사항 관련 부분을 찾아 반환하는 파이프  
    '''
    def __init__(self):
        self.set_env() 

    def set_env(self):
        self.myfile_handler = MyFileHandler()
        self.post_processor = PostProcessor()
        self.openai_llm = LLMOpenAI()
        self.openai_llm.set_response_guideline()

    def extract_requirements(self, excel_file, sheet_name, row_idx):
        requirement_df = self.myfile_handler.open_file(excel_file, file_type='.xlsx', sheet_name=sheet_name, header=[0, 1, 2])
        user_requirement = self.myfile_handler.extract_row_info(requirement_df, row_idx)
        return user_requirement
    
    def get_model_response(self, ocr_result, user_requirements, save_path=None, file_name=None):
        '''
        ocr 결과와, user_requirements를 입력으로 받아, 각 조, 항, 호에 해당하는 문서를 추출하고, 해당 영역에서 정답을 찾아 반환하는 함수 
        '''
        all_records = []
        for category in user_requirements['Category']:
            for key, requirement in user_requirements['Category'][category].items():
                if key == '펀드그룹분류코드':
                    requirement['참조 Data'] = '제3조 2항 1호'
                
                ref = requirement['참조 Data'] 
                if ref is not None: 
                    ref = re.sub(r'^제(\d+)호', r'제\1조', ref).strip()
                
                jo = self.myfile_handler.extract_jo_number(ref)
                extracted_jo_text = self.myfile_handler.extract_jo(ocr_result, jo)
                extracted_text = self.post_processor.extract_reference(extracted_jo_text, ref)
                answer = requirement['입력 Data'] 
                requirement['입력 Data'] = None
                origin_requirement = requirement.copy()
                requirement['비고'] = None 
                print(f'key: {key}, req: {requirement}')
                print(f'jo: {jo}, ref: {ref}')
                print(extracted_text, end='\n\n')

                user_requirement = {
                    'requirement': key,
                    'reference': ref,
                    'remark': requirement['비고'].strip() if requirement.get('비고') else None
                }
                llm_prompt = self.openai_llm.set_prompt_template(extracted_text, user_requirement, self.post_processor.reference_code)
                # print(f'prompt: {llm_prompt}')
                llm_response = self.openai_llm.get_response(llm_prompt, role=self.openai_llm.system_role, sub_role=self.openai_llm.sub_role)
                # final_response = self.post_processor.apply_remark(llm_response, extracted_text, user_requirement)
                if llm_response.isdigit():
                    llm_response=float(llm_response)
                print(f'model response: {llm_response}, answer: {answer}', end='\n\n')
                record = {
                    'key': key,
                    'requirement': origin_requirement, 
                    'model_input': requirement,
                    'extracted_text': extracted_text if requirement['참조 Data'] is not None else "참조 Data가 Null 이기 때문에, 전체 텍스트를 참조합니다.",
                    'model_response': llm_response,
                    'answer': answer
                }
                all_records.append(record)
        if save_path != None: 
            with open(os.path.join(save_path, file_name), 'w', encoding='utf-8') as f:
                json.dump(all_records, f, ensure_ascii=False, indent=2, default=str)
            return 
        return all_records
