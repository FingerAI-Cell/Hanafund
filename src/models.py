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
        너는 주어진 OCR 결과를 바탕으로, 입력받은 사용자 요청에서 key에 해당하는 값을 찾아 반환하는 역할을 수행하는 전문가야. 
        사용자 요청은 {key:{'참조 Data', '입력 Data', '비고'}} 형태로 되어 있어.  
        참조 Data는 key 값에 대한 답이 나와있는 위치를 의미하고, 비고는 값을 찾거나, 반환할 때 참고해야 할 내용이 적혀 있어. 
        참조 Data가 None 인 경우에는 주어진 OCR 결과를 너가 살펴보고 key에 대한 적절한 값을 찾아 반환해줘.  
        이 둘을 참고해서 값을 반환해주는데, 값만 반환하지 말고 다른 말은 하지마. 특히, 텍스트 전체를 그대로 반환하는건 절대 안돼. 
        """
        self.sub_role = """
        * 좌당단가 = 1좌의 가격이 얼마인가 ?    e.g) 1좌를 3원으로 하여 ~  -> 좌당단가 = 3

        다음은 '운용사코드' 및 '위탁사펀드명'를 찾기 위한 사용자 요청 샘플이야.  
        ==============================
        {
            "운용사코드": {
                "참조 Data": "제1조",
                "입력 Data": None,
                "비고": "운용사명 앞에 \"집합투자업자인…\""
            }
        }
        ==============================
        반환값: 트러스톤자산운용 
        ==============================
        {
            "위탁사펀드명": {
                "참조 Data": "제3조",
                "입력 Data": None,
                "비고": "\"투자신탁의 명칭은…\""
            }
        }
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