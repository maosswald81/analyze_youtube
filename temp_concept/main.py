import yt_dlp # type: ignore
import datetime
import whisper # type: ignore
from pydub import AudioSegment # type: ignore
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
import textwrap
import time
import tiktoken # type: ignore
import os
import pyttsx3 
import os
import re

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def fetch_urls():
    def is_valid_url(url):
        # Regular expression pattern for validating URLs
        pattern = re.compile(r'^(https?://)?([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?$')
        return re.match(pattern, url) is not None

    urls = []
    while True:
        user_input = input("Enter a URL of a YouTube video you wish to transcribe or type 'done' if you wish to stop: ")
        
        if user_input.lower() == 'done':
            break
        elif is_valid_url(user_input):  # Validate the URL
            urls.append(user_input)  # Add the valid URL to the list
            print(f"URL '{user_input}' added to the list.")
        else:
            print("Invalid URL. Please enter a valid URL or type 'done' to stop.")
    
    return urls
 
# Function to download and convert YouTube video to audio
def download_youtube_audio(urls, output_format='mp3'):
    # Create the 'youtube_audios' directory if it doesn't exist
    output_dir = 'youtube_audios'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Clear the contents of 'youtube_audios' directory to start fresh
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    for url in urls:
        try:
            # Extract the video title using yt-dlp
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'unknown_title').replace('/', '_').replace('\\', '_')

            ydl_opts = {
                'format': 'bestaudio/best',  # Download the best audio quality
                'outtmpl': os.path.join(output_dir, f"{video_title}.%(ext)s"),  # Save with video title
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file (assuming it's webm or another format)
            downloaded_file = os.path.join(output_dir, f"{video_title}.webm")  # Default downloaded format
            if not os.path.exists(downloaded_file):
                downloaded_file = os.path.join(output_dir, f"{video_title}.m4a")  # Alternative format

            # Convert the audio file to the desired format
            audio = AudioSegment.from_file(downloaded_file)
            output_filename = os.path.join(output_dir, f"{video_title}.{output_format}")
            audio.export(output_filename, format=output_format)
            print(f"Audio saved as {output_filename}")

            # Delete the original downloaded audio file
            os.remove(downloaded_file)
            print(f"Deleted the original downloaded audio file: {downloaded_file}")

        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")

def convert_files_to_mp3():
    directory="youtube_audios"
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        file_ext = os.path.splitext(filename)[1].lower()
        output_file = os.path.join(directory, os.path.splitext(filename)[0] + ".mp3")

        # Skip if already an MP3 file
        if file_ext == ".mp3":
            continue

        try:
            if file_ext in [".wav", ".ogg", ".flac", ".aac", ".m4a"]:
                print(f"Converting {filename} to MP3...")
                audio = AudioSegment.from_file(file_path, format=file_ext[1:])
                audio.export(output_file, format="mp3")

            elif file_ext in [".mp4", ".mkv", ".avi", ".mov"]:
                print(f"Extracting audio from {filename} using FFmpeg...")
                command = f'ffmpeg -i "{file_path}" -q:a 0 -map a "{output_file}" -y'
                subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            else:
                print(f"Skipping unsupported file type: {filename}")
                continue

            # Optional: Remove the original file after conversion
            os.remove(file_path)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

def transcribe_audio():
    model = whisper.load_model('base.en')
    output_dir = 'youtube_audios'
    save_target = 'transcription.txt'

    # Delete the existing transcription file if it exists, to start fresh
    if os.path.exists(save_target):
        os.remove(save_target)

    # Iterate over the files in the output directory
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        
        # Check if the file is an audio file (you can add more extensions if needed)
        if file_path.endswith(('.mp3', '.wav', '.webm', '.mp4')):
            try:
                # Transcribe the audio file
                result = model.transcribe(file_path)

                # Save the transcription to a text file
                with open(save_target, 'a') as file:
                    file.write(f"Transcription for {filename}:\n")
                    for indx, segment in enumerate(result['segments']):
                        file.write(f"   Segment {indx + 1}\n")
                        file.write(f"      {str(datetime.timedelta(seconds=segment['start']))} ---> {str(datetime.timedelta(seconds=segment['end']))}\n")
                        file.write(f"      {segment['text'].strip()}\n")
                    
                    file.write("\n")
                print(f"Transcription for {filename} saved successfully.")
                
            except Exception as e:
                print(f"An error occurred while transcribing {file_path}: {e}")


# def format_text_file(input_file: str, output_file: str, line_length: int):
#     # Read the content of the input file
#     with open(input_file, 'r') as file:
#         lines = file.readlines()

#     # Open the output file for writing
#     with open(output_file, 'w') as file:
#         for line in lines:
#             # Only wrap lines that exceed the specified line length
#             if len(line) > line_length:
#                 # Wrap the line to the specified length and write it to the file
#                 wrapped_line = textwrap.fill(line, width=line_length)
#                 file.write(wrapped_line + '\n')
#             else:
#                 # Write lines that are within the length limit as they are
#                 file.write(line)

def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")  # General encoding for GPT models
    return len(enc.encode(text))

def split_text(text: str, max_tokens: int):
    """Splits text into chunks that fit within the token limit."""
    words = text.split()
    chunks = []
    chunk = []
    token_count = 0

    for word in words:
        word_tokens = count_tokens(word)
        if token_count + word_tokens > max_tokens:
            chunks.append(" ".join(chunk))
            chunk = [word]
            token_count = word_tokens
        else:
            chunk.append(word)
            token_count += word_tokens

    if chunk:
        chunks.append(" ".join(chunk))

    return chunks

def ai_analyze():
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = "The following is the transcription for one or multiple videos. Analyze the content, summarize each video, and continue the conversation by answering any further questions."

    if os.path.exists('analyzed_transcription.txt'):
        os.remove('analyzed_transcription.txt')

    with open('analyzed_transcription.txt', 'a') as mainfile:
        with open('transcription.txt', 'r') as file:
            transcript = file.read()

        token_limit = 8000  # Set lower limit to prevent API rejection
        conversation_history = [{"role": "system", "content": prompt}]
        transcript_chunks = split_text(transcript, token_limit)

        for chunk in transcript_chunks:
            conversation_history.append({"role": "user", "content": chunk})
            chat_completion = client.chat.completions.create(
                messages=conversation_history, model="gpt-4-turbo", stream=True
            )

            response = ""
            for chunk_response in chat_completion:
                if chunk_response.choices[0].delta.content:
                    response += chunk_response.choices[0].delta.content
                    print(chunk_response.choices[0].delta.content, end="")
                    mainfile.write(chunk_response.choices[0].delta.content)

            print("\n")
            conversation_history.append({"role": "assistant", "content": response})
            time.sleep(5)  # Delay to stay within rate limits

        # Continuous Q&A loop
        while True:
            user_input = input("Do you have any further questions about the videos? (yes/no): ").strip().lower()
            if user_input in ["yes", "y"]:
                question = input("Ask your question: ")
                conversation_history.append({"role": "user", "content": question})

                chat_completion = client.chat.completions.create(
                    messages=conversation_history, model="gpt-4-turbo", stream=True
                )

                response = ""
                for chunk_response in chat_completion:
                    if chunk_response.choices[0].delta.content:
                        response += chunk_response.choices[0].delta.content
                        print(chunk_response.choices[0].delta.content, end="")
                        mainfile.write(chunk_response.choices[0].delta.content)

                print("\n")
                conversation_history.append({"role": "assistant", "content": response})
                time.sleep(5)

            elif user_input in ["no", "n"]:
                print("Goodbye!")
                break
try:
    response = input("Do you want to enter in new urls to transcribe?\nEnter y for yes and n for no: ")
    if 'y' in response.lower():
        urls = fetch_urls()
        print("Collected URLs:", urls)
        download_youtube_audio(urls, 'mp3')  # You can change 'mp3' to 'wav' or other formats
        convert_files_to_mp3()
        transcribe_audio()
    response = input("Do you want to to use ai to analyze transcription?\nEnter y for yes and n for no: ")
    if 'y' in response.lower(): 
        ai_analyze()
    time.sleep(3)
    # format_text_file('analyzed_transciption.txt', 'analyzed_transciption.txt', 80)
except ValueError as e:
    print(e)

