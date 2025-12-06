import streamlit as st
import replicate
import os
import requests
from io import BytesIO

# Configuración de la página (Toque Nexo)
st.set_page_config(page_title="VoiceAlchemist - Limpiador de Audio", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.write("Sube tu mensaje semanal. La IA eliminará el ruido y mejorará tu voz.")

# Sidebar para instrucciones (Pensando en el usuario no técnico)
with st.sidebar:
    st.info("ℹ️ **Instrucciones:**\n1. Sube tu archivo (MP3 o WAV).\n2. Espera a que la barra termine.\n3. Descarga tu audio limpio.")
    st.warning("⚠️ Paciencia: Si el internet es lento, la subida puede tardar unos segundos.")

# Input de Token (Oculto en variables de entorno en producción)
# Para pruebas locales puedes descomentar esto, pero en prod usa st.secrets
# api_token = st.text_input("Replicate API Token", type="password")
# os.environ["REPLICATE_API_TOKEN"] = api_token

# Carga del archivo
audio_file = st.file_uploader("Sube tu grabación aquí", type=['mp3', 'wav', 'm4a'])

if audio_file is not None:
    st.audio(audio_file, format='audio/mp3')
    
    if st.button("✨ Limpiar y Mejorar Audio"):
        if not st.secrets["REPLICATE_API_TOKEN"]:
            st.error("Falta configurar el API Token.")
        else:
            with st.spinner('⏳ Procesando... La Alquimia está ocurriendo...'):
                try:
                    # Usamos un modelo de restauración de audio robusto en Replicate
                    # Ejemplo: 'meronym/speaker-transcription' o modelos de 'voice-fixer'
                    # Aquí usamos uno genérico de speech enhancement
                    model = replicate.models.get("grand-challenge/audio-denoising")
                    # Nota: Hay modelos mejores como 'voice-fixer', hay que buscar el ID actual en Replicate
                    
                    # Como replicate a veces pide URLs o paths, para Streamlit es mejor
                    # usar el cliente SDK directo si soporta buffers, o guardar temporalmente.
                    
                    # Opción robusta para Replicate:
                    output = replicate.run(
                        "grand-challenge/audio-denoising:...", # Insertar hash del modelo específico
                        input={"audio": audio_file}
                    )
                    
                    st.success("¡Listo! Tu audio ha sido transformado.")
                    st.audio(output, format='audio/wav')
                    
                    # Botón de descarga manual (hack para descargar desde URL)
                    st.markdown(f'<a href="{output}" download="mensaje_limpio.wav" target="_blank">📥 Descargar Audio Limpio</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Hubo un error en el proceso: {e}")