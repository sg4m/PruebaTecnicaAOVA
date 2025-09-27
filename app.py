import streamlit as st
import sys
import os
import time
import json
from datetime import datetime
from typing import Optional

# Agregar el directorio src al path para importar nuestros módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import Config
from src.ai.gemini_client import GeminiClient
from src.ai.context_manager import ContextManager, MessageType
from src.audio.speech_to_text import SpeechToText
from src.audio.text_to_speech import TextToSpeech
from src.database.supabase_client import SupabaseClient
# from streamlit_audiorecorder import audiorecorder  # Comentado temporalmente

def inicializar_sesion():
    """Inicializar variables de sesión de Streamlit"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Lead info functionality removed for simplification
    
    # Inicializar cliente de Gemini
    if 'gemini_client' not in st.session_state:
        try:
            st.session_state.gemini_client = GeminiClient()
        except Exception as e:
            st.error(f"Error inicializando Gemini: {e}")
            st.session_state.gemini_client = None
    
    # Inicializar cliente de Speech-to-Text
    if 'speech_to_text' not in st.session_state:
        try:
            st.session_state.speech_to_text = SpeechToText()
        except Exception as e:
            st.error(f"Error inicializando Speech-to-Text: {e}")
            st.session_state.speech_to_text = None
    
    # Inicializar cliente de Text-to-Speech
    if 'text_to_speech' not in st.session_state:
        try:
            st.session_state.text_to_speech = TextToSpeech()
        except Exception as e:
            st.error(f"Error inicializando Text-to-Speech: {e}")
            st.session_state.text_to_speech = None
    
    # Inicializar cliente de base de datos
    if 'db_client' not in st.session_state:
        try:
            st.session_state.db_client = SupabaseClient()
            # Probar conexión
            if st.session_state.db_client.test_connection():
                st.session_state.db_connected = True
            else:
                st.session_state.db_connected = False
                st.session_state.db_client = None
        except Exception as e:
            st.warning(f"Base de datos no disponible: {e}")
            st.session_state.db_client = None
            st.session_state.db_connected = False
    
    # Inicializar Context Manager
    if 'context_manager' not in st.session_state:
        try:
            # Pasar cliente de BD al Context Manager
            st.session_state.context_manager = ContextManager(
                db_client=st.session_state.db_client if st.session_state.get('db_connected') else None
            )
            # Iniciar nueva conversación si no existe
            if not hasattr(st.session_state, 'current_session_id'):
                session_id = st.session_state.context_manager.start_new_conversation()
                st.session_state.current_session_id = session_id
                print(f"Nueva conversación iniciada: {session_id}")
        except Exception as e:
            st.error(f"Error inicializando Context Manager: {e}")
            st.session_state.context_manager = None

def guardar_conversacion_completa() -> Optional[str]:
    """
    Guardar la conversación completa en la base de datos, incluyendo 
    tanto la tabla de conversaciones como mensajes individuales
    
    Returns:
        ID de la conversación guardada o None si hay error
    """
    try:
        if not st.session_state.context_manager or not st.session_state.db_client:
            return None
        
        # 1. Guardar conversación principal usando Context Manager
        conversation_id = st.session_state.context_manager.save_conversation_to_db()
        
        if not conversation_id:
            print("Error: No se pudo guardar la conversación principal")
            return None
        
        # 2. Guardar mensajes individuales en la tabla messages
        messages_saved = 0
        for i, message in enumerate(st.session_state.conversation_history):
            try:
                # Preparar datos del mensaje según el esquema
                message_data = {
                    'conversation_id': conversation_id,
                    'message_type': message['role'],  # 'user' o 'assistant'
                    'content': message['content'],
                    'audio_duration': message.get('audio_duration'),
                    'intent': message.get('intent'),
                    'sentiment': message.get('sentiment'),
                    'confidence_score': message.get('confidence_score'),
                    'extracted_info': json.dumps(message.get('extracted_info', {})) if message.get('extracted_info') else None,
                    'timestamp': datetime.fromtimestamp(message.get('timestamp', time.time())).isoformat(),
                    'processing_time_ms': message.get('processing_time_ms')
                }
                
                # Limpiar valores None para la inserción
                clean_message_data = {k: v for k, v in message_data.items() if v is not None}
                
                # Insertar mensaje en BD
                result = st.session_state.db_client.supabase.table('messages').insert(clean_message_data).execute()
                
                if result.data:
                    messages_saved += 1
                else:
                    print(f"Warning: No se pudo guardar el mensaje {i}")
                    
            except Exception as e:
                print(f"Error guardando mensaje {i}: {e}")
                continue
        
        print(f"Conversación guardada: {conversation_id}")
        print(f"Mensajes guardados: {messages_saved}/{len(st.session_state.conversation_history)}")
        
        return conversation_id
        
    except Exception as e:
        print(f"Error guardando conversación completa: {e}")
        return None

def mostrar_sidebar():
    """Mostrar la barra lateral con configuraciones y estado"""
    with st.sidebar:
        st.header("Configuración")
        
        # Verificar configuración
        try:
            Config.validate_config()
            st.success("Configuración válida")
            config_ok = True
        except ValueError as e:
            st.error(f"Error en configuración: {e}")
            config_ok = False
        
        # Estado de la base de datos
        st.markdown("Estado de la Base de Datos")
        if st.session_state.get('db_connected', False):
            st.success("Conectado a Supabase")
            
            # Mostrar estadísticas básicas
            if st.session_state.db_client:
                try:
                    stats = st.session_state.db_client.get_database_stats()
                    if stats:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Leads", stats.get('total_leads', 0))
                        with col2:
                            st.metric("Conversaciones", stats.get('total_conversations', 0))
                        with col3:
                            st.metric("Alta Calidad", stats.get('high_quality_leads', 0))
                except Exception as e:
                    st.error(f"Error obteniendo stats: {e}")
            
            # Sección de gestión de conversaciones
            st.markdown("Gestión de Conversaciones")
            
            # Información de la conversación actual
            if st.session_state.context_manager and st.session_state.context_manager.current_context:
                ctx = st.session_state.context_manager.current_context
                st.info(f"**Sesión:** {ctx.session_id[:8]}... ({len(ctx.messages)} mensajes)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Botón para guardar conversación completa
                    if st.button("Guardar", help="Guarda toda la conversación en la BD"):
                        if st.session_state.context_manager and len(st.session_state.conversation_history) > 0:
                            with st.spinner("Guardando conversación..."):
                                result = guardar_conversacion_completa()
                                if result:
                                    st.success(f"Guardada (ID: {result[:8]}...)")
                                else:
                                    st.error("Error guardando")
                        else:
                            st.warning("No hay conversación para guardar")
                
                with col2:
                    # Espacio para futuras funcionalidades
                    st.write("")
            else:
                st.info("Inicia una conversación para habilitar guardado")
        else:
            st.warning("Base de datos no disponible")
            st.caption("La aplicación funciona sin BD")
        
        # Estado del agente
        st.markdown("Estado del Agente")
        if (st.session_state.gemini_client and 
            st.session_state.speech_to_text and 
            st.session_state.text_to_speech):
            st.success("Agente Funcionando")
            st.caption("IA, STT y TTS funcionando")
        else:
            st.error("Agente con Problemas")
            if not st.session_state.gemini_client:
                st.caption("Error en cliente IA")
            if not st.session_state.speech_to_text:
                st.caption("Error en Speech-to-Text")
            if not st.session_state.text_to_speech:
                st.caption("Error en Text-to-Speech")
        
        # Estado del Context Manager  
        st.markdown("Contexto Inteligente")
        if st.session_state.context_manager and st.session_state.context_manager.current_context:
            ctx = st.session_state.context_manager.current_context
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Fase", ctx.current_phase.value.title())
                st.metric("Interacciones", ctx.total_interactions)
            
            with col2:
                duration_min = int((time.time() - ctx.start_time) / 60)
                st.metric("Duración", f"{duration_min} min")
                st.metric("Mensajes", len(ctx.messages))
            
            # Mostrar insights si hay
            insights = st.session_state.context_manager._generate_conversation_insights()
            if insights.get('engagement_level'):
                engagement_color = {"high": "🟢", "medium": "🟡", "low": "🔴"}
                level = insights['engagement_level']
                st.write(f"**Engagement:** {engagement_color.get(level, '⚪')} {level.title()}")
        
        # Estado del sistema TTS
        st.markdown("Estado de Voz")
        if st.session_state.text_to_speech:
            tts_status = st.session_state.text_to_speech.get_tts_status()
            st.info(tts_status["message"])
            
            # Mostrar información sobre pyttsx3
            if tts_status["pyttsx3"]:
                st.success("Sistema de voz básico activo")
            else:
                st.warning("Sistema de voz no disponible")
        
        # Estadísticas
        st.markdown("Estadísticas de Sesión")
        total_mensajes = len(st.session_state.conversation_history)
        mensajes_usuario = len([m for m in st.session_state.conversation_history if m['role'] == 'user'])
        mensajes_agente = len([m for m in st.session_state.conversation_history if m['role'] == 'assistant'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", total_mensajes)
            st.metric("Usuario", mensajes_usuario)
        with col2:
            st.metric("Agente", mensajes_agente)
            st.metric("Sesiones", 1)
        
        # Configuraciones de voz
        st.markdown("Configuración de Voz")
        if st.session_state.text_to_speech and st.session_state.text_to_speech.is_available():
            st.success("TTS Disponible")
            
            # Toggle para reproducción automática
            auto_speak = st.checkbox(
                "Reproducir automáticamente", 
                value=st.session_state.get('auto_speak', False),
                help="Reproduce las respuestas del agente automáticamente"
            )
            st.session_state.auto_speak = auto_speak
            
            # Mostrar voces disponibles
            voices = st.session_state.text_to_speech.get_available_voices()
            if voices:
                st.info(f"Voces disponibles: {len(voices)}")
        else:
            st.warning("TTS no disponible")
        
        # Botones de control
        st.markdown("Controles generales: ")
        if st.button("Limpiar Chat", help="Eliminar todo el historial"):
            st.session_state.conversation_history = []
            st.success("Chat limpiado")
            time.sleep(1)
            st.rerun()
        
        return config_ok

def mostrar_conversacion():
    """Mostrar el historial de conversación"""
    st.header("Conversación con el Agente")
    
    # Contenedor del chat
    chat_container = st.container()
    with chat_container:
        if st.session_state.conversation_history:
            for i, message in enumerate(st.session_state.conversation_history):
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(f"**Usuario:** {message['content']}")
                else:
                    with st.chat_message("assistant"):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**Agente IA:** {message['content']}")
                        with col2:
                            if st.button("🔊", key=f"speak_{i}", help="Reproducir respuesta"):
                                if st.session_state.text_to_speech and st.session_state.text_to_speech.is_available():
                                    with st.spinner("Reproduciendo..."):
                                        success = st.session_state.text_to_speech.speak_text(message['content'])
                                        if not success:
                                            st.error("Error reproduciendo audio")
                                else:
                                    st.error("TTS no disponible")
        else:
            st.info("¡Hola! Soy tu agente de IA especializado en lead generation. Puedes comunicarte conmigo escribiendo un mensaje o subiendo un archivo de audio.")
            st.markdown("""
            **¿Qué puedo hacer por ti?**
            -Responder preguntas sobre productos/servicios
            -Recopilar información sobre tus necesidades
            -Ayudarte a encontrar la solución perfecta
            -Analizar tu perfil como prospecto
            """)

def procesar_mensaje(contenido, tipo="texto"): # type: ignore
    """Procesar mensaje del usuario y generar respuesta usando Gemini con contexto inteligente"""
    
    # Agregar mensaje del usuario al historial tradicional (para compatibilidad)
    st.session_state.conversation_history.append({
        'role': 'user',
        'content': contenido,
        'tipo': tipo,
        'timestamp': time.time()
    })
    
    # Agregar mensaje al Context Manager
    if st.session_state.context_manager:
        message_type = MessageType.USER_AUDIO if tipo == "audio" else MessageType.USER_TEXT
        st.session_state.context_manager.add_message('user', contenido, message_type)
        
        # Analizar y actualizar fase de conversación
        st.session_state.context_manager.analyze_conversation_phase()
        st.session_state.context_manager.update_conversation_summary()
    
    # Verificar si Gemini está disponible
    if st.session_state.gemini_client is None:
        respuesta = "Lo siento, hay un problema con la conexión a Gemini. Por favor verifica tu configuración."
    else:
        try:
            # Generar respuesta usando Gemini con contexto inteligente
            respuesta = st.session_state.gemini_client.generate_response(
                contenido,
                context=st.session_state.conversation_history[:-1],  # Fallback
                context_manager=st.session_state.context_manager  # Contexto inteligente
            )
            
            # Lead extraction functionality removed for simplification
            
        except Exception as e:
            print(f"Error procesando con Gemini: {e}")
            respuesta = "Disculpa, tuve un problema técnico. ¿Podrías repetir tu mensaje?"
    
    # Agregar respuesta del agente al historial tradicional
    st.session_state.conversation_history.append({
        'role': 'assistant', 
        'content': respuesta,
        'timestamp': time.time()
    })
    
    # Agregar respuesta al Context Manager
    if st.session_state.context_manager:
        st.session_state.context_manager.add_message('assistant', respuesta, MessageType.AGENT_RESPONSE)
    
    # Reproducir respuesta automáticamente (opcional)
    if st.session_state.get('auto_speak', False) and st.session_state.text_to_speech:
        try:
            st.session_state.text_to_speech.speak_text(respuesta)
        except Exception as e:
            print(f"Error reproduciendo respuesta automática: {e}")

def mostrar_controles_input():
    """Mostrar controles para enviar mensajes"""
    st.header("Envía tu Mensaje")
    
    # Pestañas para diferentes tipos de input
    tab1, tab2 = st.tabs(["Texto", "Audio"])
    
    with tab1:
        st.markdown("### Escribe tu mensaje")
        texto_input = st.text_area(
            "¿En qué puedo ayudarte hoy?",
            placeholder="Ejemplo: Hola, me interesa conocer sus servicios de marketing digital...",
            height=100
        )
        
        if st.button("Enviar Mensaje", type="primary", key="enviar_texto"):
            if texto_input.strip():
                with st.spinner("Procesando mensaje..."):
                    procesar_mensaje(texto_input.strip(), "texto")
                    st.success("Mensaje enviado")
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.warning("Por favor escribe un mensaje.")
    
    with tab2:
        # Sub-pestañas para diferentes tipos de audio
        audio_tab1, audio_tab2 = st.tabs(["Subir Audio", "Grabar Audio"])
        
        with audio_tab1:
            st.markdown("### Sube un archivo de audio")
            st.info("**Recomendación**: Usa archivos WAV para mejor compatibilidad. Para MP3/M4A necesitas FFmpeg instalado.")
            
            uploaded_audio = st.file_uploader(
                "Selecciona un archivo de audio",
                type=['wav', 'mp3', 'ogg', 'm4a'],
                help="Formatos soportados: WAV (recomendado), MP3, OGG, M4A"
            )
        
        if uploaded_audio is not None:
            st.audio(uploaded_audio, format=uploaded_audio.type)
            st.success(f"Archivo cargado: {uploaded_audio.name}")
            
            if st.button("Procesar Audio", type="primary", key="procesar_audio"):
                if st.session_state.speech_to_text is None:
                    st.error("Sistema de transcripción no disponible")
                else:
                    with st.spinner("Transcribiendo audio..."):
                        # Transcribir audio real
                        texto_transcrito = st.session_state.speech_to_text.transcribe_audio_file(uploaded_audio)
                        
                        if texto_transcrito and not texto_transcrito.startswith("Error") and not texto_transcrito.startswith("No se pudo"):
                            # Mostrar transcripción
                            st.success(f"Transcripción: {texto_transcrito}")
                            
                            # Procesar mensaje
                            procesar_mensaje(texto_transcrito, "audio")
                            st.success("Audio transcrito y procesado")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"{texto_transcrito}")
        
        with audio_tab2:
            st.markdown("### Grabación desde micrófono")
            
            # Verificar si hay micrófono disponible
            if st.session_state.speech_to_text and st.session_state.speech_to_text.is_microphone_available():
                st.success("Micrófono detectado")
                
                # Configuración de grabación
                col1, col2 = st.columns(2)
                with col1:
                    timeout = st.slider("Tiempo de grabación (segundos)", 3, 10, 5)
                with col2:
                    st.write("")  # Espaciado
                
                if st.button("Empezar Grabación", type="primary", key="record_audio"):
                    if st.session_state.speech_to_text is None:
                        st.error("Sistema de transcripción no disponible")
                    else:
                        # Grabar y transcribir desde micrófono
                        texto_transcrito = st.session_state.speech_to_text.transcribe_microphone(timeout)
                        
                        if texto_transcrito and not texto_transcrito.startswith("Error") and not texto_transcrito.startswith("No se pudo") and not texto_transcrito.startswith("Tiempo"):
                            # Mostrar transcripción
                            st.success(f"Transcripción: {texto_transcrito}")
                            
                            # Procesar mensaje
                            procesar_mensaje(texto_transcrito, "audio_live")
                            st.success("Audio grabado, transcrito y procesado")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.warning(f"{texto_transcrito}")
            else:
                st.warning("No se detectó micrófono o el sistema de audio no está disponible")
                st.info("Asegúrate de que tu micrófono esté conectado y funcionando")

def main():
    """Función principal de la aplicación"""
    # Configuración de la página
    st.set_page_config(
        page_title="Agente AOVA",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicializar sesión
    inicializar_sesion()
    
    # Título principal con estilo
    st.markdown("""
    #AI Agent de Voz para Lead Generation
    ### *Convierte conversaciones en oportunidades de negocio*
    """)
    st.markdown("---")
    
    # Mostrar sidebar y verificar configuración
    config_ok = mostrar_sidebar()
    
    if not config_ok:
        st.error("La aplicación no puede funcionar sin una configuración válida. Revisa las variables de entorno en el archivo .env")
        st.stop()
    
    # Layout principal
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        mostrar_conversacion()
    
    with col2:
        mostrar_controles_input()
    
    # Footer con información
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>Copyright Santiago Gamborino © 2025 </strong></p>
        <p>Powered by Streamlit • Google Gemini • Supabase</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()