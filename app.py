import streamlit as st
import replicate
import os
import tempfile
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")
st.title("🎙️ VoiceAlchemist")
st.markdown("Sube tu audio. La IA se encarga del resto.")

# --- TOKEN (Tu llave maestra única) ---
if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api = st.secrets["REPLICATE_API_TOKEN"]
else:
    replicate_api = None

with st.sidebar:
    if not replicate_api:
        st.warning("⚠️ Falta el Token")
        replicate_api = st.text_input("Pega tu Token aquí:", type="password")
    else:
        st.success("✅ Token Conectado") # Un solo token para todo
    
    st.divider()
    
    # Usamos el MISMO modelo para todo, solo cambiamos la intensidad
    modo = st.radio(
        "¿Qué necesitas?",
        ("🛡️ Solo Limpiar Ruido", "✨ Mejorar Calidad de Voz"),
        help="'Solo Limpiar' es más rápido y natural. 'Mejorar' reconstruye la voz."
    )

# --- PROCESO ---
audio_file = st.file_uploader("Sube tu grabación", type=['mp3', 'wav', 'm4a', 'ogg'])

if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("🚀 Iniciar Alquimia"):
        if not replicate_api:
            st.error("⛔ Necesitas el Token para pagar a la IA.")
        else:
            os.environ["REPLICATE_API_TOKEN"] = replicate_api
            
            with st.spinner('⏳ Procesando... (Esto tarda un poco, no cierres la pestaña)'):
                tmp_path = None
                try:
                    # 1. GUARDADO ROBUSTO DEL ARCHIVO
                    # Forzamos extensión .mp3 para que Replicate no se confunda
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_file.flush() # Aseguramos que todo se escriba en disco
                        tmp_path = tmp_file.name
                    
                    # Esperamos un instante para liberar el archivo del sistema
                    time.sleep(0.5)
                    
                    # 2. CONFIGURACIÓN DEL MODELO
                    # Usamos el hash exacto que funcionó en tu Playground
                    model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                    
                    # Ajustamos la "fuerza" según lo que elija tu amigo
                    if "Limpiar" in modo:
                        temp = 0.1  # Baja creatividad = Solo limpia
                    else:
                        temp = 0.5  # Alta creatividad = Mejora voz
                    
                    # 3. ENVÍO A LA NUBE
                    with open(tmp_path, "rb") as file_to_send:
                        output = replicate.run(
                            model_id,
                            input={
                                "input_audio": file_to_send,
                                "denoise_flag": True,
                                "solver": "Midpoint",
                                "prior_temperature": temp,
                                "number_function_evaluations": 64
                            }
                        )
                    
                    # 4. ÉXITO
                    st.success("✅ ¡Audio transformado!")
                    st.audio(output)
                    st.markdown(f'<a href="{output}" download="audio_final.wav" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Descargar Audio</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"😓 Error Técnico: {str(e)}")
                    st.info("Intenta subir el audio en formato MP3 si sigue fallando.")
                
                finally:
                    # Borramos el archivo temporal para no dejar basura
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
