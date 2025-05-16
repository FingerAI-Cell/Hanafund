import requests

# 테스트할 서버 주소
url = 'http://127.0.0.1:8081/run'

# 보낼 JSON 데이터
data = {
    "file_name": "하나펀드서비스_신탁계약서.xlsx",
    "sheet_name": "회계",
    "row_idx": 2
}

data2 = {
    "pdf_file_name": "01.cropped_신탁계약서_트러스톤매크로채권전략증권투자신탁[채권].pdf",
    "excel_file_name": "하나펀드서비스_신탁계약서.xlsx",
    "sheet_name": "회계", 
    "row_idx": 0
}

response = requests.post(url, json=data2)

print("Status Code:", response.status_code)
try:
    print("Response (JSON):", response.json())
except Exception as e:
    print("JSON Decode Error:", e)
    print("Raw Response Text:", response.text)
