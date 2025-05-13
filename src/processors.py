from .docs import MyFileHandler
import tempfile
import fitz  # PyMuPDF
import re 

class FrontProcessor:
    '''
    ocr 작업 전, 후처리 담당 
    0. Header, Footer 제거 
    1. 조 항 호 형태로 텍스트 변환 
    '''
    def crop_pdf(self, file_name, output_path=None, top_crop_ratio=0.1, bottom_crop_ratio=0.08):
        doc = fitz.open(file_name)
        for page in doc:
            rect = page.rect
            top_crop = rect.height * top_crop_ratio
            bottom_crop = rect.height * bottom_crop_ratio
            new_rect = fitz.Rect(
                rect.x0,
                rect.y0 + top_crop,
                rect.x1,
                rect.y1 - bottom_crop
            )
            page.set_cropbox(new_rect)
        if output_path != None:
            doc.save(output_path)
            return 
        else: 
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            doc.save(tmp_file.name)
            tmp_file.close()
            return tmp_file.name

    def replace_soft_newline(self, ocr_result):
        """
        OCR 결과에서 줄 중간의 불필요한 줄바꿈만 제거하고,
        '제XX조(...)' 구조 구분을 위한 줄바꿈은 유지함.
        """
        replaced_result = []
        for page in ocr_result:
            text = page
            text = re.sub(r'(법\s*제\s*\d+\s*조)\s*\n\s*(제\s*\d+항)', r'\1 \2', text)
            text = re.sub(r'(?<=[가-힣])\n(?=[가-힣])', '', text)

            lines = text.split('\n')
            merged = []
            for line in lines:
                stripped = line.strip()
                if re.search(r'제\s*\d+\s*조\s*\(', stripped):
                    merged.append('\n' + stripped)
                else:
                    merged.append(' ' + stripped)
            replaced_result.append(''.join(merged).strip())
        return replaced_result

    def convert_text(self, ocr_result):
        '''
        ①~⑳ 변환 + 줄 시작 숫자. -> 숫자호 변환
        '''
        circled_number_map = {
            '①': '1항 ', '②': '2항 ', '③': '3항 ', '④': '4항 ', '⑤': '5항 ',
            '⑥': '6항 ', '⑦': '7항 ', '⑧': '8항 ', '⑨': '9항 ', '⑩': '10항 ',
            '⑪': '11항 ', '⑫': '12항 ', '⑬': '13항 ', '⑭': '14항 ', '⑮': '15항 ',
            '⑯': '16항 ', '⑰': '17항 ', '⑱': '18항 ', '⑲': '19항 ', '⑳': '20항 ',
        }
        converted_text = [] 
        for result in ocr_result: 
            for circled, replacement in circled_number_map.items():
                result = result.replace(circled, replacement)
            result = re.sub(r'(?<!\d)(\d+)\.\s+(?=\S)', r'\1호 ', result)
            converted_text.append(result)
        return converted_text
    

class PostProcessor:
    '''
    1. 비고에서 '~ 이상인 경우 100' 같은 문구 적용 
    2. 데이터 추출 대상 구분 코드 적용 
    3. 
    '''
    def __init__(self):
        self.set_code()
        self.set_env()
        
    def set_env(self):
        self.myfile_handler = MyFileHandler()

    def set_code(self):
        '''
        business_day_targets 요구사항이 나오면 반환 포맷은 제O엽업일
        '''
        self.reference_code = dict()
        self.reference_code['펀드그룹분류코드'] = ['투자신탁', '투자일임', '투자회사']
        self.reference_code['한도산식'] = {'미만': '<', '이하': '≤', '초과': '>', '이상': '≥', '사이': 'between'}
        self.reference_code['단위구분'] = ['%', '원', '억', '백만', '만', '주', '계약', '만주', '개', '업종', '종목', '년', '월', '일', '분기', '신용등급', '신용평가등급']
        self.reference_code['펀드구조'] = ['일반펀드', '모펀드', '자펀드', '클래스운용', '클래스', '클래스운용(자)']
        self.reference_code['펀드영업일기준'] = ['거래소 영업일', '판매사 영업일'] 
        self.reference_code['공모사모구분'] = ['공모/단독', '공모/일반', '사모/단독', '사모/일반']
        self.reference_code['분배방식구분'] = ['전액분배', '평가이익유보', '매매평가이익유보']
        self.business_day_targets = [
            '설정대금확정일',
            '설정(결제)일',
            '설정대금결제일',
            '환매대금확정일',
            '환매대금결제일'
        ]
    
    def extract_reference(self, ocr_result, reference):
        '''
        주어진 텍스트에서, reference에 해당하는 항, 호를 추출해서 반환하는 함수
        '''
        if reference is None:
            return ocr_result 

        hang, ho = self.myfile_handler.extract_hang_ho_number(reference)
        if hang is not None and ho is not None:    # 항, 호 모두 존재하는 경우 '항 추출 -> 해당 항에서 호 추출' 
            hang_text, flag = self.myfile_handler.extract_hang(ocr_result, hang) 
            # print(f'hang text: {hang_text}', end='\n\n')
            if flag == False: 
                text = ocr_result 
            else: 
                text = self.myfile_handler.extract_ho(hang_text, ho)
        elif hang is not None and ho is None: 
            hang_text, flag = self.myfile_handler.extract_hang(ocr_result, hang)
            if flag == False: 
                text = ocr_result 
            else:
                text = hang_text  
        elif hang is None and ho is not None: 
            text = self.myfile_handler.extract_ho(ocr_result, ho)
        else: 
            text = ocr_result
        return text

    def adjust_limit_by_remark(self, model_response, text, remark):
        '''
        최저, 최고인 경우 후처리 진행하는 함수
        reference 참고해서 해당 text 추출 
        이후 비고와 비교 
        '''
        if remark is None:
            return model_response
        
        match = re.search(r'이상인 경우\s*(\d+)', remark)
        if match:
            return int(match.group(1))

        match = re.search(r'이하인 경우\s*(\d+)', remark)
        if match:
            return int(match.group(1))

        if '이상인 경우' in remark:
            match = re.search(r'(\d+)\s*%', text)
            if match:
                return int(match.group(1))

        if '이하인 경우' in remark:
            match = re.search(r'(\d+)\s*%', text)
            if match:
                return int(match.group(1))    

    def extract_limit_operator(self, text):
        for keyword, symbol in self.reference_code['한도산식'].items():
            if keyword in text:
                return symbol
        # 없으면 명시적 한도 조건 없음
        return None  

    def apply_remark(self, model_response, ocr_result, user_requirement):
        '''
        user_requirement: {
            'requirement: "", 
            "reference": "", 
            "remark": ""
        }
        컴플: 펀드그룹분류코드, 최고-최저비율, 한도산식, 신용등급
        '''
        # print(f'original text: {ocr_result}', end='\n\n')
        text = self.extract_reference(ocr_result, user_requirement['reference'])
        if user_requirement['reference'] is not None:
            print(f"extracted_text: {text}, reference: {user_requirement['reference']}, remark: {user_requirement['remark']}")

        if '최저비율' in user_requirement['requirement'] or '최고비율' in user_requirement['requirement']:
            return self.adjust_limit_by_remark(model_response, text, user_requirement['remark'])
        # elif user_requirement['requirement'] == '한도산식':
        #    return self.extract_limit_operator(text)
        elif user_requirement.keys() == '단위구분':
            pass 
        elif user_requirement.keys() in self.business_day_targets:
            pass 
        else:
            return model_response