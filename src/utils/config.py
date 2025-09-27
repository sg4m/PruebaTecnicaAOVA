import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CLOUD_CREDENTIALS_PATH = os.getenv('GOOGLE_CLOUD_CREDENTIALS_PATH')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_PASSWORD = os.getenv('SUPABASE_PASSWORD')
    
    # Configuraciones de audio
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHUNK_DURATION = 5  # segundos
    
    # Configuraciones de Whisper
    WHISPER_MODEL = "base"  # Cambiamos de "turbo" a "base" para mejor compatibilidad
    
    # Configuraciones de Gemini
    GEMINI_MODEL = "gemini-1.5-flash"  # Modelo actualizado
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    @classmethod
    def validate_config(cls):
        """Validar que todas las configuraciones necesarias estén presentes"""
        required_vars = [
            'GOOGLE_API_KEY',
            'SUPABASE_URL', 
            'SUPABASE_KEY'
        ]
        
        missing_vars: list[str] = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Faltan las siguientes variables de entorno: {missing_vars}")
        
        return True