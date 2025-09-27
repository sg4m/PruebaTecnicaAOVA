import pyttsx3
import tempfile
import os
from typing import Optional
import streamlit as st

class TextToSpeech:
    """Cliente simplificado para convertir texto a voz usando solo pyttsx3"""
    
    def __init__(self):
        """Inicializar el motor pyttsx3"""
        self.engine = None
        
        try:
            self.engine = pyttsx3.init()
            self.configure_voice()
            print("pyttsx3 TTS inicializado correctamente")
        except Exception as e:
            print(f"Error inicializando TTS: {e}")
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
            
            # Configurar velocidad y volumen optimizados
            self.engine.setProperty('rate', 180)    # Palabras por minuto
            self.engine.setProperty('volume', 0.8)   # Volumen (0.0 a 1.0)
            
        except Exception as e:
            print(f"Error configurando voz: {e}")

    def speak_text(self, text: str) -> bool:
        """
        Reproducir texto como voz usando pyttsx3
        
        """
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
        Convertir texto a archivo de audio usando pyttsx3
        
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
        Obtener estado del sistema TTS simplificado

        """
        status = {
            "pyttsx3": self.engine is not None,
            "message": ""
        }
        
        if self.engine:
            status["message"] = "TTS básico funcionando correctamente"
        else:
            status["message"] = "TTS no disponible"
        
        return status
    
    def is_available(self) -> bool:
        """
        Verificar si TTS está disponible

        """
        return self.engine is not None