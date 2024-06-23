import sys
import os
import time
import re
import json
import requests
import opencc
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Get environment variables
OLLAMA_HOST = os.getenv('OLLAMA_HOST')
MINIO_SERVER = os.getenv('MINIO_SERVER')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
TRANSCRIPT_PATH = os.getenv('TRANSCRIPT_PATH')

class JsonFileHandler:
    def __init__(self, minio_client, bucket_name):
        self.minio_client = minio_client
        self.bucket_name = bucket_name

    def process_file(self, file_path):
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extract meet_id from room_name
        meet_id = data["room_name"].split('@')[0]
                
        print(f"MeetID: {meet_id}")
        
        # Process events
        formatted_texts = []
        for event in data["events"]:
            if event["event"] == "SPEECH":
                participant_name = event["participant"]["name"]
                transcript_text = event["transcript"][0]["text"]  # Assuming there's always at least one transcript entry
                formatted_text = f'{participant_name} says: {transcript_text}'
                formatted_texts.append(formatted_text)
        
        # Join all formatted texts
        text = "\n".join(formatted_texts)
        print(text)
        if text:
            summary = chat_with_ollama(text)            
            print(summary)
            converter = opencc.OpenCC('s2t.json') # converting simplified chinese to tranditional chinese (tw)
            summary_text = converter.convert(summary["message"]["content"])
            summary_file_path = f"{meet_id}.summary.txt"
            # Write the summary to the file
            with open(summary_file_path, 'w', encoding='utf-8') as file:
                file.write(summary_text)
            print(f"Summary written to {summary_file_path}")
            self.upload_to_minio(summary_file_path)
            print(f"Uploaded summary to {summary_file_path} in bucket {self.bucket_name}")            

    def upload_to_minio(self, summary_file_path):
        try:
            print(f'About to upload from {summary_file_path}')
            with open(summary_file_path, 'rb') as file_data:
                file_stat = os.stat(summary_file_path)
                remote_path = f"{TRANSCRIPT_PATH}/{os.path.basename(summary_file_path)}"
                self.minio_client.put_object(
                    self.bucket_name,
                    remote_path,
                    data=file_data,
                    length=file_stat.st_size,
                    content_type='text/plain'
                )
            print(f"Successfully uploaded to MinIO at {summary_file_path}")
        except S3Error as exc:
            print(f"Failed to upload to MinIO: {exc}")

def chat_with_ollama(text):
    # """ Use ollama.chat to send text to the model and get a response. """
    # response = ollama.chat(options=ollama_options, model="ycchen/breeze-7b-instruct-v1_0", stream=False, messages=[
    #     {'role': 'system', 'content': 'Summarize the provided meeting transcript that features at least two participants. Exclude all salutations, farewells, remarks about microphone checks or audio issues, and any timestamps. Carefully read the entire transcript to grasp the main discussion points, then provide a summary. The summary should be comprehensive, containing at least 300 words. Output in Traditional Chinese. English acronyms or abbreviations can leave as is.'},
    #     {'role': 'user', 'content': text}
    #     ])
    # Define the endpoint and headers
    endpoint = f"{OLLAMA_HOST}/api/chat"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "model": "ycchen/breeze-7b-instruct-v1_0",
        "stream": False,
        "messages": [
            {'role': 'system', 'content': 'Summarize the provided meeting transcript that features at least two participants. Exclude all salutations, farewells, remarks about microphone checks or audio issues, and any timestamps. Carefully read the entire transcript to grasp the main discussion points, then provide a summary. The summary should be comprehensive, containing at least 300 words. Output in Traditional Chinese. English acronyms or abbreviations can leave as is.'},
            {'role': 'user', 'content': text}
        ]
    }
    # Send the request
    try:
        response = requests.post(endpoint, json=payload, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")

# Main execution flow
if __name__ == "__main__":

    # Check if directory path is provided
    if len(sys.argv) != 2:
        print("Usage: python main.py <absolute_directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    # Ensure the path is absolute
    if not os.path.isabs(directory_path):
        print("Please provide an absolute directory path.")
        sys.exit(1)
    
    # Get the JSON file in the directory
    json_files = [file for file in os.listdir(directory_path) if file.endswith('.json')]
    if len(json_files) != 1:
        print("The directory should contain exactly one JSON file.")
        sys.exit(1)
    
    json_file_path = os.path.join(directory_path, json_files[0])
    
    # Initialize MinIO client
    minio_client = Minio(
        MINIO_SERVER,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False  # Set to True if using HTTPS
    )

    event_handler = JsonFileHandler(minio_client, MINIO_BUCKET_NAME)
    event_handler.process_file(json_file_path)