import streamlit as st
import replicate
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")
st.title("🎙️ VoiceAlchemist")

# --- TOKEN ---
# Intentamos cogerlo de secrets, si no, lo pedimos (sin molestar si ya está)
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]
    token_status = "✅ Configurado"
else:
    token_status = "⚠️ Falta Token"

with st.sidebar:
    st.write(f"Estado del Sistema: {token_status}")
    if token_status == "⚠️ Falta Token":
        api_token = st.text_input("Pega tu Token r8_... aquí:", type="password")
        if api_token:
            os.environ["REPLICATE_API_TOKEN"] = api_token
            st.success("¡Token guardado!")

    st.divider()
    modo = st.radio(
        "Modo de Procesamiento:",
        ("🛡️ Limpieza (Quitar Ruido)", "✨ Estudio (Mejorar Voz)"),
        help="Usa 'Limpieza' si el audio es muy largo o falla."
    )

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube el audio (WhatsApp, MP3, M4A)", type=['mp3', 'wav', 'm4a', 'ogg'])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("🚀 Procesar Audio Ahora"):
        if "REPLICATE_API_TOKEN" not in os.environ:
            st.error("⛔ Falta el Token. Por favor ponlo en la barra lateral.")
        else:
            with st.spinner('⏳ Enviando datos a la nube... (Sin archivos temporales)'):
                try:
                    # ESTRATEGIA DIRECTA (RAM -> API)
                    # No guardamos nada en disco. Pasamos el objeto directo.
                    # Replicate necesita que el puntero esté al principio.
                    audio_file.seek(0)
                    
                    # Configuración del modelo (Hash fijo = No error 404)
                    model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                    
                    # Ajuste de temperatura según modo
                    temp = 0.1 if "Limpieza" in modo else 0.5
                    
                    output = replicate.run(
                        model_id,
                        input={
                            "input_audio": audio_file, # Enviamos el objeto de Streamlit directo
                            "denoise_flag": True,
                            "solver": "Midpoint",
                            "prior_temperature": temp,
                            "number_function_evaluations": 64
                        }
                    )
                    
                    # ÉXITO
                    st.success("✅ ¡Lo logramos!")
                    st.audio(output)
                    
                    # Botón de descarga
                    st.markdown(f'<a href="{output}" download="audio_final.wav" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Descargar Audio</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"😓 Error: {str(e)}")
                    st.warning("Si sigue fallando, prueba a convertir el audio a MP3 en tu PC antes de subirlo.")
