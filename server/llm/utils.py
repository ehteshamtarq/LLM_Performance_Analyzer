import os
import csv
import re
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# from openai import OpenAI

load_dotenv()

async def groq_api_call(prompt_text):

    client = Groq(
    api_key = os.getenv('GROQ_API_KEY')
    )

    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"{prompt_text} Please provide a short answer.",
        }],
        model="llama-3.3-70b-versatile",
    )

    if hasattr(chat_completion, 'choices') and len(chat_completion.choices) > 0:
        model_response = chat_completion.choices[0].message.content
        return {"groq": model_response}
    else:
        return {"groq": "Error: Response structure unexpected."}

async def gemini_api_call(prompt_text):

    genai.configure(api_key=os.getenv('GENAI_API_KEY'))  
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_text)
    
    model_response = response.text
    return model_response

async def evaluate_row(prompt_text_formatted, llm_names):
    responses = []
    
    if "groq" in llm_names:
        responses.append(await groq_api_call(prompt_text_formatted))
    if "gemini" in llm_names:
        responses.append(await gemini_api_call(prompt_text_formatted))
    
    return responses

def parse_csv(file_path):
    rows = []
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)
    return rows

async def score_responses_with_openai(prompt_text, response, expected_output):

    # client = OpenAI(
    #     api_key= os.getenv('OPENAI_API_KEY')
    # )

    # scoring_prompt = (
    #     f"Evaluate the response below based on the correctness and faithfulness to the provided prompt "
    #     f"and expected output. Provide scores out of 10 as clean numerical values:\n\n"
    #     f"Prompt: {prompt_text}\n"
    #     f"Expected Output: {expected_output}\n"
    #     f"Response: {response}\n\n"
    #     f"Correctness (numerical value only):\nFaithfulness (numerical value only):"
    # )


    # completion = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     store=True,
    #     messages=[
    #         {"role": "user", "content": scoring_prompt}
    #     ]
    # )

    # scores = completion.choices[0].message.content


    genai.configure(api_key=os.getenv('GENAI_API_KEY'))

    scoring_prompt = (
        f"Evaluate the response below based on the correctness and faithfulness to the provided prompt "
        f"and expected output. Provide scores out of 10 as clean numerical values:\n\n"
        f"Prompt: {prompt_text.lower()}\n"  # Make the prompt text lowercase
        f"Expected Output: {expected_output.lower()}\n"  # Make the expected output lowercase
        f"Response: {response.lower()}\n\n"  # Make the response lowercase
        f"Correctness (numerical value only):\nFaithfulness (numerical value only):"
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(scoring_prompt)

    scores = response.text 

    try:
        
        correctness_match = re.search(r"Correctness:\s*(\d+(\.\d+)?)", scores, re.IGNORECASE)
        faithfulness_match = re.search(r"Faithfulness:\s*(\d+(\.\d+)?)", scores, re.IGNORECASE)

        if not correctness_match or not faithfulness_match:
            raise ValueError("Could not extract scores from response.")

        correctness = correctness_match.group(1)
        faithfulness = faithfulness_match.group(1)


    except Exception as e:
        raise ValueError(f"Unexpected response format: {scores}") from e

    return correctness, faithfulness
