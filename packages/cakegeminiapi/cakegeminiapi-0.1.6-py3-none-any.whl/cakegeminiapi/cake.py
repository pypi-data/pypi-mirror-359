import os
from .core import video2txt
from .prompts import PROMPT_VIDEO_Commentator

class CakeGeminiAPI:
    def __init__(self, api_key, proxy=None):
        self.api_key = api_key
        self.proxy = proxy

    def video2txt(self, video_path, prompt_text):
        """
        给定视频和提示词，完成提示词要求的任务
        """
        return video2txt(self.api_key, video_path, prompt_text, self.proxy)

    def video_commentator(self, video_path):
        """
        视频解说员
        """
        return video2txt(self.api_key, video_path, PROMPT_VIDEO_Commentator, self.proxy)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="CakeGeminiAPI Video Commentator")
    parser.add_argument("-k", "--api_key", type=str, required=False, help="Google API key for Gemini. https://aistudio.google.com/apikey")
    parser.add_argument("video_path", type=str, help="Path to the video file")
    parser.add_argument("-p", "--proxy", type=str, default=None, help="Proxy server URL (optional)")

    args = parser.parse_args()


    api_key = args.api_key if args.api_key else os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API key is required. Please set the GOOGLE_API_KEY environment variable or use the -k option.")
    api = CakeGeminiAPI(api_key=api_key, proxy=args.proxy)
    result = api.video_commentator(args.video_path)
    print(result)

if __name__ == "__main__":
    main()