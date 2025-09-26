"""
Sistema de contexto para la IA
Controla memoria de conversación, seguimiento de temas y personalización
Incluye persistencia en base de datos con Supabase
"""

from typing import Dict, List, Optional, Any, Union
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class MessageType(Enum):
    """Tipos de mensajes en la conversación"""
    USER_TEXT = "user_text"
    USER_AUDIO = "user_audio"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_INFO = "system_info"
    LEAD_UPDATE = "lead_update"

class ConversationPhase(Enum):
    """Fases de la conversación de ventas"""
    INTRODUCTION = "introduction"
    DISCOVERY = "discovery"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"

@dataclass
class ConversationMessage:
    """Mensaje individual en la conversación"""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    message_type: MessageType
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        result = asdict(self)
        # Convertir MessageType enum a string para serialización JSON
        result['message_type'] = self.message_type.value
        return result

@dataclass
class ConversationSummary:
    """Resumen de puntos clave de la conversación"""
    key_points: List[str]
    mentioned_needs: List[str]
    objections_raised: List[str]
    interests_shown: List[str]
    next_actions: List[str]
    last_updated: float

@dataclass
class ConversationContext:
    """Contexto completo de la conversación"""
    session_id: str
    lead_id: str
    start_time: float
    last_activity: float
    current_phase: ConversationPhase
    messages: List[ConversationMessage]
    summary: ConversationSummary
    lead_info: Dict[str, Any]
    total_interactions: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'session_id': self.session_id,
            'lead_id': self.lead_id,
            'start_time': self.start_time,
            'last_activity': self.last_activity,
            'current_phase': self.current_phase.value,
            'messages': [msg.to_dict() for msg in self.messages],
            'summary': asdict(self.summary),
            'lead_info': self.lead_info,
            'total_interactions': self.total_interactions
        }

class ContextManager:
    """Gestor principal del contexto de conversación con persistencia en BD"""
    
    def __init__(self, max_context_messages: int = 20, db_client: Optional[Any] = None):
        self.max_context_messages = max_context_messages
        self.current_context: Optional[ConversationContext] = None
        self.contexts_cache: Dict[str, ConversationContext] = {}
        self.db_client = db_client  # Cliente de Supabase
    
    def start_new_conversation(self, lead_id: Optional[str] = None) -> str:
        """Iniciar una nueva conversación"""
        import uuid
        session_id = f"session_{int(time.time() * 1000)}"
        current_time = time.time()
        
        # Generar lead_id como UUID válido si no se proporciona
        effective_lead_id = lead_id or str(uuid.uuid4())
        
        self.current_context = ConversationContext(
            session_id=session_id,
            lead_id=effective_lead_id,
            start_time=current_time,
            last_activity=current_time,
            current_phase=ConversationPhase.INTRODUCTION,
            messages=[],
            summary=ConversationSummary(
                key_points=[],
                mentioned_needs=[],
                objections_raised=[],
                interests_shown=[],
                next_actions=[],
                last_updated=current_time
            ),
            lead_info={},
            total_interactions=0
        )
        
        return session_id
    
    def add_message(self, role: str, content: str, message_type: MessageType = MessageType.USER_TEXT, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Agregar un mensaje al contexto actual"""
        if not self.current_context:
            self.start_new_conversation()
        
        # Verificar que current_context existe después de la inicialización
        assert self.current_context is not None
        
        message_id = f"msg_{len(self.current_context.messages)}_{int(time.time() * 1000)}"
        
        message = ConversationMessage(
            id=message_id,
            role=role,
            content=content,
            message_type=message_type,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        self.current_context.messages.append(message)
        self.current_context.last_activity = time.time()
        self.current_context.total_interactions += 1
        
        # Nota: Los mensajes se guardarán cuando se guarde la conversación completa
        # NO se guardan mensajes individuales
        
        # Mantener solo los últimos mensajes para el contexto
        if len(self.current_context.messages) > self.max_context_messages * 2:
            # Conservar los primeros mensajes (introducción) y los más recientes
            introduction_messages = self.current_context.messages[:3]
            recent_messages = self.current_context.messages[-self.max_context_messages:]
            self.current_context.messages = introduction_messages + recent_messages
        
        return message_id
    
    def update_lead_info(self, new_info: Dict[str, Any]) -> None:
        """Actualizar información del lead"""
        if not self.current_context:
            return
            
        # Merge profundo de la información
        self._deep_update(self.current_context.lead_info, new_info)
        
        # Guardar/actualizar lead en BD si está disponible
        if self.db_client:
            self._save_or_update_lead_in_db(new_info)
        
        # Agregar mensaje del sistema sobre actualización
        self.add_message(
            role="system",
            content=f"Lead information updated: {list(new_info.keys())}",
            message_type=MessageType.LEAD_UPDATE,
            metadata={"updated_fields": list(new_info.keys())}
        )
    
    def save_conversation_to_db(self) -> Optional[str]:
        """Guardar conversación completa en la base de datos"""
        if not self.current_context or not self.db_client:
            return None
        
        try:
            # Verificar si la conversación ya existe
            existing_conversation = self.db_client.get_conversation(self.current_context.session_id)
            
            if existing_conversation:
                # La conversación ya existe, no necesitamos crear una nueva
                print(f"Conversación ya existe en BD: {existing_conversation['id']}")
                return existing_conversation['id']
            else:
                # Crear nueva conversación
                conversation_id = self.db_client.save_conversation(
                    self.current_context.session_id,
                    self.current_context.to_dict()
                )
                print(f"Conversación guardada en BD: {conversation_id}")
                return conversation_id
                
        except Exception as e:
            print(f"Error guardando conversación: {e}")
            return None
    
    def load_conversation_from_db(self, session_id: str) -> bool:
        """Cargar conversación desde la base de datos"""
        if not self.db_client:
            return False
        
        try:
            conversation_data = self.db_client.get_conversation(session_id)
            if not conversation_data:
                return False
            
            # Reconstruir el contexto desde los datos de BD
            context_data = json.loads(conversation_data.get('conversation_data', '{}'))
            
            messages = []
            for msg_data in context_data.get('messages', []):
                # Manejar tanto string como enum para message_type
                msg_type = msg_data['message_type']
                if isinstance(msg_type, str):
                    message_type = MessageType(msg_type)
                else:
                    message_type = msg_type
                    
                message = ConversationMessage(
                    id=msg_data['id'],
                    role=msg_data['role'],
                    content=msg_data['content'],
                    message_type=message_type,
                    timestamp=msg_data['timestamp'],
                    metadata=msg_data.get('metadata', {})
                )
                messages.append(message)
            
            summary_data = context_data.get('summary', {})
            summary = ConversationSummary(
                key_points=summary_data.get('key_points', []),
                mentioned_needs=summary_data.get('mentioned_needs', []),
                objections_raised=summary_data.get('objections_raised', []),
                interests_shown=summary_data.get('interests_shown', []),
                next_actions=summary_data.get('next_actions', []),
                last_updated=summary_data.get('last_updated', time.time())
            )
            
            self.current_context = ConversationContext(
                session_id=context_data['session_id'],
                lead_id=context_data['lead_id'],
                start_time=context_data['start_time'],
                last_activity=context_data['last_activity'],
                current_phase=ConversationPhase(context_data['current_phase']),
                messages=messages,
                summary=summary,
                lead_info=context_data.get('lead_info', {}),
                total_interactions=context_data.get('total_interactions', 0)
            )
            
            print(f"Conversación cargada desde BD: {session_id}")
            return True
            
        except Exception as e:
            print(f"Error cargando conversación: {e}")
            return False
    
    def get_conversation_context_for_ai(self) -> Dict[str, Any]:
        """Obtener contexto optimizado para el modelo de IA"""
        if not self.current_context:
            return {}
        
        # Crear resumen del contexto
        context_summary = {
            "conversation_phase": self.current_context.current_phase.value,
            "total_interactions": self.current_context.total_interactions,
            "conversation_duration_minutes": (time.time() - self.current_context.start_time) / 60,
            "lead_info": self.current_context.lead_info,
            "summary": asdict(self.current_context.summary)
        }
        
        # Mensajes recientes para contexto inmediato
        recent_messages = self.current_context.messages[-self.max_context_messages:]
        context_messages = []
        
        for msg in recent_messages:
            if msg.message_type in [MessageType.USER_TEXT, MessageType.USER_AUDIO, MessageType.AGENT_RESPONSE]:
                context_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                })
        
        return {
            "context_summary": context_summary,
            "recent_messages": context_messages,
            "conversation_insights": self._generate_conversation_insights()
        }
    
    def analyze_conversation_phase(self) -> ConversationPhase:
        """Analizar y determinar la fase actual de la conversación"""
        if not self.current_context or len(self.current_context.messages) < 2:
            return ConversationPhase.INTRODUCTION
        
        # Obtener últimos mensajes del usuario
        user_messages = [
            msg.content.lower() for msg in self.current_context.messages[-6:]
            if msg.role == "user"
        ]
        
        conversation_text = " ".join(user_messages)
        
        # Palabras clave para cada fase
        phase_keywords = {
            ConversationPhase.INTRODUCTION: ["hola", "buenos días", "me llamo", "soy", "empresa"],
            ConversationPhase.DISCOVERY: ["necesito", "problema", "buscamos", "queremos", "ayuda"],
            ConversationPhase.QUALIFICATION: ["presupuesto", "timeline", "cuándo", "inversión", "costo"],
            ConversationPhase.PRESENTATION: ["cómo funciona", "características", "beneficios", "demo"],
            ConversationPhase.OBJECTION_HANDLING: ["pero", "sin embargo", "preocupa", "duda", "no estoy seguro"],
            ConversationPhase.CLOSING: ["empezar", "contratar", "siguiente paso", "propuesta", "reunión"],
            ConversationPhase.FOLLOW_UP: ["después", "próxima", "contactar", "llamar", "email"]
        }
        
        # Contar matches para cada fase
        phase_scores = {}
        for phase, keywords in phase_keywords.items():
            score = sum(1 for keyword in keywords if keyword in conversation_text)
            phase_scores[phase] = score
        
        # Determinar fase con mayor puntuación
        if phase_scores:
            detected_phase = max(phase_scores.items(), key=lambda x: x[1])[0]
            self.current_context.current_phase = detected_phase
            return detected_phase
        
        return self.current_context.current_phase
    
    def update_conversation_summary(self) -> None:
        """Actualizar el resumen de la conversación"""
        if not self.current_context or len(self.current_context.messages) < 3:
            return
        
        # Analizar mensajes recientes del usuario
        recent_user_messages = [
            msg.content for msg in self.current_context.messages[-10:]
            if msg.role == "user"
        ]
        
        if not recent_user_messages:
            return
        
        # Extraer información clave usando análisis simple
        conversation_text = " ".join(recent_user_messages).lower()
        
        # Detectar necesidades mencionadas
        need_keywords = ["necesito", "necesitamos", "buscamos", "queremos", "requiero"]
        for keyword in need_keywords:
            if keyword in conversation_text:
                # Extraer contexto alrededor de la palabra clave
                sentences = conversation_text.split(".")
                for sentence in sentences:
                    if keyword in sentence and sentence.strip() not in self.current_context.summary.mentioned_needs:
                        self.current_context.summary.mentioned_needs.append(sentence.strip())
        
        # Detectar objeciones
        objection_keywords = ["pero", "sin embargo", "problema", "preocupa", "duda"]
        for keyword in objection_keywords:
            if keyword in conversation_text:
                sentences = conversation_text.split(".")
                for sentence in sentences:
                    if keyword in sentence and sentence.strip() not in self.current_context.summary.objections_raised:
                        self.current_context.summary.objections_raised.append(sentence.strip())
        
        self.current_context.summary.last_updated = time.time()
    
    def get_personalized_prompt_context(self) -> str:
        """Generar contexto personalizado para el prompt del AI"""
        if not self.current_context:
            return ""
        
        context_parts = []
        
        # Información básica
        if self.current_context.lead_info:
            personal = self.current_context.lead_info.get('personal', {})
            if personal.get('nombre'):
                context_parts.append(f"El cliente se llama {personal['nombre']}")
            if personal.get('empresa'):
                context_parts.append(f"representa a la empresa {personal['empresa']}")
            if personal.get('cargo'):
                context_parts.append(f"y trabaja como {personal['cargo']}")
        
        # Fase actual
        phase_messages = {
            ConversationPhase.INTRODUCTION: "Estamos en la fase de introducción",
            ConversationPhase.DISCOVERY: "Estamos explorando sus necesidades",
            ConversationPhase.QUALIFICATION: "Estamos calificando el prospecto",
            ConversationPhase.PRESENTATION: "Estamos presentando soluciones",
            ConversationPhase.OBJECTION_HANDLING: "Estamos manejando objeciones",
            ConversationPhase.CLOSING: "Estamos en proceso de cierre",
            ConversationPhase.FOLLOW_UP: "Estamos en seguimiento"
        }
        
        context_parts.append(phase_messages.get(self.current_context.current_phase, ""))
        
        # Necesidades identificadas
        if self.current_context.summary.mentioned_needs:
            needs = ", ".join(self.current_context.summary.mentioned_needs[:3])
            context_parts.append(f"Han mencionado estas necesidades: {needs}")
        
        # Objeciones identificadas
        if self.current_context.summary.objections_raised:
            objections = ", ".join(self.current_context.summary.objections_raised[:2])
            context_parts.append(f"Han expresado estas preocupaciones: {objections}")
        
        return ". ".join(filter(None, context_parts)) + "." if context_parts else ""
    
    # ==========================================
    # MÉTODOS AUXILIARES PARA BASE DE DATOS
    # ==========================================
    
    def _save_message_to_db(self, message: ConversationMessage) -> None:
        """Guardar mensaje individual en la base de datos"""
        if not self.db_client or not self.current_context:
            return
        
        try:
            # Buscar o crear conversation_id en BD
            conversation = self.db_client.get_conversation(self.current_context.session_id)
            if not conversation:
                # Crear conversación si no existe
                conversation_id = self.db_client.save_conversation(
                    self.current_context.session_id,
                    self.current_context.to_dict()
                )
            else:
                conversation_id = conversation['id']
            
            # Preparar datos del mensaje para BD
            message_data = {
                'conversation_id': conversation_id,
                'message_type': message.role,
                'content': message.content,
                'intent': message.metadata.get('intent') if message.metadata else None,
                'sentiment': message.metadata.get('sentiment') if message.metadata else None,
                'confidence_score': message.metadata.get('confidence') if message.metadata else None,
                'extracted_info': json.dumps(message.metadata) if message.metadata else None,
                'timestamp': datetime.fromtimestamp(message.timestamp).isoformat(),
                'processing_time_ms': message.metadata.get('processing_time_ms') if message.metadata else None
            }
            
            # Insertar en BD (asumiendo que existe una tabla messages)
            # self.db_client.supabase.table('messages').insert(message_data).execute()
            
        except Exception as e:
            print(f"Error guardando mensaje en BD: {e}")
    
    def _save_or_update_lead_in_db(self, lead_info: Dict[str, Any]) -> None:
        """Guardar o actualizar lead en la base de datos"""
        if not self.db_client or not self.current_context:
            return
        
        try:
            # Verificar si el lead ya existe
            existing_lead = self.db_client.get_lead(self.current_context.lead_id)
            
            if existing_lead:
                # Actualizar lead existente
                self.db_client.update_lead(self.current_context.lead_id, lead_info)
            else:
                # Crear nuevo lead con el lead_id actual
                lead_data_with_id = {**lead_info}
                new_lead_id = self.db_client.create_lead(lead_data_with_id)
                
                # Si se creó exitosamente, actualizar el lead_id en el contexto
                if new_lead_id:
                    self.current_context.lead_id = new_lead_id
                    print(f"Lead creado en BD con ID: {new_lead_id}")
                
        except Exception as e:
            print(f"Error guardando lead en BD: {e}")
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Actualización profunda de diccionarios anidados"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _generate_conversation_insights(self) -> Dict[str, Any]:
        """Generar insights de la conversación para el AI"""
        if not self.current_context:
            return {}
        
        insights = {
            "engagement_level": "high" if self.current_context.total_interactions > 5 else "medium" if self.current_context.total_interactions > 2 else "low",
            "response_frequency": len([msg for msg in self.current_context.messages if msg.role == "user"]),
            "conversation_length": len(self.current_context.messages),
            "last_user_message_time": None,
            "conversation_phase": self.current_context.current_phase.value,
            "key_topics_mentioned": len(self.current_context.summary.mentioned_needs),
            "objections_count": len(self.current_context.summary.objections_raised)
        }
        
        # Tiempo del último mensaje del usuario
        user_messages = [msg for msg in self.current_context.messages if msg.role == "user"]
        if user_messages:
            insights["last_user_message_time"] = user_messages[-1].timestamp
        
        return insights
    
    # ==========================================
    # COMPATIBILIDAD CON ARCHIVOS
    # ==========================================
    
    def save_context(self, filepath: str = None) -> bool:
        """Guardar contexto actual a archivo"""
        if not self.current_context:
            return False
        
        try:
            if not filepath:
                filepath = f"context_{self.current_context.session_id}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_context.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving context: {e}")
            return False
    
    def load_context(self, filepath: str) -> bool:
        """Cargar contexto desde archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruir el contexto
            messages = []
            for msg_data in data['messages']:
                message = ConversationMessage(
                    id=msg_data['id'],
                    role=msg_data['role'],
                    content=msg_data['content'],
                    message_type=MessageType(msg_data['message_type']),
                    timestamp=msg_data['timestamp'],
                    metadata=msg_data.get('metadata', {})
                )
                messages.append(message)
            
            summary = ConversationSummary(**data['summary'])
            
            self.current_context = ConversationContext(
                session_id=data['session_id'],
                lead_id=data['lead_id'],
                start_time=data['start_time'],
                last_activity=data['last_activity'],
                current_phase=ConversationPhase(data['current_phase']),
                messages=messages,
                summary=summary,
                lead_info=data['lead_info'],
                total_interactions=data['total_interactions']
            )
            
            return True
        except Exception as e:
            print(f"Error loading context: {e}")
            return False