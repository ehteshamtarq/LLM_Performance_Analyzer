import os
import csv
import aiohttp
import asyncio
import google.generativeai as genai
from groq import Groq
from .models import EvaluationResult  # Assuming the model exists for storing results
from openai import OpenAI
import re
from dotenv import load_dotenv

load_dotenv()

async def groq_api_call(prompt_text):

    client = Groq(
    api_key = os.getenv('GROQ_API_KEY')
    )

    # Making a request to the Groq API (no 'await' needed here)
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": f"{prompt_text} Please provide a short answer.",
        }],
        model="llama-3.3-70b-versatile",
    )

    # Assuming chat_completion contains a 'choices' field, access like this:
    if hasattr(chat_completion, 'choices') and len(chat_completion.choices) > 0:
        model_response = chat_completion.choices[0].message.content
        return {"groq": model_response}
    else:
        # Return an error message if the expected structure isn't found
        return {"groq": "Error: Response structure unexpected."}

async def gemini_api_call(prompt_text):

    genai.configure(api_key=os.getenv('GENAI_API_KEY'))  
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_text)
    
    # Extract the response text
    model_response = response.text
    return model_response

async def evaluate_row(prompt_text_formatted, llm_names):
    responses = []
    
    # Loop through the requested LLMs (e.g., Groq and Gemini)
    if "groq" in llm_names:
        responses.append(await groq_api_call(prompt_text_formatted))
    if "gemini" in llm_names:
        responses.append(await gemini_api_call(prompt_text_formatted))
    
    return responses

def calculate_scores(response, expected_output):
    # Placeholder scoring logic (replace with actual scoring algorithms)
    correctness = 10 if expected_output in response else 5
    faithfulness = 8  # Placeholder score
    return correctness, faithfulness

def parse_csv(file_path):
    rows = []
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)
    return rows

async def score_responses_with_openai(prompt_text, response, expected_output):

    client = OpenAI(
        api_key= os.getenv('OPENAI_API_KEY')
    )

    scoring_prompt = (
        f"Evaluate the response below based on the correctness and faithfulness to the provided prompt "
        f"and expected output. Provide scores out of 10 as clean numerical values:\n\n"
        f"Prompt: {prompt_text}\n"
        f"Expected Output: {expected_output}\n"
        f"Response: {response}\n\n"
        f"Correctness (numerical value only):\nFaithfulness (numerical value only):"
    )


    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": scoring_prompt}
        ]
    )

    scores = completion.choices[0].message.content

    try:
        # Flexible regex to capture numbers for both Correctness and Faithfulness
        correctness_match = re.search(r"Correctness:\s*(\d+(\.\d+)?)", scores, re.IGNORECASE)
        faithfulness_match = re.search(r"Faithfulness:\s*(\d+(\.\d+)?)", scores, re.IGNORECASE)

        if not correctness_match or not faithfulness_match:
            raise ValueError("Could not extract scores from response.")

        # Extract and convert scores to float
        correctness = (correctness_match.group(1))
        faithfulness = (faithfulness_match.group(1))

    except Exception as e:
        raise ValueError(f"Unexpected response format: {scores}") from e

    return correctness, faithfulness
