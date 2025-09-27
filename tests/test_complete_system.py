#!/usr/bin/env python3
"""
Script de prueba para el sistema completo con Context Manager
Simula una conversación completa para probar todo el flujo
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.ai.gemini_client import GeminiClient
from src.ai.context_manager import ContextManager, MessageType, ConversationPhase
from src.utils.config import Config
import json
import time

def test_complete_system():
    """Probar el sistema completo con Context Manager"""
    
    print("🧪 Iniciando prueba del sistema completo con Context Manager...")
    
    # Inicializar componentes
    try:
        gemini_client = GeminiClient()
        context_manager = ContextManager()
        
        print("✅ Componentes inicializados correctamente")
        
        # Iniciar nueva conversación
        session_id = context_manager.start_new_conversation()
        print(f"📋 Nueva conversación iniciada: {session_id}")
        
    except Exception as e:
        print(f"❌ Error inicializando componentes: {e}")
        return
    
    # Simular conversación completa
    conversation_steps = [
        {
            "user_message": "Hola, me llamo Carlos Mendoza y soy CTO de InnovaTech Solutions. Estamos buscando ayuda con automatización de marketing.",
            "expected_phase": ConversationPhase.INTRODUCTION
        },
        {
            "user_message": "Somos una startup de 35 empleados en el sector fintech. Nuestro principal problema es que no tenemos un sistema para nutrir leads automáticamente.",
            "expected_phase": ConversationPhase.DISCOVERY
        },
        {
            "user_message": "Necesitamos implementar algo antes de fin de año, y tenemos un presupuesto de alrededor de 20,000 dólares para este proyecto.",
            "expected_phase": ConversationPhase.QUALIFICATION
        },
        {
            "user_message": "¿Podrían mostrarme cómo funciona su plataforma? Me interesa ver casos de éxito similares al nuestro.",
            "expected_phase": ConversationPhase.PRESENTATION
        },
        {
            "user_message": "Me preocupa un poco la integración con nuestros sistemas existentes. ¿Qué tan complejo sería?",
            "expected_phase": ConversationPhase.OBJECTION_HANDLING
        },
        {
            "user_message": "Perfecto, creo que es justo lo que necesitamos. ¿Cuáles serían los próximos pasos? Mi email es carlos.mendoza@innovatech.com",
            "expected_phase": ConversationPhase.CLOSING
        }
    ]
    
    print(f"\n🎭 Simulando conversación de {len(conversation_steps)} pasos...")
    
    for i, step in enumerate(conversation_steps, 1):
        print(f"\n--- PASO {i} ---")
        user_message = step["user_message"]
        expected_phase = step["expected_phase"]
        
        print(f"👤 Usuario: {user_message}")
        
        # Agregar mensaje del usuario al contexto
        context_manager.add_message('user', user_message, MessageType.USER_TEXT)
        
        # Analizar fase de conversación
        detected_phase = context_manager.analyze_conversation_phase()
        print(f"🎯 Fase detectada: {detected_phase.value}")
        
        # Actualizar resumen de conversación
        context_manager.update_conversation_summary()
        
        # Generar respuesta del agente
        try:
            agent_response = gemini_client.generate_response(
                user_message,
                context_manager=context_manager
            )
            print(f"🤖 Agente: {agent_response[:150]}...")
            
            # Agregar respuesta del agente al contexto
            context_manager.add_message('assistant', agent_response, MessageType.AGENT_RESPONSE)
            
        except Exception as e:
            print(f"❌ Error generando respuesta: {e}")
            continue
        
        # Mostrar información del contexto cada pocas interacciones
        if i % 2 == 0:  # Cada 2 mensajes
            try:
                print("� Analizando progreso del contexto...")
                
                if context_manager.current_context:
                    ctx = context_manager.current_context
                    print(f"   • Total mensajes: {len(ctx.messages)}")
                    print(f"   • Interacciones: {ctx.total_interactions}")
                    print(f"   • Fase actual: {ctx.current_phase.value}")
                
            except Exception as e:
                print(f"❌ Error analizando contexto: {e}")
        
        # Pausa breve para simular tiempo real
        time.sleep(0.5)
    
    # Mostrar resumen final del contexto
    print(f"\n" + "="*60)
    print("📈 RESUMEN FINAL DE LA CONVERSACIÓN")
    print("="*60)
    
    if context_manager.current_context:
        ctx = context_manager.current_context
        
        print(f"🆔 ID de sesión: {ctx.session_id}")
        print(f"⏱️  Duración: {(time.time() - ctx.start_time):.1f} segundos")
        print(f"💬 Total de mensajes: {len(ctx.messages)}")
        print(f"🔄 Interacciones: {ctx.total_interactions}")
        print(f"📍 Fase final: {ctx.current_phase.value}")
        
        # Información del lead
        if ctx.lead_info:
            print(f"\n👤 INFORMACIÓN DEL LEAD:")
            print(json.dumps(ctx.lead_info, indent=2, ensure_ascii=False))
        
        # Resumen de conversación
        print(f"\n📝 RESUMEN DE CONVERSACIÓN:")
        if ctx.summary.mentioned_needs:
            print(f"🎯 Necesidades identificadas: {len(ctx.summary.mentioned_needs)}")
            for need in ctx.summary.mentioned_needs:
                print(f"  • {need}")
        
        if ctx.summary.objections_raised:
            print(f"⚠️  Objeciones identificadas: {len(ctx.summary.objections_raised)}")
            for objection in ctx.summary.objections_raised:
                print(f"  • {objection}")
        
        # Insights de conversación
        insights = context_manager._generate_conversation_insights()
        print(f"\n🧠 INSIGHTS:")
        print(f"📊 Nivel de engagement: {insights.get('engagement_level', 'unknown')}")
        print(f"📈 Longitud de conversación: {insights.get('conversation_length', 0)} mensajes")
        print(f"🎭 Fase actual: {insights.get('conversation_phase', 'unknown')}")
        
        # Contexto personalizado para IA
        print(f"\n🎯 CONTEXTO PERSONALIZADO GENERADO:")
        personalized_context = context_manager.get_personalized_prompt_context()
        print(f"'{personalized_context}'")
        
        # Guardar contexto
        try:
            if context_manager.save_context("test_conversation_context.json"):
                print(f"\n💾 Contexto guardado en: test_conversation_context.json")
        except Exception as e:
            print(f"\n❌ Error guardando contexto: {e}")
    
    print(f"\n✅ Prueba del sistema completo finalizada!")

if __name__ == "__main__":
    # Verificar configuración
    try:
        Config.validate_config()
        print("✅ Configuración válida")
    except ValueError as e:
        print(f"❌ Error en configuración: {e}")
        print("💡 Asegúrate de tener configurado GOOGLE_API_KEY en .env")
        exit(1)
    
    test_complete_system()