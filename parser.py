from typing import Optional

from openai import OpenAI
import json
import logging
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

client = OpenAI()

MAX_PARSING_ATTEMPTS = 5


def llm(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        temperature=1,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


def parse(json_schema: dict, text: str, additional_instructions: Optional[str] = None) -> dict:
    prompt = f"""
    You will be given a text input. You need to parse it, 
    and output the result as a JSON abiding by the following JSONSchema spec:
    ```json
    {json.dumps(json_schema, indent=True)}
    ```
    Do not output the JSONSchema, only the parsed JSON. 
    {additional_instructions}
    """
    messages = [
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": text
        },
    ]

    attempt = 0
    while attempt <= MAX_PARSING_ATTEMPTS:
        logger.info(f"Parsing attempt # {attempt}...")

        parsing_attempt = llm(messages)

        parsed = json.loads(parsing_attempt)

        try:
            validate(parsed, json_schema)
        except ValidationError as e:
            error_msg = f"The current output doesn't match the expected schema, error: {e.message} in {e.json_path}. Please fix."
            logger.info(error_msg)
            messages.append({
                "role": "user",
                "content": error_msg
            })
        else:
            logger.info("Parsing succeeded!")
            return parsed

        attempt += 1


if __name__ == '__main__':
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('schema', help='Path to JSONSchema spec')
    parser.add_argument('text', help='Text you would like to parse')
    parser.add_argument('--additional_instructions', help='Additional parsing isntructions')
    args = parser.parse_args()

    with open(args.schema) as f:
        json_schema = json.load(f)

    parsed_recipe = parse(json_schema, args.text, args.additional_instructions)

    print(json.dumps(parsed_recipe, indent=True))