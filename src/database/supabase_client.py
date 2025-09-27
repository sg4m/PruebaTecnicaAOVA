"""
Cliente de Supabase para el Agente de IA
Maneja la conexión y operaciones CRUD con la base de datos
"""

from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import json
import time
from datetime import datetime, timedelta
from src.utils.config import Config

class SupabaseClient:
    """Cliente para interactuar con Supabase"""
    
    def __init__(self):
        """Inicializar cliente de Supabase"""
        try:
            self.url = Config.SUPABASE_URL
            self.key = Config.SUPABASE_KEY
            
            if not self.url or not self.key:
                raise ValueError("Faltan credenciales de Supabase en la configuración")
            
            self.supabase: Client = create_client(self.url, self.key)
            print("✅ Cliente Supabase inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando Supabase: {e}")
            raise e
    
    def test_connection(self) -> bool:
        """Probar conexión a Supabase"""
        try:
            # Intentar hacer una consulta simple
            result = self.supabase.table('leads').select("id").limit(1).execute()
            print("✅ Conexión a Supabase exitosa")
            return True
        except Exception as e:
            print(f"❌ Error de conexión a Supabase: {e}")
            return False
    
    # ==========================================
    # OPERACIONES DE LEADS
    # ==========================================
    
    def create_lead(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """
        Crear un nuevo lead en la base de datos
        
        Args:
            lead_data: Información del lead extraída por el sistema
            
        Returns:
            ID del lead creado o None si hay error
        """
        try:
            # Preparar datos para inserción
            lead_record = self._prepare_lead_data(lead_data)
            
            # Insertar en la base de datos
            result = self.supabase.table('leads').insert(lead_record).execute()
            
            if result.data and len(result.data) > 0:
                lead_id = result.data[0]['id']
                print(f"✅ Lead creado con ID: {lead_id}")
                return lead_id
            else:
                print("❌ No se pudo crear el lead")
                return None
                
        except Exception as e:
            print(f"❌ Error creando lead: {e}")
            return None
    
    def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> bool:
        """
        Actualizar información de un lead existente
        
        Args:
            lead_id: ID del lead a actualizar
            lead_data: Nueva información del lead
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            # Preparar datos de actualización
            update_data = self._prepare_lead_data(lead_data, update=True)
            
            # Actualizar en la base de datos
            result = self.supabase.table('leads').update(update_data).eq('id', lead_id).execute()
            
            if result.data and len(result.data) > 0:
                print(f"✅ Lead {lead_id} actualizado correctamente")
                return True
            else:
                print(f"❌ No se pudo actualizar el lead {lead_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error actualizando lead: {e}")
            return False
    
    def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un lead por ID
        
        Args:
            lead_id: ID del lead
            
        Returns:
            Información del lead o None si no existe
        """
        try:
            result = self.supabase.table('leads').select("*").eq('id', lead_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo lead: {e}")
            return None
    
    def search_leads(self, filters: Dict[str, Any] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Buscar leads con filtros opcionales
        
        Args:
            filters: Filtros de búsqueda
            limit: Límite de resultados
            
        Returns:
            Lista de leads encontrados
        """
        try:
            query = self.supabase.table('leads').select("*")
            
            # Aplicar filtros si existen
            if filters:
                for field, value in filters.items():
                    if value is not None:
                        query = query.eq(field, value)
            
            result = query.limit(limit).execute()
            return result.data or []
            
        except Exception as e:
            print(f"❌ Error buscando leads: {e}")
            return []
    
    # ==========================================
    # OPERACIONES DE CONVERSACIONES
    # ==========================================
    
    def save_conversation(self, session_id: str, context_data: Dict[str, Any]) -> Optional[str]:
        """
        Guardar una conversación completa
        
        Args:
            session_id: ID de la sesión de conversación
            context_data: Datos del contexto de conversación
            
        Returns:
            ID de la conversación guardada o None si hay error
        """
        try:
            # Preparar datos de conversación
            conversation_record = self._prepare_conversation_data(session_id, context_data)
            
            # Insertar en la base de datos
            result = self.supabase.table('conversations').insert(conversation_record).execute()
            
            if result.data and len(result.data) > 0:
                conversation_id = result.data[0]['id']
                print(f"✅ Conversación guardada con ID: {conversation_id}")
                return conversation_id
            else:
                print("❌ No se pudo guardar la conversación")
                return None
                
        except Exception as e:
            print(f"❌ Error guardando conversación: {e}")
            return None
    
    def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener una conversación por session_id
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Datos de la conversación o None si no existe
        """
        try:
            result = self.supabase.table('conversations').select("*").eq('session_id', session_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo conversación: {e}")
            return None
    
    def get_lead_conversations(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Obtener todas las conversaciones de un lead
        
        Args:
            lead_id: ID del lead
            
        Returns:
            Lista de conversaciones del lead
        """
        try:
            result = self.supabase.table('conversations').select("*").eq('lead_id', lead_id).execute()
            return result.data or []
            
        except Exception as e:
            print(f"❌ Error obteniendo conversaciones del lead: {e}")
            return []
    
    # ==========================================
    # OPERACIONES DE MÉTRICAS
    # ==========================================
    
    def save_interaction_metrics(self, session_id: str, metrics: Dict[str, Any]) -> bool:
        """
        Guardar métricas de una interacción
        
        Args:
            session_id: ID de la sesión
            metrics: Métricas de la interacción
            
        Returns:
            True si se guardó correctamente
        """
        try:
            metric_record = {
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'metrics_data': json.dumps(metrics),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('interaction_metrics').insert(metric_record).execute()
            
            return result.data and len(result.data) > 0
            
        except Exception as e:
            print(f"❌ Error guardando métricas: {e}")
            return False
    
    def get_analytics_dashboard_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtener datos para dashboard de analytics
        
        Args:
            days: Número de días hacia atrás para analizar
            
        Returns:
            Datos agregados para dashboard
        """
        try:
            # Fecha límite
            date_limit = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Leads por día
            leads_result = self.supabase.table('leads').select("created_at, lead_score").gte('created_at', date_limit).execute()
            
            # Conversaciones por día
            conversations_result = self.supabase.table('conversations').select("created_at, total_interactions, final_phase").gte('created_at', date_limit).execute()
            
            # Procesar datos
            dashboard_data = {
                'total_leads': len(leads_result.data) if leads_result.data else 0,
                'total_conversations': len(conversations_result.data) if conversations_result.data else 0,
                'leads_by_day': self._group_by_day(leads_result.data, 'created_at'),
                'conversations_by_day': self._group_by_day(conversations_result.data, 'created_at'),
                'lead_score_distribution': self._analyze_lead_scores(leads_result.data),
                'phase_distribution': self._analyze_phases(conversations_result.data),
                'period_days': days
            }
            
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Error obteniendo datos de analytics: {e}")
            return {}
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def _prepare_lead_data(self, lead_data: Dict[str, Any], update: bool = False) -> Dict[str, Any]:
        """Preparar datos de lead para inserción/actualización en BD"""
        
        # Extraer información estructurada
        personal = lead_data.get('personal', {}) or lead_data.get('informacion_personal', {})
        contacto = lead_data.get('contacto', {})
        necesidades = lead_data.get('necesidades', {})
        comercial = lead_data.get('comercial', {})
        score_info = lead_data.get('score', {}) or lead_data.get('puntuacion_lead', {})
        analisis = lead_data.get('analisis', {})
        
        record = {
            # Información personal
            'nombre': personal.get('nombre'),
            'cargo': personal.get('cargo'),
            'empresa': personal.get('empresa'),
            'industria': personal.get('industria'),
            'tamaño_empresa': personal.get('tamaño_empresa'),
            
            # Contacto
            'email': contacto.get('email'),
            'telefono': contacto.get('telefono'),
            'preferencia_contacto': contacto.get('preferencia_contacto'),
            
            # Necesidades y comercial
            'necesidades_descripcion': necesidades.get('descripcion'),
            'urgencia': necesidades.get('urgencia'),
            'problemas_actuales': necesidades.get('problemas') or necesidades.get('problemas_actuales'),
            'presupuesto': comercial.get('presupuesto'),
            'timeline': comercial.get('timeline'),
            'autoridad_compra': comercial.get('autoridad') or comercial.get('autoridad_compra'),
            'decision_maker': comercial.get('decision_maker'),
            
            # Puntuación y análisis
            'lead_score': score_info.get('total') or score_info.get('score_total', 0),
            'categoria': score_info.get('categoria'),
            'quality_grade': analisis.get('quality_grade'),
            'priority': analisis.get('priority'),
            
            # Datos JSON completos
            'raw_lead_data': json.dumps(lead_data),
        }
        
        # Agregar timestamps
        if not update:
            record['created_at'] = datetime.utcnow().isoformat()
        
        record['updated_at'] = datetime.utcnow().isoformat()
        
        # Limpiar valores None
        return {k: v for k, v in record.items() if v is not None}
    
    def _prepare_conversation_data(self, session_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar datos de conversación para inserción en BD"""
        
        record = {
            'session_id': session_id,
            'lead_id': context_data.get('lead_id'),
            'start_time': datetime.fromtimestamp(context_data.get('start_time', time.time())).isoformat(),
            'end_time': datetime.fromtimestamp(context_data.get('last_activity', time.time())).isoformat(),
            'total_interactions': context_data.get('total_interactions', 0),
            'final_phase': context_data.get('current_phase'),
            'messages_count': len(context_data.get('messages', [])),
            'summary_data': json.dumps(context_data.get('summary', {})),
            'conversation_data': json.dumps(context_data),
            'created_at': datetime.utcnow().isoformat()
        }
        
        return record
    
    def _group_by_day(self, data: List[Dict], date_field: str) -> Dict[str, int]:
        """Agrupar datos por día"""
        if not data:
            return {}
        
        grouped = {}
        for item in data:
            if date_field in item and item[date_field]:
                # Extraer solo la fecha (sin hora)
                date_str = item[date_field][:10]  # YYYY-MM-DD
                grouped[date_str] = grouped.get(date_str, 0) + 1
        
        return grouped
    
    def _analyze_lead_scores(self, leads_data: List[Dict]) -> Dict[str, int]:
        """Analizar distribución de puntuaciones de leads"""
        if not leads_data:
            return {}
        
        distribution = {
            'high_quality': 0,    # 80-100
            'medium_quality': 0,  # 60-79
            'low_quality': 0,     # 40-59
            'unqualified': 0      # 0-39
        }
        
        for lead in leads_data:
            score = lead.get('lead_score', 0) or 0
            if score >= 80:
                distribution['high_quality'] += 1
            elif score >= 60:
                distribution['medium_quality'] += 1
            elif score >= 40:
                distribution['low_quality'] += 1
            else:
                distribution['unqualified'] += 1
        
        return distribution
    
    def _analyze_phases(self, conversations_data: List[Dict]) -> Dict[str, int]:
        """Analizar distribución de fases finales de conversación"""
        if not conversations_data:
            return {}
        
        phases = {}
        for conversation in conversations_data:
            phase = conversation.get('final_phase', 'unknown')
            phases[phase] = phases.get(phase, 0) + 1
        
        return phases
    
    # ==========================================
    # OPERACIONES DE ADMINISTRACIÓN
    # ==========================================
    
    def create_tables_if_not_exist(self) -> bool:
        """
        Crear tablas si no existen (solo para desarrollo/testing)
        En producción, las tablas deben crearse via Supabase Dashboard
        """
        print("ℹ️  Para crear las tablas, usa el SQL Schema proporcionado en Supabase Dashboard")
        return True
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas generales de la base de datos"""
        try:
            stats = {}
            
            # Contar leads
            leads_result = self.supabase.table('leads').select("id", count='exact').execute()
            stats['total_leads'] = leads_result.count or 0
            
            # Contar conversaciones
            conversations_result = self.supabase.table('conversations').select("id", count='exact').execute()
            stats['total_conversations'] = conversations_result.count or 0
            
            # Leads de alta calidad (score >= 80)
            high_quality_result = self.supabase.table('leads').select("id", count='exact').gte('lead_score', 80).execute()
            stats['high_quality_leads'] = high_quality_result.count or 0
            
            return stats
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}