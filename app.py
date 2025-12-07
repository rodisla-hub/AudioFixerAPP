import streamlit as st
import replicate
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.markdown("Herramienta de limpieza de audio profesional para **mensajes semanales**.")

# --- GESTIÓN DEL SECRETO (INVISIBLE) ---
# Intentamos obtener el token de la "caja fuerte" de Streamlit
if "REPLICATE_API_TOKEN" in st.secrets:
    # Si existe, lo configuramos en silencio
    replicate_api = st.secrets["REPLICATE_API_TOKEN"]
    os.environ["REPLICATE_API_TOKEN"] = replicate_api
else:
    # Si no existe, mostramos un aviso solo para ti (el administrador)
    replicate_api = None
    st.error("⚙️ **Configuración Pendiente:** No se detectó el Token de IA.")
    st.info("Socio, ve a 'Settings > Secrets' en Streamlit Cloud y pega el token como acordamos.")

# --- INTERFAZ DE USUARIO ---
# Barra lateral simple solo con instrucciones
with st.sidebar:
    st.info("ℹ️ **Cómo usar:**\n1. Sube tu grabación.\n2. Pulsa el botón mágico.\n3. Espera unos segundos y descarga.")

# Área de subida
audio_file = st.file_uploader("Sube el archivo de audio (MP3, WAV, M4A)", type=['mp3', 'wav', 'm4a'])

if audio_file is not None:
    # Reproductor original
    st.subheader("1. Audio Original")
    st.audio(audio_file)
    
    # Botón de acción
    if st.button("✨ Limpiar y Mejorar Audio"):
        if not replicate_api:
            st.error("⛔ No puedo procesar el audio porque falta la configuración del Token.")
        else:
            with st.spinner('⏳ La IA está limpiando el ruido y ecualizando... (Esto tarda unos 30-60 segundos)'):
                try:
                    # Modelo Resemble Enhance (Estándar de calidad actual)
                    model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                    
                    output = replicate.run(
                        model_id,
                        input={
                            "input_audio": audio_file,
                            "denoise_flag": True,  # Elimina ruidos de fondo (ventiladores, etc.)
                            "solver": "Midpoint",  # Balance entre calidad y velocidad
                            "prior_temperature": 0.5
                        }
                    )
                    
                    # Resultado
                    st.success("✅ ¡Proceso completado con éxito!")
                    st.subheader("2. Audio Mejorado (Studio Quality)")
                    st.audio(output)
                    
                    # Botón de descarga visualmente atractivo
                    st.markdown(f'''
                        <a href="{output}" download="mensaje_limpio_pro.wav">
                            <button style="background-color: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                                📥 Descargar Audio Listo para Publicar
                            </button>
                        </a>
                    ''', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"😓 Hubo un error técnico inesperado: {str(e)}")
