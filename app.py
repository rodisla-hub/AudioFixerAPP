import streamlit as st
import replicate
import os
import tempfile
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")
st.title("🎙️ VoiceAlchemist")
st.markdown("Modelo: **Playmore Speech Enhancer** (Salida Calidad Estudio WAV)")

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
    
    st.info("ℹ️ El archivo resultante será .WAV (Alta Calidad). Si pesa mucho para WhatsApp, envíalo como 'Documento'.")

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube el audio", type=['mp3', 'wav', 'm4a', 'ogg'])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("🚀 Procesar Audio"):
        if not replicate_api:
            st.error("⛔ Falta el Token.")
        else:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            with st.spinner('⏳ Procesando... (Esto funciona, prometido)'):
                tmp_path = None
                try:
                    # 1. GUARDAR EN DISCO (Modo Seguro)
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
                    
                    # Convertir salida a texto
                    output_url = str(output)
                    
                    # 3. ÉXITO
                    st.success("✅ ¡Audio Restaurado!")
                    st.audio(output_url)
                    
                    # Botón de descarga
                    st.markdown(f'<a href="{output_url}" download="mensaje_restaurado.wav" style="background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">📥 Descargar Audio (WAV)</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"😓 Error Técnico: {str(e)}")
                
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
