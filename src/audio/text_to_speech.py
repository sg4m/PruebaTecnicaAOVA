import pyttsx3
import tempfile
import os
from typing import Optional
import streamlit as st
from io import BytesIO
import base64
from google.cloud import texttospeech
from src.utils.config import Config

class TextToSpeech:
    """Cliente para convertir texto a voz usando Google Cloud TTS y pyttsx3 como fallback"""
    
    def __init__(self):
        """Inicializar los motores de TTS (Google Cloud y pyttsx3 como fallback)"""
        self.config = Config()
        self.google_client = None
        self.engine = None
        
        # Intentar inicializar Google Cloud TTS
        self.google_status = "no_configurado"
        try:
            if hasattr(self.config, 'GOOGLE_CLOUD_CREDENTIALS_PATH') and self.config.GOOGLE_CLOUD_CREDENTIALS_PATH:
                # Verificar que el archivo de credenciales existe
                if os.path.exists(self.config.GOOGLE_CLOUD_CREDENTIALS_PATH):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.GOOGLE_CLOUD_CREDENTIALS_PATH
                    self.google_client = texttospeech.TextToSpeechClient()
                    self.google_status = "activo"
                    print("✅ Google Cloud TTS inicializado correctamente - Voz natural habilitada")
                else:
                    self.google_status = "archivo_no_encontrado"
                    print(f"❌ Archivo de credenciales no encontrado: {self.config.GOOGLE_CLOUD_CREDENTIALS_PATH}")
                    print("📖 Consulta CONFIGURAR_TTS.md para instrucciones completas")
            else:
                self.google_status = "no_configurado"
                print("ℹ️  Google Cloud TTS no configurado - usando voz básica")
                print("💡 Para voz natural: configura GOOGLE_CLOUD_CREDENTIALS_PATH en .env")
        except Exception as e:
            print(f"⚠️  Error inicializando Google Cloud TTS: {str(e)}")
            print("📖 Consulta CONFIGURAR_TTS.md para solucionar problemas")
            self.google_client = None
            self.google_status = "error"
        
        # Fallback a pyttsx3
        try:
            self.engine = pyttsx3.init()
            self.configure_voice()
            print("✅ pyttsx3 TTS inicializado como fallback")
        except Exception as e:
            st.error(f"Error inicializando TTS: {e}")
            self.engine = None
    
    def configure_voice(self):
        """Configurar la voz del agente"""
        if self.engine is None:
            return
            
        try:
            # Obtener voces disponibles
            voices = self.engine.getProperty('voices')
            
            # Buscar voz en español (femenina preferida para agente de ventas)
            spanish_voice = None
            female_voice = None
            
            for voice in voices:
                if voice.languages and 'es' in str(voice.languages).lower():
                    spanish_voice = voice.id
                    if 'female' in voice.name.lower() or 'mujer' in voice.name.lower():
                        female_voice = voice.id
                        break
            
            # Configurar voz
            if female_voice:
                self.engine.setProperty('voice', female_voice)
            elif spanish_voice:
                self.engine.setProperty('voice', spanish_voice)
            elif voices:
                # Usar la primera voz disponible
                self.engine.setProperty('voice', voices[0].id)
            
            # Configurar velocidad y volumen
            self.engine.setProperty('rate', 180)    # Palabras por minuto
            self.engine.setProperty('volume', 0.8)   # Volumen (0.0 a 1.0)
            
        except Exception as e:
            print(f"Error configurando voz: {e}")
    
    def _synthesize_with_google_cloud(self, text: str) -> Optional[bytes]:
        """
        Sintetizar texto usando Google Cloud TTS
        
        Args:
            text: Texto a sintetizar
            
        Returns:
            Audio en bytes o None si hay error
        """
        if not self.google_client:
            return None
            
        try:
            # Configurar la síntesis
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configurar voz en español (España) - Voz neural más natural
            voice = texttospeech.VoiceSelectionParams(
                language_code="es-ES",
                name="es-ES-Neural2-C",  # Voz femenina neural muy natural
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # Configurar audio de salida en MP3 de alta calidad
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,  # Velocidad normal
                pitch=0.0,          # Tono normal
                volume_gain_db=0.0  # Volumen normal
            )
            
            # Realizar síntesis
            response = self.google_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            print(f"Error en Google Cloud TTS: {e}")
            return None

    def speak_text(self, text: str) -> bool:
        """
        Reproducir texto como voz usando Google Cloud TTS o pyttsx3 como fallback
        
        Args:
            text: Texto a convertir en voz
            
        Returns:
            True si se reprodujo correctamente
        """
        # Intentar primero con Google Cloud TTS
        if self.google_client:
            try:
                audio_content = self._synthesize_with_google_cloud(text)
                if audio_content:
                    # Crear archivo temporal para reproducir
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    temp_file.write(audio_content)
                    temp_file.close()
                    
                    # Mostrar control de audio en Streamlit
                    st.audio(audio_content, format="audio/mp3")
                    
                    # Limpiar archivo temporal
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                    
                    return True
            except Exception as e:
                print(f"Error con Google Cloud TTS, usando fallback: {e}")
        
        # Fallback a pyttsx3
        if self.engine is None:
            return False
            
        try:
            # Reinicializar engine para evitar conflictos
            self.engine.stop()
            
            # Crear nuevo engine para esta reproducción
            temp_engine = pyttsx3.init()
            
            # Aplicar la misma configuración
            voices = temp_engine.getProperty('voices')
            if voices:
                # Usar la primera voz disponible
                temp_engine.setProperty('voice', voices[0].id)
            temp_engine.setProperty('rate', 180)
            temp_engine.setProperty('volume', 0.8)
            
            # Reproducir
            temp_engine.say(text)
            temp_engine.runAndWait()
            temp_engine.stop()
            
            return True
        except Exception as e:
            print(f"Error reproduciendo voz: {e}")
            return False
    
    def text_to_audio_file(self, text: str) -> Optional[str]:
        """
        Convertir texto a archivo de audio usando Google Cloud TTS o pyttsx3 como fallback
        
        Args:
            text: Texto a convertir
            
        Returns:
            Ruta del archivo de audio temporal o None si hay error
        """
        # Intentar primero con Google Cloud TTS
        if self.google_client:
            try:
                audio_content = self._synthesize_with_google_cloud(text)
                if audio_content:
                    # Crear archivo temporal MP3
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    temp_file.write(audio_content)
                    temp_file.close()
                    return temp_file.name
            except Exception as e:
                print(f"Error con Google Cloud TTS para archivo, usando fallback: {e}")
        
        # Fallback a pyttsx3
        if self.engine is None:
            return None
            
        try:
            # Crear archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.close()
            
            # Guardar audio en archivo
            self.engine.save_to_file(text, temp_file.name)
            self.engine.runAndWait()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Error creando archivo de audio: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """
        Obtener lista de voces disponibles
        
        Returns:
            Lista de nombres de voces
        """
        if self.engine is None:
            return []
            
        try:
            voices = self.engine.getProperty('voices')
            return [voice.name for voice in voices] if voices else []
        except:
            return []
    
    def get_tts_status(self) -> dict:
        """
        Obtener estado detallado del sistema TTS
        
        Returns:
            Diccionario con información del estado
        """
        status = {
            "google_cloud": self.google_status,
            "pyttsx3": self.engine is not None,
            "voice_quality": "natural" if self.google_client else "basic",
            "message": ""
        }
        
        if self.google_status == "activo":
            status["message"] = "🎤 Voz natural Google Cloud TTS activa"
        elif self.google_status == "no_configurado":
            status["message"] = "🔧 Usando voz básica - configura Google Cloud para voz natural"
        elif self.google_status == "archivo_no_encontrado":
            status["message"] = "❌ Archivo de credenciales no encontrado"
        elif self.google_status == "error":
            status["message"] = "⚠️ Error en Google Cloud TTS - usando fallback"
        
        return status
    
    def is_available(self) -> bool:
        """
        Verificar si TTS está disponible
        
        Returns:
            True si TTS funciona
        """
        return self.engine is not None