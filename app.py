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
        ("🛡️ Limpieza Natural (VoiceFixer)", "✨ Reconstrucción IA (Resemble)"),
        help="VoiceFixer repara grabaciones viejas o ruidosas. Resemble intenta mejorar la calidad a estudio."
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
            
            msg_espera = '⏳ Buscando el modelo y procesando... (Esto tarda unos minutos)'
            
            with st.spinner(msg_espera):
                try:
                    # 1. Preparar archivo (Pasaporte)
                    file_extension = os.path.splitext(audio_file.name)[1]
                    if not file_extension: file_extension = ".mp3"
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    with open(tmp_path, "rb") as file_to_send:
                        
                        # --- LÓGICA DE BÚSQUEDA AUTOMÁTICA DE VERSIÓN ---
                        # Esto evita el Error 422 de "versión inválida"
                        
                        if "Natural" in modo:
                            # MOTOR 1: Voice Fixer (El Tractor Fiable)
                            # Buscamos la última versión disponible automáticamente
                            model = replicate.models.get("cjwbw/voice-fixer")
                            version = model.latest_version
                            
                            output = replicate.run(
                                f"{model.owner}/{model.name}:{version.id}",
                                input={
                                    "audio": file_to_send,
                                    "mode": "high_quality" # Modo específico de este modelo
                                }
                            )
                            
                        else:
                            # MOTOR 2: Resemble Enhance (El Ferrari)
                            model = replicate.models.get("resemble-ai/resemble-enhance")
                            version = model.latest_version
                            
                            output = replicate.run(
                                f"{model.owner}/{model.name}:{version.id}",
                                input={
                                    "input_audio": file_to_send,
                                    "denoise_flag": True,
                                    "solver": "Midpoint",
                                    "prior_temperature": 0.1, # Creatividad baja para evitar robots
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
                    st.info("Nota: Si el audio es muy largo (>3 min), intenta usar 'Limpieza Natural'.")
