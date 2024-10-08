import streamlit as st
import speech_recognition as sr
import arabic_reshaper
from pydub import AudioSegment
import os

# Surah Al-Kausar text for comparison
SURAH_AL_KAUSAR = "ﺍﻧﺎ ﺍﻋﻄﻴﻨﺎﻙ ﺍﻟﻜﻮﺛﺮ ﻓﺼﻞ ﻟﺮﺑﻚ ﻭﺍﻧﺤﺮ ﺍﻥ ﺷﺎﻧﺌﻚ ﻫﻮ ﺍﻻﺑﺘﺮ"

# Function to transcribe audio from a file
def transcribe_audio(file_path):
    try:
        sound = AudioSegment.from_file(file_path)
        wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'
        sound.export(wav_file_path, format='wav')

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)
            transcribed_text = recognizer.recognize_google(audio_data, language='ar-SA')
        
        os.remove(wav_file_path)
        return transcribed_text
    except sr.UnknownValueError:
        return "خطأ: لم يتمكن النظام من التعرف على الكلام."
    except sr.RequestError as e:
        return f"خطأ في الاتصال بالخدمة: {e}"
    except Exception as e:
        return f"حدث خطأ: {str(e)}"

# Function to color the transcribed text
def color_transcribed_text(transcribed_text):
    reshaped_transcribed_text = arabic_reshaper.reshape(transcribed_text.strip())
    reshaped_surah_kasar = arabic_reshaper.reshape(SURAH_AL_KAUSAR.strip())
    
    # Splitting the transcribed text into words for comparison
    transcribed_words = reshaped_transcribed_text.split()
    surah_words = reshaped_surah_kasar.split()

    colored_text = ""
    for word in transcribed_words:
        if word in surah_words:
            colored_text += f"<span style='color:green;'>{word}</span> "
            surah_words.remove(word)  # Remove matched word to avoid duplication
        else:
            colored_text += f"<span style='color:red;'>{word}</span> "

    return colored_text.strip()

# Main application
def main():
    st.title("Quran Speech to Text Transcriber")

    # Add custom CSS for Arabic text styling
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');

            .arabic-text {
                font-family: 'Amiri', serif;
                font-size: 28px;
                direction: rtl;
                text-align: right;
                line-height: 1.6;
            }
        </style>
        """, unsafe_allow_html=True)

    # File upload for recitation
    uploaded_file = st.file_uploader("Upload your recitation file", type=["mp3", "wav", "flac", "ogg", "aac", "wma"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_audio_file", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Transcribe Recitation"):
            # Transcribe the uploaded audio file
            transcribed_text = transcribe_audio("temp_audio_file")

            if transcribed_text.startswith("خطأ"):
                st.markdown(f"<p class='arabic-text' style='color:red;'>{transcribed_text}</p>", unsafe_allow_html=True)
            else:
                # Color the transcribed text based on the match with Surah Al-Kausar
                colored_result = color_transcribed_text(transcribed_text)
                st.markdown(f"<p class='arabic-text'>{colored_result}</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
