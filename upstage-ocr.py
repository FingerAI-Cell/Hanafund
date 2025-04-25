from dotenv import load_dotenv
import requests
import argparse
import json 
import os 

def main(args):
    load_dotenv()
    upstage_api_key = os.getenv('UPSTAGE_API_KEY')
    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {upstage_api_key}"}
    pdf_path = './dataset/ocr'
    file_list = os.listdir(pdf_path)
    pdfs = [f for f in file_list if f.endswith('.pdf')]
    print(pdfs)
    file_names = []

    for pdf in pdfs:
        contents = [] 
        files = {"document": open(os.path.join(pdf_path, pdf), "rb")}
        data = {"model": "ocr"}
        response = requests.post(url, headers=headers, files=files, data=data)
        print(response.json())
        # print(response.json()['content'])
        page_info = response.json()['pages']
        text_list = [box['text'] + '\n\n' for box in page_info]
        contents.append(text_list)

        with open(os.path.join('./dataset/outputs/ocr', pdf.split('.')[0] + '.json'), "w", encoding="utf-8") as output_file:
            json.dump(contents, output_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--filename', type=str, default=None)
    cli_args = cli_parser.parse_args()
    main(cli_args)