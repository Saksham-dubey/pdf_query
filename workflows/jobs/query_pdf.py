from openai import OpenAI
from dotenv import load_dotenv
import os
from workflows.utils.utils import list_pdf_files
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

pdf_directory = os.path.join(os.getcwd(),"PDF") 

url_list = list_pdf_files(pdf_directory)

file = client.files.create(
    file=open(url_list[0], "rb"),
    purpose="user_data"
)

file_1 = client.files.create(
    file=open(url_list[1], "rb"),
    purpose="user_data"
)
# files = client.files.create(
#     file=open(url_list, "rb"),
#     purpose="user_data"
# )

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
           
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_file",
                    "file_id": file_1.id,
                },
                {
                    "type": "input_text",
                    "text": "Complete this Systematic design and ... ?",
                },
            ]
        }
    ]
)

response_data = response.output[0].content[0].text
print(response_data)

