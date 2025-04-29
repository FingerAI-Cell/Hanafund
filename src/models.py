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
        사용자 요청에 비고가 적혀있을건데, 값을 찾을 때 비고를 참고하기도 하지만, 값을 찾고나서 비고를 참고해야 할 때가 있어. 
        값을 반환하기 전에, 반드시 비고를 추가적으로 확인하고, 변경이 필요한 경우 변경해서 반홚재줘. 
        그리고, 특정 요청값에 대해 정의한 참고 자료를 줄건데, 이 값이 들어오는 경우에는 비고 말고, 참고 자료에 나와있는 값을 반환하면 돼. 
        이렇게 얻은 값과, 해당 값을 찾은 위치 정보(몇 조 명 항)만 반환해주고, 다른 말은 하지마. 
        """
        self.sub_role = """
        '운용사코드'를 찾아서 반환하는 샘플 예제와, '위탁사펀드명'을 찾아서 반환하는 샘플 예제야. 
        ==============================
        "운용사코드": {
            "참조 Data": "",
            "입력 Data": "",
            "비고": "운용사명 앞에 \"집합투자업자인…\""
        },
        ==============================
        반환값: 트러스톤자산운용, 제1조 
        ==============================
        "위탁사펀드명": {
            "참조 Data": "",
            "입력 Data": "",
            "비고": "\"투자신탁의 명칭은…\""
        },
        ==============================
        반환값: 트러스톤매크로채권전략증권투자신탁[채권], 제 3조 
        """

    def set_prompt_template(self, ocr_result, user_requirements, reference):
        self.data_prompt_template = """
        OCR 결과: {ocr_result}
        사용자 요구사항: {user_requirements}
        참고표: {reference} 
        """
        return self.data_prompt_template.format(ocr_result=ocr_result, user_requirements=user_requirements, reference=reference)
                   
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