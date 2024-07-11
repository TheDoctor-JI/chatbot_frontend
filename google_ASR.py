import argparse
from google.cloud import speech
import dotenv
import os

dotenv.load_dotenv()

def transcribe_file_with_auto_punctuation(
    content: bytes, language_code: str = "yue-Hant-HK",
) -> speech.RecognizeResponse:
    """Transcribe the given audio file with auto punctuation enabled."""
    client = speech.SpeechClient(credentials=os.getenv("GOOGLE_API_KEY"))

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code=language_code,
        enable_automatic_punctuation=True,
        audio_channel_count=2,
        enable_word_time_offsets=True,
    )

    response = client.recognize(config=config, audio=audio)

    for i, result in enumerate(response.results):
        alternative = result.alternatives[0]
        print("-" * 20)
        print(f"First alternative of result {i}")
        print(f"Transcript: {alternative.transcript}")

    return response
