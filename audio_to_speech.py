import os
import sys
import speech_recognition as sr
from pydub import AudioSegment

def convert_audio_to_text(audio_file_path, output_text_file):
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Convert the audio file to a format compatible with the recognizer
    audio = AudioSegment.from_file(audio_file_path)
    converted_audio_path = "converted_audio.wav"
    audio.export(converted_audio_path, format="wav")

    # Load the converted audio file for speech recognition
    with sr.AudioFile(converted_audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            # Perform the transcription using Google Web Speech API
            text = recognizer.recognize_google(audio_data)
            
            # Save the transcription to a text file
            with open(output_text_file, "w") as file:
                file.write(text)
            
            print(f"Transcription saved to {output_text_file}")
        
        except sr.UnknownValueError:
            print("Google Web Speech API could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Web Speech API; {e}")

if __name__ == "__main__":
    # Ask for the input audio file path
    audio_file_path = input("Please enter the path to the input audio file: ").strip()
    
    # Remove surrounding quotes if present
    if audio_file_path.startswith('"') and audio_file_path.endswith('"'):
        audio_file_path = audio_file_path[1:-1]
    elif audio_file_path.startswith("'") and audio_file_path.endswith("'"):
        audio_file_path = audio_file_path[1:-1]

    # Check if the file exists
    if not os.path.isfile(audio_file_path):
        print(f"Error: The file '{audio_file_path}' does not exist.")
        sys.exit(1)
    
    # Ask for the output text file path
    output_text_file = input("Please enter the path for the output text file: ").strip()
    
    # Convert audio to text and save to file
    convert_audio_to_text(audio_file_path, output_text_file)

