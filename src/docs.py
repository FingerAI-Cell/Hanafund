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
        self.set_reference()

    def set_reference(self):
        self.reference = dict()
        self.reference['펀드종류구분'] = ['투자신탁', '투자일임', '투자회사'] 
        self.reference['펀드구조'] = ['일반펀드', '모펀드', '자펀드', '클래스운용', '클래스', '클래스운용(자)']
        self.reference['펀드영업일기준'] = ['거래소 영업일', '판매사 영업일'] 
        self.reference['공모사모구분'] = ['공모/단독', '공모/일반', '사모/단독', '사모/일반']
        self.reference['분배방식구분'] = ['전액분배', '평가이익유보', '매매평가이익유보']
    
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

    def find_referenced_clauses(text):
        """
        텍스트에서 '제XX조제YY항을 준용한다 / 따른다 / 참조한다' 등의 참조 조항을 찾아냄.
        """
        pattern = r"제\s*(\d+)\s*조(?:\s*제\s*(\d+)\s*항)?을\s*(준용|따른|참조)한다"
        matches = re.findall(pattern, text)

        referenced = set()
        for jo_str, hang_str, _ in matches:
            jo = int(jo_str)
            hang = int(hang_str) if hang_str else None
            referenced.add((jo, hang))  # (조, 항)
        return referenced

    def parse_jo_hang_ho(self, line):
        if line == None: 
            return None 
        line = line.strip()
        jo_match = re.search(r'제\s*(\d+)\s*조', line)
        jo = int(jo_match.group(1)) if jo_match else None

        hang_matches = re.findall(r'(\d+)\s*항', line)
        hangs = [int(h) for h in hang_matches] if hang_matches else []

        ho_matches = re.findall(r'(\d+)\s*호', line)
        hos = [int(h) for h in ho_matches] if ho_matches else []
        result = defaultdict(dict)
        if not hangs:
            result[jo] = None
        else:
            for hang in hangs:
                result[jo][hang] = hos if hos else None
        return dict(result)

    def extract_jo(self, text, jo):
        pattern = rf'(제\s*{jo}\s*조.*?)(?=제\s*{jo+1}\s*조|제\s*\d+\s*장)'
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else None

    def extract_jo_hang(self, text, jo, hang):
        jo_block = self.extract_jo(text, jo)
        if not jo_block:
            return None
        pattern = rf'{hang}\s*항(.*?)(?=\d+\s*항|제\s*\d+\s*조|제\s*\d+\s*장)'
        match = re.search(pattern, jo_block, re.DOTALL)
        return match.group(1).strip() if match else None

    def extract_jo_hang_ho(self, text, jo=1, hang=1, ho=1):
        jo_pattern = rf'(제\s*{jo}\s*조.*?)(?=제\s*{jo+1}\s*조|제\s*\d+\s*장)'
        jo_match = re.search(jo_pattern, text, re.DOTALL)
        if not jo_match:
            return None
        jo_block = jo_match.group(1)

        hang_pattern = rf'{hang}항(.*?)(?=\d+항|제\s*\d+\s*조|제\s*\d+\s*장)'
        hang_match = re.search(hang_pattern, jo_block, re.DOTALL)
        if not hang_match:
            return None
        hang_block = hang_match.group(1)

        ho_pattern = rf'{ho}호(.*?)(?=\d+호|제\s*\d+\s*조|제\s*\d+\s*장)'
        ho_match = re.search(ho_pattern, hang_block, re.DOTALL)
        if not ho_match:
            return None
        return ho_match.group(0).strip()

    def extract_multiple(self, text, target_dict):
        extracted = []
        if target_dict == None:
            print(f'참고 Data가 없어, 전체 text를 반환합니다.')
            return text 
        for jo, hang_map in target_dict.items():
            if hang_map is None:
                content = self.extract_jo(text, jo)
                if content:
                    extracted.append((jo, None, None, content))
            else:
                for hang, hos in hang_map.items():
                    if hos is None:
                        content = self.extract_jo_hang(text, jo, hang)
                        if content:
                            extracted.append((jo, hang, None, content))
                    else:
                        for ho in hos:
                            content = self.extract_jo_hang_ho(text, jo, hang, ho)
                            if content:
                                extracted.append((jo, hang, ho, content))
        return extracted