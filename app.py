import streamlit as st
import replicate
import os
import tempfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.markdown("Herramienta de limpieza de audio profesional.")

# --- GESTIÓN DEL TOKEN (Híbrida) ---
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
    st.header("🎛️ Panel de Control")
    
    # SELECTOR DE MODO
    modo = st.radio(
        "Elige el motor:",
        ("🛡️ Limpieza Natural (Recomendado)", "✨ Reconstrucción IA (Estudio)"),
        help="La limpieza natural quita el ruido sin cambiar la voz. La reconstrucción intenta mejorar la calidad pero tarda más."
    )

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube tu grabación (WhatsApp, MP3, M4A)", type=['mp3', 'wav', 'm4a', 'ogg'])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button(f"🚀 Procesar con {modo}"):
        
        if not replicate_api:
            st.error("⛔ Falta el Token.")
        else:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            # Mensaje personalizado según el modo
            msg_espera = '⏳ Limpiando ruido... (Rápido)' if "Natural" in modo else '⏳ Reconstruyendo voz con IA... (Esto puede tardar 2-3 min)'
            
            with st.spinner(msg_espera):
                try:
                    # 1. Preparar archivo (El Pasaporte)
                    file_extension = os.path.splitext(audio_file.name)[1]
                    if not file_extension: file_extension = ".mp3"
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    with open(tmp_path, "rb") as file_to_send:
                        
                        # --- LÓGICA DE MOTORES ---
                        
                        if "Natural" in modo:
                            # MOTOR 1: TRACTOR (Fiable y Natural)
                            # Usamos un modelo específico solo para quitar ruido.
                            # Es rápido y no robotiza la voz.
                            model_id = "grand-challenge/audio-denoising:4f9c1788753238a2e4a6d05f3192451f8a845945c796790928e442834d9a24d7"
                            output = replicate.run(model_id, input={"audio": file_to_send})
                            
                        else:
                            # MOTOR 2: FERRARI DOMADO (Resemble Enhance Ajustado)
                            model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                            
                            output = replicate.run(
                                model_id,
                                input={
                                    "input_audio": file_to_send,
                                    "denoise_flag": True,
                                    "solver": "Midpoint",
                                    # AQUÍ ESTÁ EL TRUCO: Bajamos la temperatura de 0.5 a 0.1
                                    # Esto elimina el efecto robot.
                                    "prior_temperature": 0.1, 
                                    "number_function_evaluations": 64
                                }
                            )
                    
                    # Limpieza
                    os.remove(tmp_path)
                    
                    st.success("✅ ¡Proceso completado!")
                    
                    # Mostrar resultado
                    st.subheader("Resultado Final")
                    st.audio(output)
                    
                    st.markdown(f'<a href="{output}" download="mensaje_procesado.wav" style="background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: bold;">📥 Descargar Audio</a>', unsafe_allow_html=True)

                except Exception as e:
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.remove(tmp_path)
                    st.error(f"😓 Ocurrió un error (posiblemente por tiempo de espera): {str(e)}")
                    if "Natural" not in modo:
                        st.info("💡 Consejo: Intenta usar el modo 'Limpieza Natural', es mucho más rápido y estable con audios largos.")
