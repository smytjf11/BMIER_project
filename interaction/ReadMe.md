# Python Voice Assistant

This Python program runs in a Docker container and uses the host's microphone to listen for a keyword, transcribe the sentence, pass it to a Large Language Model via an API, and play the response over the host system's speakers.

## Prerequisites

Before running this program, make sure you have the following installed on your system:

- Docker
- Python 3
- Any necessary Python packages, such as `speechrecognition` and `pyaudio`

## Running the Program

To run the program, follow these steps:

1. Build the Docker image:

```bash
docker build -t python-voice-assistant .
```

2. Run the Docker container, making sure to allow access to the host's audio devices:

```bash
docker run --rm -it --device /dev/snd python-voice-assistant
```

3. Wait for the program to prompt you to speak a command. When you speak the keyword, the program will transcribe your sentence and send it to the Large Language Model via an API. The response will be played over the host system's speakers.

## Customization

You can customize the behavior of the program by modifying the following parameters:

* Keyword: The program will only listen for and transcribe sentences that begin with the specified keyword.
* Large Language Model: The program will send the transcribed sentence to the specified Large Language Model via an API and use the response to generate a response.

## Troubleshooting

If you encounter any issues while running the program, make sure that you have installed all of the necessary prerequisites and that you have granted the Docker container access to the host's audio devices. If the problem persists, check the program's logs for more information.
