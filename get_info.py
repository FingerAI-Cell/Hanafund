from collections import defaultdict
import pandas as pd
import argparse 
import json 
import os 


def main(args):
    excel_file = os.path.join(args.data_path, args.file_name)
    accounting_df = pd.read_excel(excel_file, sheet_name='회계', header=[0, 1, 2])
    compliance_df = pd.read_excel(excel_file, sheet_name='컴플', header=[0, 1, 2])
    
    file_num = len(accounting_df['약관 Sample']['구분'].dropna())
    file_requests = dict()
    for idx in range(file_num):
        for col in accounting_df.columns:
            print(f'Columns: {col}')
            # print(accounting_df[col])
            row_info = accounting_df.loc[idx, col]
            print(idx, row_info)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--data_path', type=str, default='./dataset/excel')
    cli_parser.add_argument('--file_name', type=str, required=True)
    cli_args = cli_parser.parse_args()
    main(cli_args)