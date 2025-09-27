import speech_recognition as sr
import tempfile
import os
from typing import Optional
import streamlit as st
from pydub import AudioSegment

class SpeechToText:
    """Cliente para convertir audio a texto usando Google Speech Recognition"""
    
    def __init__(self):
        """Inicializar el recognizer"""
        self.recognizer = sr.Recognizer()
        # Ajustar para mejor reconocimiento
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def transcribe_audio_file(self, audio_file) -> Optional[str]:
        """
        Transcribir archivo de audio a texto
        
        Args:
            audio_file: Archivo de audio de Streamlit
            
        Returns:
            Texto transcrito o None si hay error
        """
        temp_file_path = None
        wav_file_path = None
        
        try:
            # Obtener extensión del archivo
            file_extension = audio_file.name.split('.')[-1].lower()
            
            # Guardar archivo temporal con extensión original
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
                temp_file.write(audio_file.read())
                temp_file_path = temp_file.name
            
            # Convertir a WAV si no es WAV
            if file_extension != 'wav':
                try:
                    # Verificar si FFmpeg está disponible
                    try:
                        # Cargar audio con pydub
                        audio = AudioSegment.from_file(temp_file_path)
                        
                        # Convertir a WAV con configuraciones óptimas para speech recognition
                        audio = audio.set_frame_rate(16000).set_channels(1)
                        
                        # Guardar como WAV
                        wav_file_path = temp_file_path.replace(f".{file_extension}", ".wav")
                        audio.export(wav_file_path, format="wav")
                        
                    except Exception as ffmpeg_error:
                        return f"Error: FFmpeg no está instalado. Por favor, sube un archivo WAV o instala FFmpeg. Detalle: {ffmpeg_error}"
                        
                except Exception as e:
                    return f"Error convirtiendo audio: {e}. Intenta con un archivo WAV."
            else:
                wav_file_path = temp_file_path
            
            # Cargar audio con speech_recognition
            with sr.AudioFile(wav_file_path) as source:
                # Ajustar al ruido ambiente
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Leer el audio
                audio_data = self.recognizer.listen(source)
            
            # Transcribir usando Google Speech Recognition (gratuito)
            try:
                text = self.recognizer.recognize_google(
                    audio_data, 
                    language='es-ES'  # Español de España
                )
                return text
                
            except sr.UnknownValueError:
                return "No se pudo entender el audio. Por favor, habla más claro o intenta de nuevo."
                
            except sr.RequestError as e:
                return f"Error del servicio de reconocimiento: {e}"
                
        except Exception as e:
            return f"Error procesando audio: {e}"
            
        finally:
            # Limpiar archivos temporales
            for file_path in [temp_file_path, wav_file_path]:
                if file_path and file_path != temp_file_path:
                    try:
                        os.unlink(file_path)
                    except:
                        pass
            if temp_file_path:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    
    def transcribe_microphone(self, timeout: int = 5) -> Optional[str]:
        """
        Transcribir desde micrófono en tiempo real
        
        Args:
            timeout: Tiempo límite en segundos
            
        Returns:
            Texto transcrito o None si hay error
        """
        try:
            with sr.Microphone() as source:
                st.info("🎤 Escuchando... Habla ahora")
                
                # Ajustar al ruido ambiente
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Escuchar audio
                audio_data = self.recognizer.listen(source, timeout=timeout)
                
                st.info("🔄 Procesando audio...")
                
                # Transcribir
                text = self.recognizer.recognize_google(
                    audio_data,
                    language='es-ES'
                )
                
                return text
                
        except sr.WaitTimeoutError:
            return "Tiempo de espera agotado. No se detectó audio."
            
        except sr.UnknownValueError:
            return "No se pudo entender el audio. Por favor, intenta de nuevo."
            
        except sr.RequestError as e:
            return f"Error del servicio de reconocimiento: {e}"
            
        except Exception as e:
            return f"Error: {e}"
    
    def is_microphone_available(self) -> bool:
        """
        Verificar si hay micrófono disponible
        
        Returns:
            True si hay micrófono disponible
        """
        try:
            # Listar micrófonos disponibles
            mic_list = sr.Microphone.list_microphone_names()
            
            # Intentar crear una instancia de micrófono
            if len(mic_list) > 0:
                with sr.Microphone() as source:
                    # Test rápido
                    pass
                return True
            return False
        except Exception as e:
            print(f"Error detecting microphone: {e}")
            return False
    
    def get_microphone_list(self) -> list:
        """
        Obtener lista de micrófonos disponibles
        
        Returns:
            Lista de nombres de micrófonos
        """
        try:
            return sr.Microphone.list_microphone_names()
        except:
            return []