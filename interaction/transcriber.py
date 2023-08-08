from urllib.error import HTTPError #This import statement allows you to import the HTTPError class from the urllib.error module. This class represents an HTTP error that occurred when attempting to fetch a URL. You can use it to handle errors that may occur when making HTTP requests.
import asyncio # This import statement brings in the asyncio module, which provides support for asynchronous programming in Python. You can use asyncio to write concurrent code using the async and await keywords.
import openai # This import statement brings in the openai module, which is a Python wrapper for the OpenAI API. You can use this module to access the various language processing services provided by OpenAI, such as text generation and machine translation.
import pocketsphinx # This import statement brings in the pocketsphinx module, which is a Python wrapper for the PocketSphinx speech recognition engine. You can use this module to perform speech-to-text conversion, such as transcribing spoken words into written text.
import configparser # This import statement brings in the configparser module, which provides support for reading and writing configuration files. You can use this module to parse configuration files that contain sections and options, and access their values.
import logging # This import statement brings in the logging module, which provides support for logging messages and events in Python. You can use this module to log messages at different levels of severity (e.g. debug, info, warning, error) and output them to various destinations (e.g. console, file, network).
import retrying # This import statement brings in the retrying module, which provides support for retrying function calls in the event of an error. You can use this module to define retry strategies (e.g. maximum number of retries, retry on specific exceptions) and apply them to function calls using the @retrying.retry decorator.


logger = logging.getLogger(__name__)

def get_config(config_file_path):
    if config_file_path.isnull():
        config_file_path = 'config.ini'

    config = configparser.ConfigParser()
    config.read(config_file_path)

    return config

def generic_handle_error(e, step):
    # String to describe the error
    errorString = f'Error: {e} occurred in step: {step}'

    # Print the error message to the console and write it to the log
    print(errorString)
    logger.error(errorString)


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




