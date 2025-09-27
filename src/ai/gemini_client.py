import google.generativeai as genai
from typing import Dict, List, Optional
import json
from src.utils.config import Config

class GeminiClient:
    """Cliente para interactuar con Google Gemini API - Versión simplificada sin funcionalidad de leads"""
    
    def __init__(self):
        """Inicializar el cliente de Gemini"""
        self.configure_client()
        
        # Intentar con diferentes modelos disponibles
        available_models = [
            "models/gemini-flash-latest",
            "models/gemini-pro-latest", 
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro-latest",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash"
        ]
        
        self.model = None
        for model_name in available_models:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ Modelo inicializado correctamente: {model_name}")
                break
            except Exception as e:
                print(f"❌ Error con modelo {model_name}: {e}")
                continue
        
        if self.model is None:
            raise Exception("No se pudo inicializar ningún modelo de Gemini disponible")
        
    def configure_client(self):
        """Configurar la API key de Gemini"""
        # Asegurar que usamos Google AI Studio, no Vertex AI
        import os
        os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)  # Remover credenciales de Vertex AI
        genai.configure(api_key=Config.GOOGLE_API_KEY)
    
    def generate_response(self, user_message: str, context: List[Dict] = None, context_manager = None) -> str:
        """
        Generar respuesta usando Gemini con contexto inteligente
        
        Args:
            user_message: Mensaje del usuario
            context: Historial de conversación para contexto (fallback)
            context_manager: Gestor de contexto inteligente
            
        Returns:
            Respuesta generada por Gemini
        """
        try:
            # Construir prompt con contexto inteligente
            prompt = self._build_prompt(user_message, context, context_manager)
            
            # Generar respuesta
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': Config.MAX_TOKENS,
                    'temperature': Config.TEMPERATURE,
                }
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Lo siento, hubo un problema al procesar tu mensaje. ¿Podrías intentarlo de nuevo?"
    
    def _build_prompt(self, user_message: str, context: List[Dict] = None, context_manager = None) -> str:
        """Construir prompt con contexto inteligente y personalidad del agente"""
        
        system_prompt = """
        Eres un agente de atención al cliente inteligente y amigable. Tu objetivo es:
        
        1. Ser amigable, profesional y servicial
        2. Responder preguntas de manera clara y útil
        3. Mantener conversaciones naturales y fluidas
        4. Proporcionar información valiosa cuando sea apropiado
        5. Guiar las conversaciones de manera positiva
        
        REGLAS IMPORTANTES:
        - Mantén un tono conversacional y natural
        - Sé específico y útil en tus respuestas
        - Usa el contexto previo para crear continuidad
        - Haz preguntas relevantes cuando sea apropiado
        - Siempre busca ser útil y resolver dudas
        
        Si el usuario pregunta sobre servicios o productos, ofrece información general útil y pregunta cómo puedes ayudar más específicamente.
        
        NUNCA uses frases como "[Tu Nombre]" o placeholders similares.
        """
        
        # Contexto inteligente del Context Manager
        intelligent_context = ""
        if context_manager:
            try:
                personalized_context = context_manager.get_personalized_prompt_context()
                if personalized_context:
                    intelligent_context = f"\nCONTEXTO PERSONALIZADO: {personalized_context}\n"
            except:
                # Si hay error con context_manager, continuar sin él
                pass
        
        # Contexto de conversación previa (fallback)
        conversation_context = ""
        if context and len(context) > 0:
            conversation_context = "Contexto reciente:\n"
            for msg in context[-4:]:  # Solo los últimos 4 mensajes
                role = "Usuario" if msg['role'] == 'user' else "Agente"
                conversation_context += f"{role}: {msg['content']}\n"
            conversation_context += "\n"
        
        return f"{system_prompt}{intelligent_context}\n{conversation_context}Usuario: {user_message}\n\nAgente:"