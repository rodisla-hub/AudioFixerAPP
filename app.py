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

if st.button("✨ Limpiar y Mejorar Audio (Modo Pro)"):
    if not st.secrets["REPLICATE_API_TOKEN"]:
        st.error("Falta configurar el API Token.")
    else:
        with st.spinner('⏳ Procesando con Resemble AI... (Esto puede tardar unos minutos)'):
            try:
                # Usamos el modelo 'resemble-enhance' que es el estándar actual
                # Versión específica para asegurar estabilidad
                model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                
                output = replicate.run(
                    model_id,
                    input={
                        "input_audio": audio_file,
                        "denoise_flag": True,  # ¡Clave! Activa la limpieza de ruido fuerte
                        "solver": "Midpoint",  # Algoritmo equilibrado calidad/velocidad
                        "prior_temperature": 0.5
                    }
                )
                
                # Resemble a veces devuelve una lista, tomamos el primer archivo
                # o el archivo directo dependiendo de la respuesta.
                # Generalmente devuelve un objeto o URI.
                
                st.success("¡Alquimia completada! Escucha la diferencia.")
                
                # Mostrar el audio original vs el nuevo
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Original**")
                    st.audio(audio_file)
                with col2:
                    st.markdown("**Mejorado (Studio Quality)**")
                    st.audio(output, format='audio/wav')
                
                # Link de descarga
                st.markdown(f'<a href="{output}" download="audio_pro_venezuela.wav" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Descargar Audio Limpio</a>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Hubo un error técnico: {e}")
