#!/usr/bin/env python3
"""
Script simple para probar que las rutas de importación funcionan correctamente
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def test_imports():
    """Probar que todas las importaciones funcionan"""
    print("🧪 Probando importaciones...")
    
    try:
        from src.utils.config import Config
        print("✅ Config importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando Config: {e}")
        return False
    
    try:
        from src.ai.gemini_client import GeminiClient
        print("✅ GeminiClient importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando GeminiClient: {e}")
        return False
    
    try:
        from src.ai.context_manager import ContextManager, MessageType
        print("✅ ContextManager importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando ContextManager: {e}")
        return False
    
    try:
        from src.database.supabase_client import SupabaseClient
        print("✅ SupabaseClient importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SupabaseClient: {e}")
        return False
    
    try:
        from src.audio.text_to_speech import TextToSpeech
        print("✅ TextToSpeech importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando TextToSpeech: {e}")
        return False
    
    try:
        from src.audio.speech_to_text import SpeechToText
        print("✅ SpeechToText importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SpeechToText: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Probar funcionalidad básica de los componentes"""
    print("\n🧪 Probando funcionalidad básica...")
    
    try:
        from src.utils.config import Config
        Config.validate_config()
        print("✅ Configuración válida")
    except Exception as e:
        print(f"⚠️ Problema con configuración: {e}")
    
    try:
        from src.ai.gemini_client import GeminiClient
        client = GeminiClient()
        print("✅ GeminiClient inicializado correctamente")
        
        # Probar generación simple
        respuesta = client.generate_response("Hola, ¿cómo estás?")
        print(f"✅ Respuesta generada: {respuesta[:50]}...")
        
    except Exception as e:
        print(f"⚠️ Problema con GeminiClient: {e}")
    
    try:
        from src.database.supabase_client import SupabaseClient
        db_client = SupabaseClient()
        if db_client.test_connection():
            print("✅ Conexión a Supabase exitosa")
        else:
            print("⚠️ No se pudo conectar a Supabase")
    except Exception as e:
        print(f"⚠️ Problema con Supabase: {e}")

if __name__ == "__main__":
    print("🚀 PROBANDO SISTEMA COMPLETO")
    print("=" * 50)
    
    # Mostrar información del proyecto
    print(f"📁 Directorio de pruebas: {os.path.dirname(__file__)}")
    print(f"📁 Directorio del proyecto: {project_root}")
    print(f"🐍 Python path: {sys.path[-1]}")
    
    # Probar importaciones
    if test_imports():
        print("\n✅ Todas las importaciones exitosas")
        
        # Probar funcionalidad básica
        test_basic_functionality()
        
        print("\n🎉 ¡Pruebas completadas!")
        print("Ahora puedes ejecutar los otros archivos de prueba:")
        print("  python tests/test_lead_extraction.py")
        print("  python tests/test_complete_system.py")
        print("  python tests/test_database_integration.py")
    else:
        print("\n❌ Algunas importaciones fallaron")
        print("Verifica la estructura del proyecto y los archivos")