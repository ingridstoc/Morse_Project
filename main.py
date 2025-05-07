import speech_recognition as sr
from threading import Thread
from time import sleep
import time
import socket
from gtts import gTTS # google text-to-speech library
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib # to hash password using SHA-256 pt a crea o cheie de criptare pe 256 de biti
from pydub import AudioSegment
import winsound # pt a reprezenta beeps (batai - puncte si linii) prin sistemul speaker de la windows
from pydub.generators import Sine # pt a genera tonuri sinus pt puncte si linii


def record_audio_to_text():
  r = sr.Recognizer() # Obiectul va fi folosit pt recunoasterea vocii
  while(1):
    try:
      with sr.Microphone() as source: # Pornirea microfonului
        r.adjust_for_ambient_noise(source, duration=0.2)
        audio = r.listen(source) # Asculta source(microfonul) si inregistreaza pana detecteaza liniste
        MyText = r.recognize_google(audio, language="ro-RO")
        print("Mesajul audio inregistrat este: ", MyText)
        return MyText
      
    except sr.RequestError as e:
        print("Eroare la request-uri; {0}".format(e))
    except sr.UnknownValueError:
        print("Nu se intelege mesajul audio")
  return 


def text_to_audio(text):
    tts = gTTS(text=text, lang='ro')
    tts.save("audio_message_from_morse.mp3")
    os.system("start audio_message_from_morse.mp3")  


def encrypt_wav_file(input_wav_path, output_encrypted_path, password):
    key = hashlib.sha256(password.encode()).digest() # obtine cheia de criptare pe 256 de biti pt algoritmul AES folosind SHA-256
    
    with open(input_wav_path, "rb") as f:
        data = f.read()
    
    initialization_vector = os.urandom(16) # genereaza random un initialization_vector pe 16 bytes pt a face un output random si a preveni patterns 
    cipher = Cipher(algorithms.AES(key), modes.CBC(initialization_vector), backend=default_backend()) # seteaza un cifru AES
    encryptor = cipher.encryptor() # obiect pt criptare
    padding_length = 16 - (len(data) % 16) # AES trebuie sa aiba lungimea input-ului multiplu de 16 bytes
    data += bytes([padding_length]) * padding_length
    encrypted_data = encryptor.update(data) + encryptor.finalize() # criptarea AES a datelor
    
    with open(output_encrypted_path, "wb") as f: # salvarea outuput-ului in forma binara
        f.write(initialization_vector + encrypted_data)
    print(f"Criptare completa in fisierul: {output_encrypted_path}")


def decrypt_wav_file(encrypted_path, output_wav_path, password):
    key = hashlib.sha256(password.encode()).digest()
    
    with open(encrypted_path, "rb") as f: # citirea fisierului cripitat
        initialization_vector = f.read(16)  # Primii 16 bytes sunt initialization_vector, restul sunt datele audio criptate
        encrypted_data = f.read()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(initialization_vector), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize() # decriptare
    padding_length = decrypted_data[-1] 
    decrypted_data = decrypted_data[:-padding_length]

    with open(output_wav_path, "wb") as f:
        f.write(decrypted_data)
    print(f"Decriptare completa in fisierul: {output_wav_path}")


def morse_audio_to_text(file_path, wpm=20):
    morse_code_dict = {
        "A": ".-", "Ă": ".-.-", "Â": ".-.-", "B": "-...", "C": "-.-.",
        "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
        "I": "..", "Î": "..-..", "J": ".---", "K": "-.-", "L": ".-..",
        "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-",
        "R": ".-.", "S": "...", "Ș": "----", "T": "-", "Ț": "--..-",
        "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..",
        "0": "-----", "1": ".----", "2": "..---", "3": "...--",
        "4": "....-", "5": ".....", "6": "-....", "7": "--...",
        "8": "---..", "9": "----.",
        ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--",
        ":": "---...", ";": "-.-.-.", "'": ".----.", "-": "-....-",
        "/": "-..-.", "(": "-.--.", ")": "-.--.-", "=": "-...-",
        "+": ".-.-.", "_": "..--.-", "\"": ".-..-.", "$": "...-..-",
        "&": ".-...", "@": ".--.-.", " ": "/"
    }
    reverse_dict = {v: k for k, v in morse_code_dict.items()} # Reverse pt decodare
    reverse_dict[".-.-"] = "Ă"

    unit = 1200 / wpm  # Formula pt a calcula in ms o unitate Morse(punctul)
    audio = AudioSegment.from_wav(file_path)
    threshold = 500  # Threshold pt a detecta daca un audio este sunet sau liniste
    duration = len(audio) # in ms
    size = 10  # marimea pt fiecare bucata care e scanata
    morse_code = ""

    i = 0
    while i < duration:
        chunk = audio[i:i+size]
        volume = chunk.max
        if volume > threshold: # daca volumul unei bucati depaseste threshold-ul, e sunet(punct sau linie)
            beep_length = 0
            while i < duration and audio[i:i+size].max > threshold:
                beep_length += size
                i += size
            if beep_length < unit * 2:
                morse_code += "."
            else:
                morse_code += "-"
        else:
            silence_length = 0
            while i < duration and audio[i:i+size].max <= threshold: # daca volumul este mai mic decat threshold => e liniste(pauza) 
                silence_length += size
                i += size
            if silence_length < unit * 2:  # Intre partile (pctele si liniile) de la aceeasi litera
                    pass
            elif unit * 2 <= silence_length < unit * 5:  # Intre litere e pauza
                morse_code += " "
            else:  # Intre cuvinte
                morse_code += "   "

    words = morse_code.strip().split("   ")  # Desparte codul in cuv cu cate 3 spatii pt a decoda fiecare cuv
    decoded_words = []

    for word in words:
        letters = word.strip().split(" ")  
        decoded_word = ''.join(reverse_dict.get(letter, "?") for letter in letters)
        decoded_words.append(decoded_word)

    final_text_decoded = ' '.join(decoded_words).replace("Â", "Ă")
    print("Codul Morse rezultat din mesajul audio:", morse_code.strip())
    print("Textul generat din forma scrisa a codului Morse:", final_text_decoded)
    return final_text_decoded


def text_to_morse_audio(message, wpm=20):
    morse_code_dict = {
        "A": ".-", "Ă": ".-.-", "Â": ".-.-", "B": "-...", "C": "-.-.",
        "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
        "I": "..", "Î": "..-..", "J": ".---", "K": "-.-", "L": ".-..",
        "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-",
        "R": ".-.", "S": "...", "Ș": "----", "T": "-", "Ț": "--..-",
        "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..",
        "0": "-----", "1": ".----", "2": "..---", "3": "...--",
        "4": "....-", "5": ".....", "6": "-....", "7": "--...",
        "8": "---..", "9": "----.",
        ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--",
        ":": "---...", ";": "-.-.-.", "'": ".----.", "-": "-....-",
        "/": "-..-.", "(": "-.--.", ")": "-.--.-", "=": "-...-",
        "+": ".-.-.", "_": "..--.-", "\"": ".-..-.", "$": "...-..-",
        "&": ".-...", "@": ".--.-.", " ": "/"
    }

    morse_message = " ".join(morse_code_dict[char] for char in message.upper()) # face fiecare caracter majuscul si dupa il transforma in Morse si dupa le leaga in cuv
    print("Codul Morse:", morse_message)
    reverse_dict = {v: k for k, v in morse_code_dict.items()}
    reverse_message = "".join(reverse_dict[code] if code in reverse_dict else "?" for code in morse_message.split(" "))
    print("Textul rezultat din acel cod Morse pentru verificare: ", reverse_message)

    unit = 1200 / wpm  
    dot = Sine(1000).to_audio_segment(duration=unit) # genereaza un semnal sinus la 1000Hz pt durata punctului si liniei
    dash = Sine(1000).to_audio_segment(duration=unit * 3)
    silence_short = AudioSegment.silent(duration=unit) # genereaza lungimi pt pauze(liniste) pt caracterele din litere
    silence_between_letters = AudioSegment.silent(duration=unit * 3) # intre litere
    silence_between_words = AudioSegment.silent(duration=unit * 7) # intre cuvinte
    morse_audio = AudioSegment.silent(duration=0) # incepe cu un audio gol

    for char in morse_message:
        if char == ".": # daca e punct, se aude un sunet scurt si se adauga la semnalul nostru audio pe care o sa-l returnam 
            winsound.Beep(1000, int(unit))
            morse_audio += dot + silence_short
        elif char == "-":
            winsound.Beep(1000, int(unit * 3))
            morse_audio += dash + silence_short
        elif char == " ":
            time.sleep(unit * 3 / 1000)
            morse_audio += silence_between_letters
        elif char == "/":
            time.sleep(unit * 7 / 1000)
            morse_audio += silence_between_words
        time.sleep(unit / 1000) # adaug un delay de o unitate intre toate simbolurile Morse

    morse_audio.export("morse_code.wav", format="wav")
    print("Semnalul audio Morse a fost salvat in morse_code.wav")
   

def emitator(wpm):
    e = socket.socket() # creare socket
    port = 12345
    e.bind(('', port))          
    e.listen(1) # punerea socket-ului in modul listening
    receptor_socket, _ = e.accept() # accepta conexiune de la receptor

    r = sr.Recognizer()
    message = record_audio_to_text()
    text_to_morse_audio(message, wpm=wpm)
    password_for_encryption = input("Introduceti o parola pentru a cripta fisierul audio Morse: ")
    encrypt_wav_file("morse_code.wav", "encrypted_morse.bin", password_for_encryption) # Cripteaza fisierul .wav intr-unul .bin
    with open("encrypted_morse.bin", "rb") as f: # Trimiterea fisierului catre receptor
        receptor_socket.sendfile(f)
    print("Trimiterea fisierului audio Morse criptat catre receptor a fost realizata cu succes!")
    receptor_socket.close()


def receptor(wpm):
    sleep(1)  # pt a avea un delay receptorul ca sa nu inceapa inaintea emitatorului
    r = socket.socket()  
    port = 12345
    r.connect(('127.0.0.1', port))  #localhost
   
    with open("received_encrypted_morse.bin", "wb") as f:  # primeste fisierul in bucati si il salveaza in .bin
        while True:
            chunk = r.recv(4096)
            if not chunk:
                break
            f.write(chunk)

    # Cere parola pt a decripta fisierul .bin in .wav
    password_for_decryption = input("Introduceti parola pentru a decripta fisierul audio Morse: ")
    decrypt_wav_file("received_encrypted_morse.bin", "decrypted_morse.wav", password_for_decryption)
    decoded_text = morse_audio_to_text("decrypted_morse.wav", wpm=wpm)
    text_to_audio(decoded_text)
    r.close() # inchide socket


if __name__ == "__main__":
    speed = input("Introduceti numarul aferent vitezei dorite pentru generarea semnalelor audio Morse (1 - incet, 2 - mediu, 3 - repede) [default: 2 - mediu]: ").strip()
    wpm_speed = {
        "1": 10,
        "2": 20,
        "3": 30
    }
    wpm = wpm_speed.get(speed, 20)
    print(f"Viteza selectata in format wpm (cuvinte pe minut): {wpm}")

    # Creeaza cele 2 thread-uri pt emitator si receptor
    thread_emitator = Thread(target = emitator, args=(wpm,))
    thread_receptor = Thread(target = receptor, args=(wpm,))

    thread_emitator.start()
    thread_receptor.start()

    # Asteapta ca ambele sa se termine
    thread_emitator.join()
    thread_receptor.join()