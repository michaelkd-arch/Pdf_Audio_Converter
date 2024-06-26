import pyttsx3
from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_text
from boto3 import Session, client
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess

os.environ['AWS_SHARED_CREDENTIALS_FILE'] = r'C:\Users\wsr\.aws\credentials'
os.environ['AWS_DEFAULT_PROFILE'] = '<profile-name>'


def pdf_audio_converter(_text: str, output_filename: str):
    engine = pyttsx3.init(driverName='sapi5')

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.save_to_file(_text, output_filename)

    engine.runAndWait()
    print('Offline voice is ready')


def polly_converter(pdf_path: str, output_filename_path: str):
    file_path = output_filename_path
    text = extract_text(pdf_path)
    session = Session(profile_name='polly_admin')
    polly = session.client('polly', region_name='eu-central-1')

    try:
        response = polly.synthesize_speech(Text=text, OutputFormat='mp3',
                                           VoiceId='Joanna')
    except (BotoCoreError, ClientError) as error:
        print(error)
        print('Starting offline converter...')
        pdf_audio_converter(text, file_path)
        sys.exit(-1)
    if 'AudioStream' in response:
        with closing(response['AudioStream']) as stream:
            output = file_path
            try:
                with open(output, 'wb') as file:
                    file.write(stream.read())
            except IOError as error:
                print(error)
                sys.exit(-1)
    else:
        print('Could not stream audio')
        sys.exit(-1)

    if sys.platform == 'win32':
        os.startfile(output)
    else:
        opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.call([opener, output])



# polly_converter('Articles.pdf', 'ArtcilesAudio3.mp3')
