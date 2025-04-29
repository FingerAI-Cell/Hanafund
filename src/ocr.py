from dotenv import load_dotenv
import requests
import json
import os 


class OCRTask:
    def __init__(self, api_key):
        self.api_key = api_key 
    

class UPOCR(OCRTask):
    def __init__(self, api_key):
        super().__init__(api_key)
    
    def set_env(self):
        self.url = "https://api.upstage.ai/v1/document-digitization"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def get_ocr_result(self, pdf_file):
        contents = []
        files = {"document": open(pdf_file, "rb")}
        data = {"model": "ocr"}
        response = requests.post(self.url, headers=self.headers, files=files, data=data)

        page_info = response.json()['pages']
        text_list = [box['text'] + '\n\n' for box in page_info]
        contents.append(text_list)
        return contents 
    
    def save_result(self, ocr_result, save_path, file_name):
        with open(os.path.join(save_path, file_name), "w", encoding="utf-8") as output_file:
            json.dump(ocr_result, output_file, ensure_ascii=False, indent=4)