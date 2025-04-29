from src import FrontProcessor
import os 

front_processor = FrontProcessor()
pdf_path = './dataset/ocr'
file_list = os.listdir(pdf_path)
pdfs = [f for f in file_list if f.endswith('.pdf')]
print(pdfs)

for pdf in pdfs:
    save_name = 'cropped_' + pdf.split('.')[-2] + '.pdf'
    front_processor.crop_pdf(os.path.join(pdf_path, pdf), save_name)