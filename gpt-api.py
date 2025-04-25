from dotenv import load_dotenv
from src import LLMOpenAI
import argparse
import json
import os 


def main(args):
    with open(os.path.join(args.config_path, args.llm_config)) as f:
        llm_config = json.load(f)
    
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm_openai = LLMOpenAI(llm_config)
    llm_openai.set_generation_config()
    llm_openai.set_response_guideline()

    llm_prompt = llm_openai.set_prompt_template(meta_data, img_description)
    llm_response = llm_openai.get_response(llm_prompt, role=llm_openai.system_role, sub_role=llm_openai.sub_role)
    print(llm_response)


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--config_path', type=str, default='./config/')
    cli_parser.add_argument('--llm_config', type=str, default='llm_config.json')
    cli_parser.add_argument('--test_type', type=str, default='total')
    cli_parser.add_argument('--file_name', type=str, default=None)
    cli_args = cli_parser.parse_args()
    main(cli_args)