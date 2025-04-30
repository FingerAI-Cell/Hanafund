from .processors import FrontProcessor, PostProcessor
from .docs import MyFileHandler
from .models import LLMOpenAI
from .ocr import UPOCR
import re

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
        replaced_text = self.front_processor.replace_soft_newline(ocr_result[0])
        converted_text = self.front_processor.convert_text(replaced_text)
        full_text = ''.join(converted_text)
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
    
    def get_model_response(self, ocr_result, user_requirements):
        '''
        ocr 결과와, user_requirements를 입력으로 받아, 각 조, 항, 호에 해당하는 문서를 추출하고, 해당 영역에서 정답을 찾아 반환하는 함수 
        '''
        for category in user_requirements['Category']:
            for key, requirement in user_requirements['Category'][category].items():
                ref = requirement['참조 Data'] 
                jo = self.myfile_handler.extract_jo_number(ref)
                extracted_text = self.myfile_handler.extract_jo(ocr_result, jo)
    
                answer = requirement['입력 Data'] 
                requirement['입력 Data'] = None
                print(f'key: {key}, req: {requirement}')
                print(f'jo: {jo}, ref: {ref}')
                print(extracted_text)

                user_requirement = {key: requirement}
                llm_prompt = self.openai_llm.set_prompt_template(ocr_result, user_requirement)
                llm_response = self.openai_llm.get_response(llm_prompt, role=self.openai_llm.system_role, sub_role=self.openai_llm.sub_role)
                print(f'model response: {llm_response}, answer: {answer}', end='\n\n')