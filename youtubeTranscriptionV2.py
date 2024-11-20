
# 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

import ssl
import spacy
import spacy.cli
import re
import os
import whisper
import yt_dlp
import ffmpeg
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI


api_key_text = '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'


client = OpenAI(api_key=api_key_text)
# openai.api_key = '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'

# Initialize SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Load the NLP model
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

# Function to get transcript using YouTubeTranscriptApi as a fallback
def get_transcript(video_id):
    try:
        transcript_dict = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([entry['text'] for entry in transcript_dict])
        print("Full Transcript Retrieved:\n", full_transcript)
        return full_transcript
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return None

# Function to identify factual statements with numbers or statistics

# def identify_factual_statements(transcript):
#     prompt = f"Identify factual statements containing numbers, statistics, dates, or specific factual details from the following transcript:\n{transcript}"
#     completion = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt}
#         ]
#     )
#     statements = completion.choices[0].message['content']
#     print("\nIdentified Factual Statements:\n", statements)
# def identify_factual_statements(transcript):
#     prompt = "Identify factual statements containing numbers, statistics, dates, or specific factual details from the following transcript:\n" + transcript
#     response = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=prompt,
#         max_tokens=500,
#         temperature=0
#     )
#     statements = response.choices[0].text.strip()
#     print("\nIdentified Factual Statements:\n", statements)


def identify_factual_statements(transcript):
    doc = nlp(transcript)
    entities_of_interest = ['CARDINAL', 'PERCENT', 'MONEY', 'QUANTITY', 'DATE', 'TIME', 'ORDINAL']
    
    # Extract sentences with relevant entities
    factual_statements = [
        sent.text for sent in doc.sents 
        if any(ent.label_ in entities_of_interest for ent in sent.ents)
    ]
    
    # Display identified factual statements
    print("\nIdentified Factual Statements:")
    for statement in factual_statements:
        print(statement)

# Function to extract video ID from URL
def extract_video_id(url):
    # Regular expression for YouTube URL
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Function to download audio from YouTube using yt_dlp
def download_audio_from_youtube(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return "audio.wav"  # File saved as audio.wav due to ydl_opts settings
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

# Function to transcribe audio using Whisper
def transcribe_audio(file_path):
    try:
        model = whisper.load_model("base")  # Load Whisper model
        result = model.transcribe(file_path)  # Transcribe audio
        print("Transcription:\n", result["text"])
        return result["text"]
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None

# Main function to handle user input and transcribe video
def transcribe_youtube_video(url):
    video_id = extract_video_id(url) if "youtube" in url else url
    if not video_id:
        print("Invalid YouTube URL or ID.")
        return

    # Try to download and transcribe audio using Whisper
    print("Downloading audio...")
    audio_file = download_audio_from_youtube(url)
    if audio_file:
        print("Transcribing audio...")
        transcript = transcribe_audio(audio_file)
        os.remove(audio_file)  # Cleanup the audio file after transcription
        
        if transcript:
            identify_factual_statements(transcript)
        else:
            print("Failed to transcribe audio.")
    else:
        # If Whisper transcription fails, try YouTube's text-based transcript as a fallback
        print("Attempting to retrieve transcript from YouTube API...")
        transcript = get_transcript(video_id)
        if transcript:
            identify_factual_statements(transcript)
        else:
            print("Failed to retrieve transcript from YouTube API.")

# Ask user for the YouTube URL
if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ").strip()
    transcribe_youtube_video(url)


