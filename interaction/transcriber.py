from urllib.error import HTTPError
import asyncio
import openai
import pocketsphinx
import configparser
import logging
import retrying
import gTTS

logger = logging.getLogger(__name__)

def get_config(config_file_path: str = 'config.ini') -> configparser.ConfigParser:
    with open(config_file_path) as f:
        config = configparser.ConfigParser()
        config.read_file(f)
    return config

class VoiceAssistantError(Exception):
    def __init__(self, message: str, step: str):
        self.message = message
        self.step = step

def generic_handle_error(e: VoiceAssistantError):
    error_string = 'Error: {} occurred in step: {}'.format(e.message, e.step)
    print(error_string)
    logger.error(error_string)


import pocketsphinx

async def get_audio_from_microphone(keyword):
    # Set up the pocketsphinx decoder
    config = pocketsphinx.Decoder.default_config()
    config.set_string('-keyphrase', keyword)
    config.set_float('-kws_threshold', 1e-20)
    decoder = pocketsphinx.Decoder(config)

    # Set up the microphone input
    mic = pocketsphinx.AudioFile(16000, None, True)
    mic.start_recording()

    # Wait for the keyword to be spoken
    decoder.start_utt()
    while True:
        buf = mic.get_audio()
        if buf:
            decoder.process_raw(buf, False, False)
        else:
            break
        if decoder.hyp() is not None:
            break
    decoder.end_utt()

    # Start recording audio
    audio = b''
    decoder.start_utt()
    while True:
        buf = mic.get_audio()
        if buf:
            decoder.process_raw(buf, False, False)
            audio += buf
        else:
            break
        if decoder.hyp() is not None:
            # Check if the keyword has been spoken again (indicating a pause)
            if decoder.hyp().hypstr == keyword:
                break
    decoder.end_utt()

    # Stop recording and return the audio
    mic.stop_recording()
    return transcribe_audio(audio)


def transcribe_audio(audio):
    # Set up the CMUSphinx model
    model = pocketsphinx.Decoder()
    model.start_utt()
    model.process_raw(audio, False, True)
    model.end_utt()
    transcription = model.hyp().hypstr
    return transcription




def generate_text(prompt, config):
  # Set the API key
  openai.api_key = config.api_key

  # Set the model to use for the request
  model = config.model

  # Generate text using the language model
  completion = openai.Completion.create(engine=model, prompt=prompt, max_tokens=128, stop=["."])

  # Get the generated text as a string
  output_string = completion.text

  # Return the output string
  return output_string


@retrying.retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
async def text_to_speech(response, config):
    # Try generating the audio file using gTTS and update on the success
    try:
        tts = gTTS(response, lang=config['INTERACT']['TTS']['language'])
        tts.save(config['INTERACT']['TTS']['output_file'])
        logger.info('Audio file generated successfully')
        return('success')
    except HTTPError as e:
        generic_handle_error(e, step='TTS')
        return(e)


async def main(config_file_path):
    # Create a Config object
    config = get_config(config_file_path)

    # Set up Microphone and wait for a signal
    prompt = await get_audio_from_microphone()

    # Generate text using the function
    response = generate_text(prompt, config)
    
    # Say the output string
    text_to_speech(response, config)

if __name__ == '__main__':
    config_file_path = 'config.ini'

    # start the loop
    asyncio.run(main(config_file_path))




