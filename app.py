import streamlit as st
import replicate
import os
import tempfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.markdown("Herramienta de limpieza de audio profesional.")

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
    st.header("🎛️ Panel de Control")
    
    # Selector de Modo
    modo = st.radio(
        "Elige el motor:",
        ("🛡️ Limpieza Natural (Denoising)", "✨ Reconstrucción IA (Resemble)"),
        help="Limpieza Natural quita ruido de fondo (fiable). Reconstrucción mejora la voz (puede tardar)."
    )

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube tu grabación", type=['mp3', 'wav', 'm4a', 'ogg'])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button(f"🚀 Procesar con {modo}"):
        
        if not replicate_api:
            st.error("⛔ Falta el Token.")
        else:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            with st.spinner('⏳ Procesando audio... (Esto puede tardar unos minutos)'):
                try:
                    # 1. Preparar archivo (Pasaporte)
                    file_extension = os.path.splitext(audio_file.name)[1]
                    if not file_extension: file_extension = ".mp3"
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    with open(tmp_path, "rb") as file_to_send:
                        
                        # --- LÓGICA BLINDADA ---
                        
                        if "Natural" in modo:
                            # MOTOR 1: Audio Denoising (Seguridad Máxima)
                            # Usamos el hash directo porque este modelo es muy estable y no cambia.
                            # Esto EVITA el Error 404 de modelos borrados.
                            model_id = "grand-challenge/audio-denoising:4f9c1788753238a2e4a6d05f3192451f8a845945c796790928e442834d9a24d7"
                            
                            output = replicate.run(
                                model_id,
                                input={"audio": file_to_send}
                            )
                            
                        else:
                            # MOTOR 2: Resemble Enhance (Calidad Estudio)
                            # Aquí sí buscamos la última versión para evitar el Error 422
                            try:
                                model = replicate.models.get("resemble-ai/resemble-enhance")
                                version = model.latest_version
                                model_id_dynamic = f"{model.owner}/{model.name}:{version.id}"
                            except:
                                # Si falla la búsqueda, usamos el último hash conocido como respaldo
                                model_id_dynamic = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                            
                            output = replicate.run(
                                model_id_dynamic,
                                input={
                                    "input_audio": file_to_send,
                                    "denoise_flag": True,
                                    "solver": "Midpoint",
                                    "prior_temperature": 0.1, # Creatividad baja
                                    "number_function_evaluations": 64
                                }
                            )
                    
                    # Limpieza
                    os.remove(tmp_path)
                    
                    st.success("✅ ¡Proceso completado!")
                    st.subheader("Resultado Final")
                    st.audio(output)
                    
                    st.markdown(f'<a href="{output}" download="audio_limpio.wav" style="background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: bold;">📥 Descargar Audio</a>', unsafe_allow_html=True)

                except Exception as e:
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.remove(tmp_path)
                    st.error(f"😓 Error Técnico: {str(e)}")
