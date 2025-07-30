import argparse
import os
import time
import requests
import hashlib
import json
import subprocess
import re # Import the re module
from tqdm import tqdm
from datetime import datetime

import google.generativeai as genai

# Configure the API key
# Ensure GOOGLE_API_KEY is set as an environment variable

def upload_video_chunks(video_path):
    """Uploads video in chunks and returns a list of File objects."""
    print(f"Uploading {video_path}...")
    video_file_name = os.path.basename(video_path)
    
    # Determine chunk size (e.g., 10MB)
    chunk_size = 10 * 1024 * 1024  # 10 MB
    
    file_parts = []
    total_size = os.path.getsize(video_path)
    
    with open(video_path, 'rb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Uploading video") as pbar:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Create a temporary file for the chunk
                temp_chunk_path = f"/tmp/{video_file_name}_chunk_{len(file_parts)}.tmp"
                with open(temp_chunk_path, 'wb') as temp_f:
                    temp_f.write(chunk)
                
                # Upload the chunk as a File object
                file = genai.upload_file(path=temp_chunk_path, mime_type="video/mp4")
                file_parts.append(file)
                
                # Clean up the temporary chunk file
                os.remove(temp_chunk_path)
                
                pbar.update(len(chunk))
                
    print(f"Uploaded {len(file_parts)} chunks.")
    return file_parts

def wait_for_files_active(files):
    """Waits for uploaded files to become active."""
    print("Waiting for files to be processed...")
    for file in files:
        while True:
            file_info = genai.get_file(file.name)
            if file_info.state.name == "ACTIVE":
                print(f"File {file.name} is now active.")
                break
            elif file_info.state.name == "FAILED":
                raise ValueError(f"File {file.name} failed to process.")
            else:
                print(f"File {file.name} is {file_info.state.name}, waiting...")
                time.sleep(2)
    print("All files are now active and ready to use.")

def video2txt(api_key, video_path, prompt_text):
    """Analyzes a video to get a summary and breakdown into key scenes."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.0-flash') # Corrected model name

    video_files = upload_video_chunks(video_path)
    
    # Wait for files to become active before using them
    # wait_for_files_active(video_files)

    # Prompt to get summary and scene breakdown
    contents = [prompt_text]

    print("Sending request for video analysis and style extraction...")
    response = model.generate_content(contents)
    
    for video_file in video_files:
        genai.delete_file(video_file.name)
    print("Deleted temporary uploaded files.")

    return response.text

def main():
    argparser = argparse.ArgumentParser(description="Analyze a video and extract key scenes.")
    argparser.add_argument("-k", "--api_key", type=str, required=True, help="Google API key for Gemini.")
    argparser.add_argument("video_path", type=str, help="Path to the video file.")
    argparser.add_argument("--prompt_text", type=str, default="分析这个视频并提供关键场景的总结", help="Prompt text for video analysis.")
    args = argparser.parse_args()
    
    output = video2txt(
        api_key=args.api_key,
        video_path=args.video_path,
        prompt_text=args.prompt_text
    )
    print(output)

if __name__ == "__main__":
    main()