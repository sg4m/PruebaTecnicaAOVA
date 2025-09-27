#!/usr/bin/env python3
"""
Script de prueba para la integración con base de datos Supabase
Prueba las funcionalidades de creación, lectura y actualización de leads y conversaciones
"""

import sys
import os
import json
import time

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.database.supabase_client import SupabaseClient
from src.ai.context_manager import ContextManager, MessageType

def test_database_connection():
    """Probar conexión básica a la base de datos"""
    print("=" * 50)
    print("🔍 PROBANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Inicializar cliente
        db_client = SupabaseClient()
        print(f"✅ Cliente Supabase inicializado")
        
        # Probar conexión
        if db_client.test_connection():
            print("✅ Conexión exitosa a Supabase")
            return db_client
        else:
            print("❌ Error de conexión a Supabase")
            return None
            
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        print("🔧 Verifica tus credenciales de Supabase en las variables de entorno")
        return None

def test_lead_operations(db_client):
    """Probar operaciones CRUD de leads"""
    print("\n" + "=" * 50)
    print("👤 PROBANDO OPERACIONES DE LEADS")
    print("=" * 50)
    
    try:
        # Datos de prueba para lead
        lead_data = {
            "informacion_personal": {
                "nombre": "María García",
                "cargo": "Directora de Tecnología",
                "empresa": "TechInnovate SA",
                "industria": "Tecnología",
                "tamaño_empresa": "50-200 empleados"
            },
            "contacto": {
                "email": "maria.garcia@techinnovate.com",
                "telefono": "+34 600 123 456",
                "preferencia_contacto": "email"
            },
            "necesidades": {
                "descripcion": "Necesita solución de automatización para procesos",
                "urgencia": "alta",
                "problemas_actuales": "Procesos manuales lentos"
            },
            "comercial": {
                "presupuesto": "50000-100000 EUR",
                "timeline": "3-6 meses",
                "autoridad_compra": True,
                "decision_maker": True
            },
            "score": {
                "total": 88,
                "categoria": "high_priority"
            },
            "analisis": {
                "quality_grade": "A",
                "priority": "alta"
            }
        }
        
        # 1. Crear lead
        print("1️⃣ Creando nuevo lead...")
        lead_id = db_client.create_lead(lead_data)
        
        if lead_id:
            print(f"✅ Lead creado exitosamente: {lead_id}")
        else:
            print("❌ Error creando lead")
            return None
        
        # 2. Leer lead
        print("2️⃣ Leyendo información del lead...")
        lead_info = db_client.get_lead(lead_id)
        
        if lead_info:
            print(f"✅ Lead recuperado: {lead_info['nombre']} - {lead_info['empresa']}")
            print(f"   Score: {lead_info['lead_score']}")
        else:
            print("❌ Error leyendo lead")
            return None
        
        # 3. Actualizar lead
        print("3️⃣ Actualizando información del lead...")
        update_data = {
            "comercial": {
                "presupuesto": "75000-150000 EUR",
                "timeline": "2-4 meses"
            },
            "score": {
                "total": 92,
                "categoria": "high_priority"
            }
        }
        
        if db_client.update_lead(lead_id, update_data):
            print("✅ Lead actualizado exitosamente")
        else:
            print("❌ Error actualizando lead")
        
        # 4. Buscar leads
        print("4️⃣ Buscando leads...")
        leads = db_client.search_leads(limit=5)
        print(f"✅ Encontrados {len(leads)} leads")
        
        return lead_id
        
    except Exception as e:
        print(f"❌ Error en operaciones de leads: {e}")
        return None

def test_context_manager_with_db(db_client):
    """Probar Context Manager integrado con base de datos"""
    print("\n" + "=" * 50)
    print("🧠 PROBANDO CONTEXT MANAGER CON BD")
    print("=" * 50)
    
    try:
        # Inicializar Context Manager con cliente de BD
        context_manager = ContextManager(db_client=db_client)
        
        # Iniciar conversación
        session_id = context_manager.start_new_conversation()
        print(f"✅ Conversación iniciada: {session_id}")
        
        # Simular conversación
        context_manager.add_message("user", "Hola, soy Carlos Ruiz de StartupXYZ", MessageType.USER_TEXT)
        context_manager.add_message("assistant", "Hola Carlos, es un placer conocerte. ¿En qué puedo ayudarte hoy?", MessageType.AGENT_RESPONSE)
        context_manager.add_message("user", "Necesitamos una solución de CRM para nuestro equipo de ventas", MessageType.USER_TEXT)
        context_manager.add_message("assistant", "Perfecto, me gustaría conocer más sobre sus necesidades específicas.", MessageType.AGENT_RESPONSE)
        
        # Actualizar información del lead
        lead_info = {
            "informacion_personal": {
                "nombre": "Carlos Ruiz",
                "empresa": "StartupXYZ",
                "cargo": "CEO"
            },
            "necesidades": {
                "descripcion": "Solución CRM para equipo de ventas",
                "urgencia": "media"
            }
        }
        
        context_manager.update_lead_info(lead_info)
        print("✅ Información de lead actualizada en contexto")
        
        # Guardar conversación en BD
        conversation_id = context_manager.save_conversation_to_db()
        if conversation_id:
            print(f"✅ Conversación guardada en BD: {conversation_id}")
        else:
            print("❌ Error guardando conversación")
        
        # Obtener contexto para AI
        ai_context = context_manager.get_conversation_context_for_ai()
        print(f"✅ Contexto AI generado: {len(ai_context.get('recent_messages', []))} mensajes")
        
        return session_id
        
    except Exception as e:
        print(f"❌ Error en Context Manager: {e}")
        return None

def test_analytics_and_metrics(db_client):
    """Probar funcionalidades de analytics y métricas"""
    print("\n" + "=" * 50)
    print("📊 PROBANDO ANALYTICS Y MÉTRICAS")
    print("=" * 50)
    
    try:
        # Obtener estadísticas de la base de datos
        stats = db_client.get_database_stats()
        if stats:
            print("📈 Estadísticas actuales:")
            print(f"   • Total de leads: {stats.get('total_leads', 0)}")
            print(f"   • Total conversaciones: {stats.get('total_conversations', 0)}")
            print(f"   • Leads de alta calidad: {stats.get('high_quality_leads', 0)}")
            print("✅ Estadísticas obtenidas correctamente")
        else:
            print("❌ Error obteniendo estadísticas")
        
        # Obtener datos de dashboard
        dashboard_data = db_client.get_analytics_dashboard_data(days=30)
        if dashboard_data:
            print("📊 Datos de dashboard (últimos 30 días):")
            print(f"   • Leads del período: {dashboard_data.get('total_leads', 0)}")
            print(f"   • Conversaciones del período: {dashboard_data.get('total_conversations', 0)}")
            
            # Distribución de scores
            score_dist = dashboard_data.get('lead_score_distribution', {})
            if score_dist:
                print("   • Distribución de calidad:")
                print(f"     - Alta calidad: {score_dist.get('high_quality', 0)}")
                print(f"     - Media calidad: {score_dist.get('medium_quality', 0)}")
                print(f"     - Baja calidad: {score_dist.get('low_quality', 0)}")
            
            print("✅ Datos de dashboard obtenidos")
        else:
            print("❌ Error obteniendo datos de dashboard")
        
        # Guardar métricas de interacción
        metrics_data = {
            "session_duration": 300,
            "messages_exchanged": 8,
            "lead_score_generated": 88,
            "conversion_phase": "qualification"
        }
        
        if db_client.save_interaction_metrics("test_session_123", metrics_data):
            print("✅ Métricas de interacción guardadas")
        else:
            print("❌ Error guardando métricas")
            
    except Exception as e:
        print(f"❌ Error en analytics: {e}")

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DE BASE DE DATOS")
    print("=" * 60)
    
    # 1. Probar conexión
    db_client = test_database_connection()
    if not db_client:
        print("\n❌ No se puede continuar sin conexión a BD")
        print("🔧 Asegúrate de:")
        print("   1. Tener las credenciales correctas en .env")
        print("   2. Haber ejecutado el schema SQL en Supabase")
        print("   3. Tener conexión a internet")
        return
    
    # 2. Probar operaciones de leads
    lead_id = test_lead_operations(db_client)
    
    # 3. Probar Context Manager con BD
    session_id = test_context_manager_with_db(db_client)
    
    # 4. Probar analytics
    test_analytics_and_metrics(db_client)
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBAS COMPLETADAS")
    print("=" * 60)
    
    if lead_id and session_id:
        print("✅ Todas las funcionalidades probadas exitosamente")
        print(f"   • Lead creado: {lead_id}")
        print(f"   • Conversación: {session_id}")
        print("\n🚀 ¡La integración con Supabase está funcionando correctamente!")
        
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("   Revisa los errores anteriores y la configuración")

if __name__ == "__main__":
    main()