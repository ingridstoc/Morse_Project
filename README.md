 ## Morse Code Speech-to-Text Application

## Description

The Morse Code Speech-to-Text Application is a Python-based project that allows users to record audio messages, convert them to Morse code, encrypt and transmit them, and then receive and decode the Morse code back into text and audio. The application is designed to demonstrate audio processing, encryption, network communication, and Morse code manipulation.

## Features

+ **Audio Recording & Speech Recognition**: Capture spoken messages using the microphone and convert them to text using Google Speech Recognition.

+ **Text to Morse Code Conversion**: Convert text messages to Morse code format, both as text and audio.

+ **Morse Code Audio Encryption**: Encrypt Morse code audio files using AES-256 encryption with a user-provided password.

+ **Socket-Based Communication**: Transmit the encrypted Morse code audio file between two devices (emitter and receiver).

+ **Decryption & Decoding**: Decrypt the received audio file and decode the Morse code back to readable text.

+ **Text-to-Speech Playback**: Convert the decoded text back into a spoken audio message using Google Text-to-Speech (gTTS).

## Technologies Used

+ **Python**
  
+ **SpeechRecognition**: Audio-to-text conversion.
  
+ **gTTS**: Text-to-speech conversion.
  
+ **Pydub**: Audio processing and manipulation.
  
+ **Cryptography**: AES encryption and decryption of the audio Morse message
  
+ **Socket**: Network communication.

## Installation & Setup

## Prerequisites
Ensure you have the following installed:
-Python (minim 3.6 version)
-pip (Python package installer)

## Installation

1. Clone the repository:
```
git clone https://github.com/ingridstoc/Morse_Project.git
```
2. Create an environment in the terminal and activate it:
```
 .\venv\Scripts\activate
```
3. Install dependencies and libraries mentioned:

## Usage
1. Run the application:
```
python main.py
```
2. Choose the desired Morse code speed (words per minute).
   
3. Speak your message when prompted.

4. Provide a password for encrypting the Morse code audio.
The emitter will transmit the encrypted audio file to the receiver.
The receiver will decrypt and decode the Morse code back to text.

## Project Structure

+ **main.py**: The main script with emitter and receiver functionality.
  
+ **morse_code.wav**: The generated Morse code audio file.
  
+ **encrypted_morse.bin**: The encrypted Morse code audio file.
  
+ **decrypted_morse.wav**: The decrypted Morse code audio file.



