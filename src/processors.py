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
            # print(f'page: {page}')
            # 1. '법 제193조 \n제2항' 끊김 보정
            text = re.sub(r'(법\s*제\s*\d+\s*조)\s*\n\s*(제\s*\d+항)', r'\1 \2', text)

            # 2. 한글 단어 중간 줄바꿈 제거
            text = re.sub(r'(?<=[가-힣])\n(?=[가-힣])', '', text)

            lines = text.split('\n')
            merged = []
            for line in lines:
                # print(f'line: {line}')
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
        '''
        사용자 요구사항 리스트 
        [컴플] 
        1. 펀드그룹분류코드
        2. 주식편입최고비율
        3. 주식편입최저비율
        4. 채권편입최고비율
        5. 채권편입최저비율
        6. 한도산식
        7. 신용등급
        8. 단위구분 
        9. 최저비율
        10. 최고비율

        [컴플]
        1. 운용사코드
        2. 수탁사
        3. 위탁사펀드명
        4. 펀드종류구분
        5. 펀드영업일기준
        6. 단위형여부
        7. 공모사모구분 
        8. 펀드구조
        9. 최초설정일
        10. 상환예정일(약관)
        11. 한도액 
        12. 설정대금확정일(기준시간 이전)
        13. 설정(결제)일(기준시간 이전)
        14. 설정대금확정일(기준시간 이후)
        15. 설정대금결제일(기준시간 이후)
        16. 설정기준시간(시/분)
        17. 환매대금확정일(기준시간 이전)
        18. 환매대금결제일(기준시간 이전)
        19. 환매대금확정일(기준시간 이후)
        20. 환매대금결제일(기준시간 이후)
        21. 환매기준시간(시/분)
        22. 거래단위(좌수)
        23. 좌당단가
        24. 최초기준가 
        25. 신탁계산기간
        26. 분배방식구분
        27. 보수계산기간(월)
        28. 보수코드 
        29. 보수율_집합투자업자(bp)
        30. 보수율_판매회사(bp)
        31. 보수율_투자일임(bp)
        32. 보수율_신탁업자(bp)
        33. 보수율_일반사무관리회사(bp)
        '''
        if user_requirement['key'] == '한도산식':
            pass
        elif user_requirement['key'] == '신용등급':
            pass
        elif user_requirement['key'] in self.buisness_day_targets:
            pass 

    def apply_remarks(self, text, remark):
        pass 