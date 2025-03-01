import yt_dlp # type: ignore
import datetime
import whisper # type: ignore
from pydub import AudioSegment
from openai import OpenAI
from dotenv import load_dotenv
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

    i = 1
    for url in urls:
        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best audio quality
            'outtmpl': os.path.join(output_dir, 'downloaded_audio.%(ext)s'),  # Save inside 'youtube_audios' folder
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Convert the audio file to the desired format
            downloaded_file = os.path.join(output_dir, 'downloaded_audio.webm')  # Default audio file format
            audio = AudioSegment.from_file(downloaded_file)
            output_filename = os.path.join(output_dir, f"audio{i}.{output_format}")  # Save inside 'youtube_audios' folder
            audio.export(output_filename, format=output_format)
            print(f"Audio saved as {output_filename}")
            
            # Step 3: Delete the downloaded audio file
            os.remove(downloaded_file)
            print(f"Deleted the original downloaded audio file: {downloaded_file}")
            i += 1
            
        except Exception as e:
            print(f"An error occurred: {e}")

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
        if file_path.endswith(('.mp3', '.wav', '.webm')):
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


def format_text_file(input_file: str, output_file: str, line_length: int):
    # Read the content of the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Open the output file for writing
    with open(output_file, 'w') as file:
        for line in lines:
            # Only wrap lines that exceed the specified line length
            if len(line) > line_length:
                # Wrap the line to the specified length and write it to the file
                wrapped_line = textwrap.fill(line, width=line_length)
                file.write(wrapped_line + '\n')
            else:
                # Write lines that are within the length limit as they are
                file.write(line)

def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")  # General encoding for GPT models
    return len(enc.encode(text))

def ai_analyze():
    client = OpenAI(api_key=OPENAI_API_KEY)
    # engine = pyttsx3.init()
    # engine.runAndWait()

    prompt = "The following is the transcriptions for one or multiple videos. I want you to analyze what is being said and summarize the each video and answer further questions that I might have."

    if os.path.exists('analyzed_transciption.txt'):
        os.remove('analyzed_transciption.txt')

    with open('analyzed_transciption.txt', 'a') as mainfile:
        with open('transcription.txt', 'r') as file:
            transcript = file.read()

        # Check if the transcript exceeds the token limit
        token_limit = 16385  # For GPT-3.5
        tokens = count_tokens(transcript)

        # If the transcript exceeds the limit, break it into smaller parts
        if tokens > token_limit:
            print(f"Transcript has {tokens} tokens, which exceeds the limit of {token_limit}. Splitting...")

            # Split by video or content length (in segments of the transcript)
            segments = transcript.split('\n\n')  # Split by paragraphs or sections
            chunk = ""
            for i, segment in enumerate(segments):
                # Add the current segment and check if the chunk size exceeds the limit
                potential_chunk = chunk + "\n\n" + segment
                if count_tokens(potential_chunk) <= token_limit:
                    chunk = potential_chunk  # Add this segment to the chunk
                else:
                    # Send the current chunk to OpenAI
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt + chunk}],
                        model="gpt-3.5-turbo"
                    )

                    print(chat_completion.choices[0].message.content)
                    mainfile.write(chat_completion.choices[0].message.content)
                    # engine.say(chat_completion.choices[0].message.content)
                    # engine.runAndWait()

                    # Start a new chunk for the next set of segments
                    chunk = segment

            # Handle any remaining content in the chunk
            if chunk:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt + chunk}],
                    model="gpt-3.5-turbo"
                )
                print(chat_completion.choices[0].message.content)
                mainfile.write(chat_completion.choices[0].message.content)
                # engine.say(chat_completion.choices[0].message.content)
                # engine.runAndWait()

        else:
            # Process the full transcript if it's under the token limit
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt + transcript}],
                model="gpt-3.5-turbo"
            )

            print(chat_completion.choices[0].message.content)
            mainfile.write(chat_completion.choices[0].message.content)
            # engine.say(chat_completion.choices[0].message.content)
            # engine.runAndWait()

        while True:
            # engine.say("Do you have any further questions about the videos?")
            # engine.runAndWait()
            user_input = input("Do you have any further questions about the videos? Your answer: ")

            if "yes" in user_input.lower() or "yeah" in user_input.lower() or "y" in user_input.lower():
                prompt = "The following is a transcribed youtube video. I want you to answer my question according to the information found in this video. "
                print("Type your question here: ")
                # engine.say("Type your question here")
                # engine.runAndWait()
                user_input = input("Ask a question: ")

                print("You asked " + user_input)

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": user_input + prompt + transcript}],
                    model="gpt-3.5-turbo"
                )

                print(chat_completion.choices[0].message.content)
                mainfile.write(chat_completion.choices[0].message.content)
                # engine.say(chat_completion.choices[0].message.content)
                # engine.runAndWait()
            else:
                exit()
try:
    response = input("Do you want to enter in new urls to transcribe?\nEnter y for yes and n for no: ")
    if 'y' in response.lower():
        urls = fetch_urls()
        print("Collected URLs:", urls)
        download_youtube_audio(urls, 'mp3')  # You can change 'mp3' to 'wav' or other formats
        transcribe_audio()
    response = input("Do you want to to use ai to analyze transcription?\nEnter y for yes and n for no: ")
    if 'y' in response.lower(): 
        ai_analyze()
    time.sleep(3)
    format_text_file('analyzed_transciption.txt', 'analyzed_transciption.txt', 80)
except ValueError as e:
    print(e)

