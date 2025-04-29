from collections import defaultdict
import pandas as pd
import datetime
import json 
import os 

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

    def find_region(self, data, input_data):
        return text

    def set_reference(self):
        self.reference = dict()
        self.reference['한도산식'] = ['미만(<)', '이하(≤)', '초과(>)', '이상(≥)', '사이(between)']
        self.reference['단위구분'] = ['%', '원', '억', '백만', '만', '주', '계약', '만주', '개', '업종', '종목', '년', '월', '일', '분기', '신용등급']
        self.reference['펀드종류구분'] = ['투자신탁', '투자일임', '투자회사'] 
        self.reference['펀드구조'] = ['일반펀드', '모펀드', '자펀드', '클래스운용', '클래스', '클래스운용(자)']
        self.reference['펀드영업일기준'] = ['거래소 영업일', '판매사 영업일'] 
        self.reference['공모사모구분'] = ['공모/단독', '공모/일반', '사모/단독', '사모/일반']
        self.reference['분배방식구분'] = ['전액분배', '평가이익유보', '매매평가이익유보']
        self.reference['설정대금확정일'] = '반환 형식: 제1영업일 ~ 제99영업일'
        self.reference['설정(결제)일'] = '반환 형식: 제1영업일 ~ 제99영업일'
        self.reference['설정대금결제일'] = '반환 형식: 제1영업일 ~ 제99영업일'
        self.reference['환매대금확정일'] = '반환 형식: 제1영업일 ~ 제99영업일'
        self.reference['환매대금결제일'] = '반환 형식: 제1영업일 ~ 제99영업일'

    def extract_row_info(self, data, idx):
        result = {
            "Filename": idx,
            "Category": {}
        }
        grouped_by_category_mid = defaultdict(lambda: defaultdict(list))
        for col in data.columns:
            if len(col) == 3:
                category, mid, sub = col
                if category == '약관 Sample' and mid == '펀드명':
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