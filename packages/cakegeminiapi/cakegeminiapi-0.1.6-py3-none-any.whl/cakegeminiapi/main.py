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
import httplib2
import urllib3

def set_proxy(proxy_url=None):
    """设置全局代理"""
    if proxy_url:
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        # 为 httplib2 设置代理
        httplib2.Http.proxy_info = httplib2.ProxyInfo(
            proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
            proxy_host=proxy_url.split(':')[0],
            proxy_port=int(proxy_url.split(':')[1]) if ':' in proxy_url else 80
        )
        # 为 urllib3 设置代理
        urllib3.make_headers(proxy_basic_auth=None)

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

def video2txt(api_key, video_path, prompt_text, proxy=None):
    """Analyzes a video to get a summary and breakdown into key scenes."""
    # 设置代理
    set_proxy(proxy)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.0-flash') # Corrected model name

    video_files = upload_video_chunks(video_path)
    
    # Wait for files to become active before using them
    wait_for_files_active(video_files)

    # Prompt to get summary and scene breakdown
    contents = [prompt_text] + video_files

    print("Sending request for video analysis and style extraction...")
    response = model.generate_content(contents)
    
    for video_file in video_files:
        genai.delete_file(video_file.name)
    print("Deleted temporary uploaded files.")

    return response.text

def ai_video_commentator(api_key, video_path, prompt_text, proxy=None):
    """Generates a video commentary script in SRT format."""
    # 设置代理
    set_proxy(proxy)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.0-flash') # Corrected model name

    video_files = upload_video_chunks(video_path)
    
    # Wait for files to become active before using them
    wait_for_files_active(video_files)

    contents = [prompt_text]

    print("Sending request for video commentary generation...")
    response = model.generate_content(contents)
    
    for video_file in video_files:
        genai.delete_file(video_file.name)
    print("Deleted temporary uploaded files.")

    return response.text

def main():
    argparser = argparse.ArgumentParser(description="""Video Analysis""",
    epilog="""-------------------------------
    Example usage:
        geminiapi video_path "your prompt" -k GEMINI_API_KEY --proxy http://127.0.0.1:7890 # 或导出环境变量 GOOGLE_API_KEY
        
    Code sample:
        from geminiapi import video2txt
        output = video2txt(api_key, video_path, prompt_text, proxy="http://127.0.0.1:7890") 
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter
    )

    argparser.add_argument("-k", "--api_key", type=str, required=False, help="Google API key for Gemini. https://aistudio.google.com/apikey")
    argparser.add_argument("video_path", type=str, help="Path to the video file.")
    argparser.add_argument("prompt_text", type=str, help="Prompt text for video analysis.")
    argparser.add_argument("--proxy", type=str, help="Proxy URL (e.g., http://127.0.0.1:7890)")
    
    args = argparser.parse_args()

    api_key = args.api_key if args.api_key else os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API key is required. Please set the GOOGLE_API_KEY environment variable or use the -k option.")
    
    video_path = args.video_path
    prompt_text = args.prompt_text
    proxy = args.proxy if args.proxy else os.getenv("HTTP_PROXY")
    
    output = video2txt(
        api_key=api_key,
        video_path=video_path,
        prompt_text=prompt_text,
        proxy=proxy
    )
    print(output)

if __name__ == "__main__":
    main()