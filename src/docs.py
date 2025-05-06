from collections import defaultdict
import pandas as pd
import datetime
import json 
import os 
import re

class FileHandler:
    def open_file(self, file_name, file_type, header=None, sheet_name=None):
        '''
        header: [0, 1, 2]  -> 0, 1, 2행이 해당 파일의 상단 계층임을 알려줌 
        '''
        if file_type == '.xlsx':
            file = pd.read_excel(file_name, sheet_name=sheet_name, header=header)
            return file 
        elif file_type == '.json':
            with open(file_name) as f:
                file = json.load(f)
            return file

    def convert_datetime(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def save_file(self, data, save_path, file_name):
        with open(os.path.join(save_path, file_name), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=self.convert_datetime)


class MyFileHandler(FileHandler):
    def __init__(self):
        super().__init__()

    def extract_jo_number(self, text):
        '''
        간혹 제 25조 1항 -> 제 25호 1항 같이 들어오는 경우 존재. 
        '''
        if text == None: 
            return None
        text = re.sub(r'제\s*(\d+)\s*호(?=\s*\d+\s*항)', r'제 \1조', text)
        match = re.search(r'제\s*(\d+)\s*조', text)
        return int(match.group(1)) if match else None
    
    def extract_hang_ho_number(self, text):
        """
        '제16조 1항 2호' → jo=16, hang=1, ho=2 로 분해
        """
        hang_match = re.search(r'(\d+)항', text)
        ho_match = re.search(r'(\d+)호', text)

        hang = hang_match.group(1) if hang_match else None
        ho = ho_match.group(1) if ho_match else None
        return hang, ho

    def extract_jo(self, text, jo_number):
        """
        '제XX조(조문제목)' 형태로 시작하는 조문 내용만 추출 (정확한 조문 시작만)
        """
        if jo_number is None:
            return text

        pattern = rf'(?:^|\n)제\s*{jo_number}\s*조\s*\(.*?\).*?(?=\n제\s*\d+\s*조\s*\(|\n제\s*\d+\s*장|$)'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(0).strip() if match else None
    
    def extract_hang(self, ocr_text, hang_number):
        if hang_number is None:
            return ocr_text 
        
        text_list = [text.strip() for text in ocr_text.split('.')]
        result = []
        capture = False
        pattern_start = re.compile(rf'^{hang_number}항')
        for text in text_list:
            if pattern_start.match(text):  # 해당 항 시작
                result.append(text)
                capture = True
            elif re.match(r'^\d+항', text):  # 다음 항 시작 → 종료
                if capture:
                    break
            elif capture:  # 항 내부 계속 수집
                result.append(text)
        return '. '.join(result) if result else None
    
    def extract_ho(self, ocr_text, ho_number):
        if ho_number is None: 
            return ocr_text 
        
        text_list = [text.strip() for text in ocr_text.split('.')] 
        result = []
        capture = False
        pattern_start = re.compile(rf'^{ho_number}호')

        for text in text_list:
            if pattern_start.match(text):
                result.append(text)
                capture = True
            elif re.match(r'^\d+호', text):  # 다음 호가 시작되면 중단
                if capture:
                    break
            elif capture:   # 1호 관련 설명이 여러 줄일 경우 계속 붙임
                result.append(text)
        return ''.join(result)
    
    def extract_row_info(self, data, idx):
        '''
        excel file에서, 요구사항 집합 추출
        '''
        result = {
            "Filename": idx,
            "Category": {}
        }
        grouped_by_category_mid = defaultdict(lambda: defaultdict(list))
        for col in data.columns:
            if len(col) == 3:
                category, mid, sub = col
                if category == '약관 Sample' and mid == '펀드명':   # file name 정보 획득 
                    file_name = data.loc[idx, col]
                    continue 
                elif category == '약관 Sample':
                    continue
                grouped_by_category_mid[category][mid].append(col)

        for category, mids in grouped_by_category_mid.items():
            result['Category'][category] = {}
            for mid, cols in mids.items():
                value_dict = {}
                for col in cols:
                    _, _, sub = col
                    value = data.loc[idx, col]
                    value_dict[sub] = value if pd.notna(value) else None
                result['Category'][category][mid] = value_dict
        result['Filename'] = file_name
        return result     