from collections import defaultdict
from src import MyFileHandler
import pandas as pd
import argparse 
import json 
import os 


def main(args):
    myfile_handler = MyFileHandler()
    excel_file = os.path.join(args.data_path, args.file_name)

    accounting_df = myfile_handler.open_file(excel_file, file_type='.xlsx', sheet_name=args.sheet_name, header=[0, 1, 2])
    # file_num = len(accounting_df['약관 Sample']['구분'].dropna())
    file_requests = dict()
    row_idx = 2
    row_info = myfile_handler.extract_row_info(accounting_df, row_idx)
    print(row_info)
    file_name = args.file_name.split('.')[0] + '_' + args.sheet_name + '_' + str(row_idx) + '.json'
    myfile_handler.save_file(row_info, './dataset/output/', file_name)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--data_path', type=str, default='./dataset/excel')
    cli_parser.add_argument('--file_name', type=str, required=True)
    cli_parser.add_argument('--sheet_name', type=str, required=True)
    cli_args = cli_parser.parse_args()
    main(cli_args)