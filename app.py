import streamlit as st
import replicate
import os
import tempfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.write("Sube tu mensaje semanal. La IA eliminará el ruido y mejorará tu voz.")

# --- GESTIÓN INTELIGENTE DEL TOKEN ---
# 1. Intentamos leer el secreto de la nube
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api = st.secrets["REPLICATE_API_TOKEN"]
else:
    replicate_api = None

# 2. Si NO estaba en los secretos, mostramos la caja en la barra lateral
with st.sidebar:
    if not replicate_api:
        st.warning("⚠️ Token no detectado en Secrets")
        replicate_api = st.text_input(
            "Pega tu Token aquí:", 
            type="password"
        )
    else:
        st.success("✅ Token cargado desde Secrets")
        
    st.divider()
    st.info("ℹ️ **Instrucciones:**\n1. Sube tu audio.\n2. Espera la magia.\n3. Descarga.")

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube tu grabación aquí", type=['mp3', 'wav', 'm4a'])

if audio_file is not None:
    st.audio(audio_file, format='audio/mp3')
    
    if st.button("✨ Limpiar y Mejorar Audio"):
        
        if not replicate_api:
            st.error("⛔ Falta el Token. Configúralo en los 'Secrets' o pégalo en la barra lateral.")
        else:
            # Configurar entorno
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            with st.spinner('⏳ Solidificando audio y enviando a la IA...'):
                try:
                    # --- GESTIÓN DE ARCHIVO TEMPORAL (Corrección del error de carga) ---
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Llamada al modelo
                    model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                    
                    output = replicate.run(
                        model_id,
                        input={
                            "input_audio": open(tmp_path, "rb"),
                            "denoise_flag": True,
                            "solver": "Midpoint",
                            "prior_temperature": 0.5
                        }
                    )
                    
                    # Limpieza del archivo temporal
                    os.unlink(tmp_path)
                    
                    st.success("¡Alquimia completada!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original**")
                        st.audio(audio_file)
                    with col2:
                        st.markdown("**Mejorado**")
                        st.audio(output)
                    
                    st.markdown(f'<a href="{output}" download="audio_pro.wav" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Descargar Audio</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Hubo un error técnico: {e}")
