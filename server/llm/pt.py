# import os

# from groq import Groq

# client = Groq(
#     api_key='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',
# )

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "What is the capital of France? Please provide a short answer.",
#         }
#     ],
#     model="llama-3.3-70b-versatile",
# )

# print(chat_completion.choices[0].message.content)


import google.generativeai as genai

genai.configure(api_key="AIzaSyCWinZe3S4EfgGc0StRgQDOqUeCG0KUOdw")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("What is the capital of France? Please provide a short answer.")
print(response.text)