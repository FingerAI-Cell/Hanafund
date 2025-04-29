from .processors import FrontProcessor, PostProcessor
from .docs import MyFileHandler
from .models import LLMOpenAI
from .ocr import UPOCR


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

    def process_ocr(self, ocr_result):
        replaced_text = self.front_processor.replace_newline(ocr_result)
        converted_text = self.front_processor.convert_text(replaced_text)
        full_text = converted_text.join(' ')
        return full_text


class ExtractPipe:
    '''
    get user requirements, 
    '''
    pass