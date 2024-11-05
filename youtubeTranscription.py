import pyaudio
import numpy as np
import threading
import ssl
import spacy
import spacy.cli
from youtube_transcript_api import YouTubeTranscriptApi

# Initialize SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Load the NLP model
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

# Function to get the transcript from a YouTube video
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

# User input for YouTube video ID
def user_input_control():
    video_id = input("Please enter the YouTube video ID: ").strip()
    transcript = get_transcript(video_id)
    if transcript:
        identify_factual_statements(transcript)

if __name__ == "__main__":
    try:
        user_input_control()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Exiting...")
    finally:
        print("Goodbye!")
