from openai import OpenAI
import torch

class LLMModel():
    def __init__(self):
        self.set_generation_config()

    def set_gpu(self, model):
        self.device = torch.device("cuda") if torch.cuda.is_available() else "cpu"    
        model.to(self.device)
    
    def set_generation_config(self, max_tokens=500, temperature=0):
        self.gen_config = {
            "max_tokens": max_tokens,
            "temperature": temperature
        }

class LLMOpenAI(LLMModel):
    def __init__(self):
        super().__init__()
        self.client = OpenAI()

    def set_response_guideline(self):
        self.system_role = """
        너는 주어진 OCR 결과를 바탕으로, 입력받은 사용자 요청에서 '입력 Data' 부분 값을 구해서 반환하는 역할을 수행하는 전문가야. 
        사용자 요청에 비고가 적혀 있다면, 이들을 참고해서 값을 찾아줘. 찾은 값만 반환하고, 다른 말은 하지마.
        그리고 사용자 요청 항목이 참고 자료에 존재한다면, 참고 자료에 나와있는 값을 반환해줘. 
        """
        self.sub_role = """
        다음은 '운용사코드'를 찾아서 반환하는 샘플 예제와, '위탁사펀드명'을 찾아서 반환하는 샘플 예제야. 
        ==============================
        "운용사코드": {
            "참조 Data": "제1조",
            "입력 Data": None,
            "비고": "운용사명 앞에 \"집합투자업자인…\""
        },
        ==============================
        반환값: 트러스톤자산운용 
        ==============================
        "위탁사펀드명": {
            "참조 Data": "제3조",
            "입력 Data": None,
            "비고": "\"투자신탁의 명칭은…\""
        },
        ==============================
        반환값: 트러스톤매크로채권전략증권투자신탁[채권] 
        """

    def set_prompt_template(self, ocr_result, user_requirements):
        self.data_prompt_template = """
        OCR 결과: {ocr_result}
        사용자 요구사항: {user_requirements}
        """
        return self.data_prompt_template.format(ocr_result=ocr_result, user_requirements=user_requirements)
                   
    def get_response(self, query, role="", sub_role="", model='gpt-4o'):
        try:
            sub_role = sub_role
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "system", "content": sub_role},
                    {"role": "user", "content": query},
                ],
                max_tokens=self.gen_config['max_tokens'],
                temperature=self.gen_config['temperature'],
            )
        except Exception as e:
            return f"Error: {str(e)}"
        return response.choices[0].message.content