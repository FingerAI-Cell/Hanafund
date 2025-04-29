import fitz  # PyMuPDF
import re 

class FrontProcessor:
    '''
    ocr 작업 전, 후처리 담당 
    0. Header, Footer 제거 
    1. 조 항 호 형태로 텍스트 변환 
    '''
    def crop_pdf(self, file_name, output_path, top_crop_ratio=0.1, bottom_crop_ratio=0.08):
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
        doc.save(output_path)

    def replace_newline(self, ocr_result):
        replaced_result = [] 
        for page in ocr_result[0]:
            replaced_result.append(page.replace('\n', ''))
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
            # (1) ①~⑳ 변환 먼저
            for circled, replacement in circled_number_map.items():
                result = result.replace(circled, replacement)
            # (2) 줄 시작에 숫자. 형태를 숫자호로 변환
            result = re.sub(r'(?<!\d)(\d+)\.\s*', r'\1호 ', result)
            converted_text.append(result)
        return converted_text

class PostProcessor:
    '''
    1. 비고에서 '~ 이상인 경우 100' 같은 문구 적용 
    2. 데이터 추출 대상 구분 코드 적용 
    3. 
    '''
    def __init__(self):
        self.set_reference()

    def set_reference(self):
        '''
        business_day_targets 요구사항이 나오면 반환 포맷은 제O엽업일
        '''
        self.reference = dict()
        self.reference['한도산식'] = {'미만': '<', '이하': '≤', '초과': '>', '이상': '≥', '사이': 'between'}
        self.reference['단위구분'] = ['%', '원', '억', '백만', '만', '주', '계약', '만주', '개', '업종', '종목', '년', '월', '일', '분기', '신용등급']
        self.business_day_targets = [
            '설정대금확정일',
            '설정(결제)일',
            '설정대금결제일',
            '환매대금확정일',
            '환매대금결제일'
        ]

    def apply_reference(self, model_response, ocr_result, user_requirement):
        if user_requirement['key'] == '한도산식':
            pass
        elif user_requirement['key'] == '신용등급':
            pass
        elif user_requirement['key'] in self.buisness_day_targets:
            pass 

    def apply_remarks(self, text, remark):
        pass 