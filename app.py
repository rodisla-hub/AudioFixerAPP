import streamlit as st
import replicate
import os
import tempfile # <--- Nueva herramienta para crear archivos temporales

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.write("Sube tu mensaje semanal. La IA eliminará el ruido y mejorará tu voz.")

# --- BARRA LATERAL CON TOKEN (SOLUCIÓN BYPASS) ---
with st.sidebar:
    st.header("🔑 Configuración")
    # Pedimos el token directamente para evitar el error de Secrets
    api_token_input = st.text_input(
        "Pega aquí tu Replicate API Token (r8_...)", 
        type="password",
        help="El código que empieza por r8_ que copiaste de la web de Replicate"
    )
    
    st.divider()
    st.info("ℹ️ **Instrucciones:**\n1. Pega tu Token arriba.\n2. Sube tu audio.\n3. Espera la magia.\n4. Descarga.")

# --- ÁREA PRINCIPAL ---
audio_file = st.file_uploader("Sube tu grabación aquí", type=['mp3', 'wav', 'm4a'])

if audio_file is not None:
    st.audio(audio_file, format='audio/mp3')
    
    if st.button("✨ Limpiar y Mejorar Audio (Modo Pro)"):
        
        # 1. Verificación del Token
        if not api_token_input or not api_token_input.startswith("r8_"):
            st.error("⚠️ Necesitas pegar un Token válido (que empiece por r8_) en la barra lateral.")
        
        else:
            # Configurar el entorno
            os.environ["REPLICATE_API_TOKEN"] = api_token_input
            
            with st.spinner('⏳ Solidificando audio y enviando a la IA... (Esto tarda unos segundos)'):
                try:
                    # --- PASO CRÍTICO NUEVO: GUARDAR EN DISCO TEMPORAL ---
                    # Creamos un archivo temporal para que Replicate pueda leerlo bien
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        tmp_file.write(audio_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Ahora enviamos el archivo físico (tmp_path)
                    model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                    
                    output = replicate.run(
                        model_id,
                        input={
                            "input_audio": open(tmp_path, "rb"), # Leemos desde el disco
                            "denoise_flag": True,
                            "solver": "Midpoint",
                            "prior_temperature": 0.5
                        }
                    )
                    
                    # Limpieza: Borramos el archivo temporal del servidor
                    os.unlink(tmp_path)
                    
                    # --- ÉXITO ---
                    st.success("¡Alquimia completada!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original**")
                        st.audio(audio_file)
                    with col2:
                        st.markdown("**Mejorado**")
                        st.audio(output)
                    
                    # Botón de descarga
                    st.markdown(f'<a href="{output}" download="audio_mejorado_pro.wav" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📥 Descargar Audio Limpio</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Hubo un error técnico: {e}")
