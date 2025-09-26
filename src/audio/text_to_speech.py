import pyttsx3
import tempfile
import os
from typing import Optional
import streamlit as st

class TextToSpeech:
    """Cliente para convertir texto a voz usando pyttsx3"""
    
    def __init__(self):
        """Inicializar el motor de TTS (pyttsx3)"""
        self.engine = None
        
        # Inicializar pyttsx3
        try:
            self.engine = pyttsx3.init()
            self.configure_voice()
            print("pyttsx3 TTS inicializado correctamente")
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
    
    def speak_text(self, text: str) -> bool:
        """
        Reproducir texto como voz usando pyttsx3
        
        Args:
            text: Texto a convertir en voz
            
        Returns:
            True si se reprodujo correctamente
        """
        if self.engine is None:
            return False
            
        try:
            # Reproducir directamente con el engine configurado
            self.engine.say(text)
            self.engine.runAndWait()
            
            return True
        except Exception as e:
            print(f"Error reproduciendo voz: {e}")
            return False
    
    def text_to_audio_file(self, text: str) -> Optional[str]:
        """
        Convertir texto a archivo de audio usando pyttsx3
        
        Args:
            text: Texto a convertir
            
        Returns:
            Ruta del archivo de audio temporal o None si hay error
        """
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
            "pyttsx3": self.engine is not None,
            "voice_quality": "basic",
            "message": ""
        }
        
        if self.engine is not None:
            status["message"] = "pyttsx3 TTS activo"
        else:
            status["message"] = "Error: TTS no disponible"
        
        return status
    
    def is_available(self) -> bool:
        """
        Verificar si TTS está disponible
        
        Returns:
            True si TTS funciona
        """
        return self.engine is not None