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

# --- BLOQUE DE CÓDIGO CORREGIDO Y BLINDADO ---

# Recuperamos el token de forma segura. Si no existe, devuelve None (no falla).
replicate_token = st.secrets.get("REPLICATE_API_TOKEN")

if st.button("✨ Limpiar y Mejorar Audio (Modo Pro)"):
    if not replicate_token:
        st.error("⛔ Error: No he encontrado la llave 'REPLICATE_API_TOKEN' en los Secrets.")
        st.info("Por favor, ve a Settings -> Secrets y asegúrate de que el nombre sea exacto.")
    else:
        # Configurar la variable de entorno para que Replicate la lea automáticamente
        os.environ["REPLICATE_API_TOKEN"] = replicate_token
        
        with st.spinner('⏳ Procesando con Resemble AI... (Esto puede tardar unos minutos)'):
            try:
                # Tu código del modelo sigue aquí igual...
                model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                
                output = replicate.run(
                    model_id,
                    input={
                        "input_audio": audio_file,
                        "denoise_flag": True,
                        "solver": "Midpoint",
                        "prior_temperature": 0.5
                    }
                )
                
                # ... (resto del código de éxito igual)
                st.success("¡Alquimia completada! Escucha la diferencia.")
                # ... (mostrar audios)

            except Exception as e:
                st.error(f"Hubo un error técnico: {e}")
