import streamlit as st
import replicate
import os
import tempfile
import time
import requests
from pydub import AudioSegment
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")
st.title("🎙️ VoiceAlchemist")
st.markdown("Modelo: **Playmore Speech Enhancer (Salida MP3 Ligero)**")

# --- TOKEN ---
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api = st.secrets["REPLICATE_API_TOKEN"]
else:
    replicate_api = None

with st.sidebar:
    if not replicate_api:
        st.warning("⚠️ Falta Token")
        replicate_api = st.text_input("Token r8_...", type="password")
    else:
        st.success("✅ Token Conectado")

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube el audio", type=['mp3', 'wav', 'm4a', 'ogg'])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("🚀 Procesar y Convertir a MP3"):
        if not replicate_api:
            st.error("⛔ Falta el Token.")
        else:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            with st.spinner('⏳ Procesando audio en la nube...'):
                tmp_path = None
                mp3_path = None
                try:
                    # 1. PREPARAR ARCHIVO LOCAL
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_file.flush()
                        os.fsync(tmp_file.fileno())
                        tmp_path = tmp_file.name
                    
                    time.sleep(1)
                    
                    # 2. ENVIAR A REPLICATE
                    model_id = "playmore/speech-enhancer:bda37cf8cb38f5b677514933634a281b263a04225f7b2bf62c1c1b8748d21ae6"
                    
                    with open(tmp_path, "rb") as file_to_send:
                        output = replicate.run(
                            model_id,
                            input={"audio": file_to_send}
                        )
                    
                    output_url = str(output)
                    
                except Exception as e:
                    st.error(f"😓 Error en la IA: {str(e)}")
                    st.stop() # Paramos si falla aquí

            # --- FASE 2: COMPRESIÓN A MP3 ---
            with st.spinner('📦 Comprimiendo para WhatsApp (WAV -> MP3)...'):
                try:
                    # Descargamos el WAV pesado de la URL
                    response = requests.get(output_url)
                    audio_content = BytesIO(response.content)
                    
                    # Lo cargamos en el editor de audio
                    audio_segment = AudioSegment.from_file(audio_content)
                    
                    # Lo exportamos comprimido a MP3
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_mp3:
                        # 128k es calidad estándar de MP3 (poco peso, buen sonido)
                        audio_segment.export(tmp_mp3.name, format="mp3", bitrate="128k")
                        mp3_path = tmp_mp3.name
                    
                    # ÉXITO TOTAL
                    st.success("✅ ¡Listo! Audio optimizado para WhatsApp.")
                    
                    # Leemos el archivo MP3 para crear el botón de descarga
                    with open(mp3_path, "rb") as f:
                        mp3_bytes = f.read()
                    
                    st.audio(mp3_bytes, format='audio/mp3')
                    
                    st.download_button(
                        label="📥 Descargar MP3 (Ligero)",
                        data=mp3_bytes,
                        file_name="mensaje_limpio.mp3",
                        mime="audio/mpeg"
                    )

                except Exception as e:
                    st.error(f"😓 Error convirtiendo a MP3: {str(e)}")
                
                finally:
                    # Limpieza de todos los archivos temporales
                    if tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)
                    if mp3_path and os.path.exists(mp3_path): os.remove(mp3_path)
