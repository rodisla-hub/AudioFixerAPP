import streamlit as st
import replicate
import os
import tempfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.markdown("Herramienta de limpieza de audio.")

# --- GESTIÓN DEL TOKEN ---
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api = st.secrets["REPLICATE_API_TOKEN"]
else:
    replicate_api = None

with st.sidebar:
    if not replicate_api:
        st.warning("⚠️ Token no detectado")
        replicate_api = st.text_input("Pega tu Token aquí:", type="password")
    else:
        st.success("✅ Sistema conectado")
    
    st.divider()
    
    # --- SELECTOR DE MODO ---
    modo = st.radio(
        "Elige el resultado:",
        ("🛡️ Solo Limpiar (Natural)", "✨ Mejorar Voz (IA Estudio)"),
        help="'Solo Limpiar' quita el ruido. 'Mejorar Voz' intenta reconstruir la calidad."
    )

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube tu grabación", type=['mp3', 'wav', 'm4a', 'ogg'])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button(f"🚀 Procesar Audio"):
        
        if not replicate_api:
            st.error("⛔ Falta el Token.")
        else:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            with st.spinner('⏳ Trabajando en el audio...'):
                try:
                    # 1. PASAPORTE DE ARCHIVO (Crear temporal)
                    file_extension = os.path.splitext(audio_file.name)[1]
                    if not file_extension: file_extension = ".mp3"
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # 2. SELECCIÓN DE MODELO (HASHES FIJOS - NO CAMBIAR)
                    with open(tmp_path, "rb") as file_to_send:
                        
                        if "Natural" in modo:
                            # MODELO A: Audio Denoising (El fiable)
                            # Este hash es eterno, no da error 404.
                            model_id = "grand-challenge/audio-denoising:4f9c1788753238a2e4a6d05f3192451f8a845945c796790928e442834d9a24d7"
                            output = replicate.run(model_id, input={"audio": file_to_send})
                            
                        else:
                            # MODELO B: Resemble Enhance (El potente)
                            # Hash exacto sacado de tu captura de pantalla del Playground
                            model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                            
                            output = replicate.run(
                                model_id,
                                input={
                                    "input_audio": file_to_send,
                                    "denoise_flag": True,
                                    "solver": "Midpoint",
                                    "prior_temperature": 0.1, # Temperatura baja para que no suene robot
                                }
                            )
                    
                    # 3. LIMPIEZA Y RESULTADO
                    os.remove(tmp_path)
                    
                    st.success("✅ ¡Hecho!")
                    st.audio(output)
                    st.markdown(f'<a href="{output}" download="audio_final.wav" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Descargar</a>', unsafe_allow_html=True)

                except Exception as e:
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.remove(tmp_path)
                    st.error(f"😓 Error: {str(e)}")
