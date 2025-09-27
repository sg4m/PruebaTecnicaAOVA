#!/usr/bin/env python3
"""
Script de prueba para el sistema de extracción de información de leads
Simula una conversación típica de ventas para probar la funcionalidad
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.ai.gemini_client import GeminiClient
from src.utils.config import Config
import json

def test_conversation_generation():
    """Probar el sistema de generación de conversaciones (funcionalidad disponible)"""
    
    print("🧪 Iniciando prueba del sistema de conversación con Gemini...")
    
    # Inicializar cliente de Gemini
    try:
        client = GeminiClient()
        print("✅ Cliente Gemini inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando Gemini: {e}")
        return
    
    # Conversación simulada
    conversacion_simulada = [
        {
            "role": "user",
            "content": "Hola, me llamo María García y soy directora de marketing de TechSolutions SA. Estamos buscando servicios de automatización de procesos de ventas."
        },
        {
            "role": "assistant", 
            "content": "¡Hola María! Es un placer conocerte. Soy AOVA, consultor de crecimiento estratégico. Me parece muy interesante que busquen automatización de ventas. ¿Cuáles son los principales desafíos que enfrentan actualmente en su proceso de ventas?"
        },
        {
            "role": "user",
            "content": "Bueno, somos una empresa de tecnología de aproximadamente 50 empleados. Nuestro problema principal es que perdemos muchos leads porque no tenemos un sistema automatizado de seguimiento. También nos toma mucho tiempo calificar los prospectos manualmente."
        },
        {
            "role": "assistant",
            "content": "Entiendo perfectamente el problema, María. La pérdida de leads por falta de seguimiento automatizado es muy común en empresas de crecimiento como la suya. ¿Tienen definido un presupuesto aproximado para implementar una solución de automatización?"
        },
        {
            "role": "user", 
            "content": "Sí, tenemos aprobado un presupuesto de entre 15,000 y 25,000 dólares para este proyecto. Necesitamos implementarlo antes del próximo trimestre. Mi email es maria.garcia@techsolutions.com por si necesitas enviarme información adicional."
        },
        {
            "role": "assistant",
            "content": "Excelente, María. Con ese presupuesto y timeline definitivamente podemos crear una solución robusta para TechSolutions. Te voy a preparar una propuesta personalizada. ¿Cuál sería el mejor momento para agendar una demo donde te pueda mostrar casos de éxito similares?"
        },
        {
            "role": "user",
            "content": "Me parece perfecto. Podríamos agendar algo para la próxima semana. Tengo autoridad total para tomar la decisión de compra, así que si la propuesta es buena podríamos cerrar rápidamente."
        }
    ]
    
    print(f"\n📋 Procesando conversación simulada con {len(conversacion_simulada)} mensajes...")
    
    # Probar generación de respuestas
    try:
        print("\n🤖 Probando generación de respuestas...")
        
        # Tomar solo los mensajes del usuario para generar respuestas
        user_messages = [msg for msg in conversacion_simulada if msg['role'] == 'user']
        
        for i, msg in enumerate(user_messages[:3], 1):  # Probar solo 3 mensajes
            print(f"\n--- PRUEBA {i} ---")
            print(f"� Usuario: {msg['content'][:100]}...")
            
            # Generar respuesta
            respuesta = client.generate_response(
                msg['content'],
                context=conversacion_simulada[:i*2]  # Contexto previo
            )
            
            print(f"🤖 Respuesta generada: {respuesta[:150]}...")
            
        print(f"\n✅ Prueba de generación completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Verificar configuración
    try:
        Config.validate_config()
        print("✅ Configuración válida")
    except ValueError as e:
        print(f"❌ Error en configuración: {e}")
        print("💡 Asegúrate de tener configurado GOOGLE_API_KEY en .env")
        exit(1)
    
    test_conversation_generation()