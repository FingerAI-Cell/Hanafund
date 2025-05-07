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
    
    def extract_hang(self, text, hang_number):
        """
        텍스트에서 특정 항(hang_number)에 해당하는 범위만 추출
        예: 1항 → '1항 ... (2항 전까지)'
        """
        try:
            hang_number = int(hang_number)
        except (ValueError, TypeError):
            return None  # or raise
        flag = True  
        start_pattern = re.compile(rf'(?:^|\n|\s){hang_number}\s*항')
        end_pattern = re.compile(rf'(?:^|\n|\s){hang_number + 1}\s*항')
        match_start = start_pattern.search(text)
        if not match_start:
            flag = False
            return text, flag 
        start = match_start.start()
        match_end = end_pattern.search(text, pos=start)
        end = match_end.start() if match_end else len(text)
        return text[start:end].strip(), flag 
    
    def extract_ho(self, text, ho_number):
        try:
            ho_number = int(ho_number)
        except (ValueError, TypeError):
            return None

        start_pattern = re.compile(rf'(?:^|\n|\s){ho_number}\s*호')
        end_pattern = re.compile(rf'(?:^|\n|\s){ho_number + 1}\s*호')
        start_match = start_pattern.search(text)
        if not start_match:
            return None
        start = start_match.start()
        end_match = end_pattern.search(text, pos=start)
        end = end_match.start() if end_match else len(text)
        return text[start:end].strip()
    
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