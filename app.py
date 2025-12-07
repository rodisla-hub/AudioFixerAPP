import streamlit as st
import replicate
import os
import tempfile
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")
st.title("🎙️ VoiceAlchemist")
st.markdown("Modelo: **Playmore Speech Enhancer**")

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
    
    if st.button("🚀 Procesar Audio"):
        if not replicate_api:
            st.error("⛔ Falta el Token.")
        else:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            with st.spinner('⏳ Procesando... (Casi listo)'):
                tmp_path = None
                try:
                    # 1. GUARDAR EN DISCO
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
                    
                    # --- CORRECCIÓN FINAL AQUÍ ---
                    # Convertimos el objeto FileOutput a string (URL) para que Streamlit lo entienda
                    output_url = str(output)
                    
                    # 3. ÉXITO
                    st.success("✅ ¡Funcionó!")
                    st.audio(output_url) # Usamos la URL extraída
                    st.markdown(f'<a href="{output_url}" download="audio_playmore.wav" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Descargar Audio</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"😓 Error Técnico: {str(e)}")
                
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
