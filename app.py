import streamlit as st
import replicate
import os
import requests

# Configuración de la página
st.set_page_config(page_title="VoiceAlchemist", page_icon="🎙️")

st.title("🎙️ VoiceAlchemist")
st.write("Sube tu mensaje semanal. La IA eliminará el ruido y mejorará tu voz.")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("🔑 Configuración")
    st.markdown("Para que esto funcione, necesitas tu Token de Replicate.")
    # AQUÍ ESTÁ EL TRUCO: Pedimos el token directamente al usuario
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
    
    # Botón de acción
    if st.button("✨ Limpiar y Mejorar Audio (Modo Pro)"):
        
        # 1. Verificamos si el usuario puso el token en la caja
        if not api_token_input:
            st.error("⚠️ ¡Alto ahí! Necesitas pegar el API Token en la barra lateral izquierda para continuar.")
        
        # 2. Verificamos que el token parezca real (que empiece por r8_)
        elif not api_token_input.startswith("r8_"):
            st.error("⚠️ Ese token no parece válido. Debe empezar por 'r8_'. Revísalo.")
            
        else:
            # 3. Todo correcto, asignamos el token
            os.environ["REPLICATE_API_TOKEN"] = api_token_input
            
            with st.spinner('⏳ Procesando con Resemble AI... (Paciencia, la alquimia tarda unos segundos)'):
                try:
                    # Modelo actualizado según tu captura y documentación oficial
                    model_id = "resemble-ai/resemble-enhance:93266a7e7f5805fb79bcf213b1a4e0ef2e45aff3c06eefd96c59e850c87fd6a2"
                    
                    output = replicate.run(
                        model_id,
                        input={
                            "input_audio": audio_file,
                            "denoise_flag": True,  # Limpieza de ruido activada
                            "solver": "Midpoint",
                            "prior_temperature": 0.5
                        }
                    )
                    
                    st.success("¡Alquimia completada!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original**")
                        st.audio(audio_file)
                    with col2:
                        st.markdown("**Mejorado**")
                        st.audio(output) # Streamlit detecta el formato solo
                    
                    # Link de descarga
                    st.markdown(f'<a href="{output}" download="audio_mejorado.wav" style="background-color: #FF4B4B; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">📥 Descargar Audio Nuevo</a>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Hubo un error técnico: {e}")
