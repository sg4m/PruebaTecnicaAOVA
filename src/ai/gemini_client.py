import google.generativeai as genai
from typing import Dict, List, Optional
import json
from src.utils.config import Config

class GeminiClient:
    """Cliente para interactuar con Google Gemini API"""
    
    def __init__(self):
        """Inicializar el cliente de Gemini"""
        self.configure_client()
        
        # Intentar con diferentes modelos disponibles (basado en tu lista real)
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
                print(f"Modelo inicializado correctamente: {model_name}")
                break
            except Exception as e:
                print(f"Error con modelo {model_name}: {e}")
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
    
    def extract_lead_info(self, conversation_history: List[Dict]) -> Dict:
        """
        Extraer información del lead de la conversación con análisis avanzado

        """
        try:
            # Construir texto de conversación
            messages_text = "\n".join([
                f"{'Cliente' if msg['role'] == 'user' else 'Agente'}: {msg['content']}"
                for msg in conversation_history
            ])
            
            extraction_prompt = f"""
            Analiza esta conversación y extrae información del prospecto en JSON compacto.

            CONVERSACIÓN:
            {messages_text}

            Extrae SOLO información mencionada explícitamente. Si no se menciona, usa null.

            Responde ÚNICAMENTE con este JSON (SIN texto adicional):
            {{
                "personal": {{
                    "nombre": null,
                    "cargo": null,
                    "empresa": null,
                    "industria": null
                }},
                "contacto": {{
                    "email": null,
                    "telefono": null
                }},
                "necesidades": {{
                    "descripcion": null,
                    "urgencia": "baja",
                    "problemas": null
                }},
                "comercial": {{
                    "presupuesto": null,
                    "timeline": null,
                    "decision_maker": false,
                    "autoridad": "baja"
                }},
                "score": {{
                    "total": 0,
                    "categoria": "sin_evaluar"
                }}
            }}

            Calcula score (0-100): +30 por contacto, +25 por necesidades claras, +25 por presupuesto, +20 por interés alto.
            """
            
            response = self.model.generate_content(
                extraction_prompt,
                generation_config={
                    'max_output_tokens': 2048,
                    'temperature': 0.1,
                },
                safety_settings={
                    'HARASSMENT': 'BLOCK_NONE',
                    'HATE_SPEECH': 'BLOCK_NONE',
                    'SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'DANGEROUS_CONTENT': 'BLOCK_NONE'
                }
            )
            
            # Verificar si la respuesta es válida
            if not response.candidates or not response.candidates[0].content.parts:
                print(f"Respuesta bloqueada por safety filter. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'desconocido'}")
                return self._get_empty_lead_structure()
            
            # Limpiar y parsear respuesta JSON
            return self._parse_json_response(response.text)
                
        except Exception as e:
            print(f"Error extracting lead info: {e}")
            if "finish_reason" in str(e):
                print("La conversación fue bloqueada por filtros de seguridad de Gemini")
            return self._get_empty_lead_structure()

    def analyze_lead_quality(self, lead_info: Dict) -> Dict:
        """
        Analizar la calidad del lead y generar recomendaciones

        """
        try:
            # Obtener puntuación existente (nueva estructura compacta)
            score = lead_info.get('score', {}).get('total', 0)
            if score == 0:
                # Fallback: estructura anterior
                score = lead_info.get('puntuacion_lead', {}).get('score_total', 0)
            
            # Análisis basado en puntuación
            if score >= 80:
                quality = "A - Prospecto"
                priority = "ALTA"
                next_steps = [
                    "Programar demo/reunión inmediata",
                    "Enviar propuesta personalizada",
                    "Asignar account manager dedicado"
                ]
            elif score >= 60:
                quality = "B - Lead medio"
                priority = "MEDIA"
                next_steps = [
                    "Obtener información de contacto faltante",
                    "Aclarar necesidades específicas",
                    "Programar llamada de seguimiento"
                ]
            elif score >= 40:
                priority = "BAJA"
                quality = "C - Lead bajo"
                next_steps = [
                    "Nurturing con contenido de valor",
                    "Identificar pain points específicos",
                    "Generar más confianza y rapport"
                ]
            else:
                quality = "D - Lead sin calificacion"
                priority = "MUY BAJA"
                next_steps = [
                    "Calificar mejor el presupuesto",
                    "Identificar autoridad de compra",
                    "Evaluar fit real del producto"
                ]
            
            return {
                "quality_grade": quality,
                "priority": priority,
                "score": score,
                "next_steps": next_steps,
                "missing_info": self._identify_missing_info(lead_info),
                "strengths": self._identify_lead_strengths(lead_info),
                "concerns": self._identify_concerns(lead_info)
            }
            
        except Exception as e:
            print(f"Error analyzing lead quality: {e}")
            return {"quality_grade": "Error", "priority": "REVISAR", "score": 0}

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parsear respuesta JSON con manejo robusto de errores y recuperación automática"""
        try:
            # Limpiar respuesta
            json_text = response_text.strip()
            
            # Remover markdown code blocks
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            elif json_text.startswith("```"):
                json_text = json_text[3:]
                
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            # Intentar parsear JSON
            extracted_info = json.loads(json_text)
            
            # Validar estructura y limpiar valores null/vacíos
            return self._clean_extracted_info(extracted_info)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Intentando recuperación automática del JSON...")
            
            # Estrategia de recuperación: intentar extraer información parcial
            recovered_info = self._recover_partial_json(response_text)
            if recovered_info:
                print("Información parcial recuperada exitosamente")
                return recovered_info
            
            print(f"No se pudo recuperar información de: {response_text[:200]}...")
            return self._get_empty_lead_structure()
    
    def _recover_partial_json(self, text: str) -> Dict:
        """Intentar recuperar información parcial de JSON malformado"""
        try:
            import re
            
            # Inicializar estructura de lead
            recovered = self._get_empty_lead_structure()
            
            # Patrones de extracción manual como fallback
            patterns = {
                'nombre': r'"nombre"\s*:\s*"([^"]*)"',
                'empresa': r'"empresa"\s*:\s*"([^"]*)"',
                'cargo': r'"cargo"\s*:\s*"([^"]*)"',
                'email': r'"email"\s*:\s*"([^"]*)"',
                'telefono': r'"telefono"\s*:\s*"([^"]*)"',
                'presupuesto': r'"presupuesto"\s*:\s*"([^"]*)"',
                'timeline': r'"timeline"\s*:\s*"([^"]*)"',
                'descripcion': r'"descripcion"\s*:\s*"([^"]*)"',
                'score_total': r'"score_total"\s*:\s*(\d+)'
            }
            
            # Extraer información usando regex
            extracted_data = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1) if key != 'score_total' else int(match.group(1))
                    extracted_data[key] = value
            
            # Organizar información en estructura correcta
            if extracted_data:
                if 'nombre' in extracted_data or 'empresa' in extracted_data or 'cargo' in extracted_data:
                    recovered['informacion_personal'] = {
                        k: v for k, v in extracted_data.items() 
                        if k in ['nombre', 'empresa', 'cargo']
                    }
                
                if 'email' in extracted_data or 'telefono' in extracted_data:
                    recovered['contacto'] = {
                        k: v for k, v in extracted_data.items() 
                        if k in ['email', 'telefono']
                    }
                
                if 'descripcion' in extracted_data:
                    recovered['necesidades'] = {'descripcion': extracted_data['descripcion']}
                
                if 'presupuesto' in extracted_data or 'timeline' in extracted_data:
                    recovered['comercial'] = {
                        k: v for k, v in extracted_data.items() 
                        if k in ['presupuesto', 'timeline']
                    }
                
                if 'score_total' in extracted_data:
                    recovered['puntuacion_lead'] = {
                        'score_total': extracted_data['score_total'],
                        'categoria': 'recuperado_parcial'
                    }
                
                return recovered
            
            return None
            
        except Exception as e:
            print(f"Error en recuperación parcial: {e}")
            return None
    
    def _clean_extracted_info(self, info: Dict) -> Dict:
        """Limpiar información extraída removiendo valores null/vacíos"""
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items() 
                       if v is not None and v != "null" and v != ""}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d if item is not None]
            else:
                return d
        
        return clean_dict(info)
    
    def _get_empty_lead_structure(self) -> Dict:
        """Estructura vacía para lead cuando hay errores"""
        return {
            "personal": {},
            "contacto": {},
            "necesidades": {},
            "comercial": {},
            "score": {"total": 0, "categoria": "sin_datos"}
        }
    
    def _identify_missing_info(self, lead_info: Dict) -> List[str]:
        """Identificar información faltante importante"""
        missing = []
        
        # Información personal (nueva estructura)
        personal = lead_info.get('personal', {}) or lead_info.get('informacion_personal', {})
        if not personal.get('nombre'):
            missing.append("Nombre completo")
        if not personal.get('empresa'):
            missing.append("Empresa")
        if not personal.get('cargo'):
            missing.append("Cargo/Posición")
            
        # Contacto
        contacto = lead_info.get('contacto', {})
        if not contacto.get('email') and not contacto.get('telefono'):
            missing.append("Información de contacto")
            
        # Comercial
        comercial = lead_info.get('comercial', {})
        if not comercial.get('presupuesto'):
            missing.append("Presupuesto aproximado")
        if not comercial.get('timeline'):
            missing.append("Timeline del proyecto")
            
        return missing
    
    def _identify_lead_strengths(self, lead_info: Dict) -> List[str]:
        """Identificar fortalezas del lead"""
        strengths = []
        
        # Verificar diferentes aspectos
        if lead_info.get('contacto', {}).get('email'):
            strengths.append("Información de contacto disponible")
            
        if lead_info.get('necesidades', {}).get('descripcion'):
            strengths.append("Necesidades específicas identificadas")
            
        comercial = lead_info.get('comercial', {})
        if comercial.get('presupuesto'):
            strengths.append("Presupuesto mencionado")
        if comercial.get('decision_maker') == "true":
            strengths.append("Es tomador de decisiones")
            
        interes = lead_info.get('interes', {})
        if interes.get('nivel') == "alto":
            strengths.append("Alto nivel de interés")
            
        return strengths
    
    def _identify_concerns(self, lead_info: Dict) -> List[str]:
        """Identificar preocupaciones o banderas rojas"""
        concerns = []
        
        comercial = lead_info.get('comercial', {})
        if comercial.get('autoridad_compra') == "baja":
            concerns.append("Baja autoridad de compra")
            
        interes = lead_info.get('interes', {})
        if interes.get('nivel') == "bajo":
            concerns.append("Bajo nivel de interés")
        if interes.get('objeciones'):
            concerns.append("Objeciones expresadas")
            
        if not lead_info.get('contacto', {}).get('email') and not lead_info.get('contacto', {}).get('telefono'):
            concerns.append("Sin información de contacto")
            
        return concerns
    
    def _build_prompt(self, user_message: str, context: List[Dict] = None, context_manager = None) -> str:
        """Construir prompt con contexto inteligente y personalidad del agente"""
        
        system_prompt = """
        Eres un agente de ventas experto de AOVA, la plataforma líder de inteligencia artificial hecha específicamente para México. 
        Tu misión es ayudar a empresas mexicanas a transformar su operación con IA.
        
        SOBRE AOVA:
        - Somos especialistas en IA para el mercado mexicano
        - Nuestras soluciones ahorran hasta 40 horas por semana a cada equipo
        - El 89% de nuestros clientes reporta reducción en tiempos de respuesta
        - Las empresas recuperan su inversión en menos de 3 meses
        - Reducimos costos operativos hasta 30% en atención al cliente
        
        NUESTROS PRODUCTOS PRINCIPALES:
        • AOVA Pulse: Vendedor virtual con avatar realista que atiende clientes 24/7, integra con CRM/ERP/WhatsApp
        • AOVA Spark: Evalúa pitches de negocio con IA, perfecto para concursos y aceleradoras
        • AOVA Line: Agente que contesta, guía y transfiere llamadas como humano, ideal para call centers
        • AOVA Lab: Soluciones 100% personalizadas (predicción, clasificación, automatización)
        
        TU OBJETIVO COMO AGENTE:
        1. Ser amigable, profesional y enfocado en resultados reales
        2. Hacer preguntas estratégicas para entender sus retos operativos
        3. Identificar oportunidades de automatización y ahorro de tiempo/costos
        4. Recopilar información: nombre, empresa, industria, retos específicos, tamaño de equipo
        5. Demostrar valor tangible con datos y casos de éxito
        6. Guiar hacia una demostración personalizada gratuita
        
        REGLAS IMPORTANTES:
        - Preséntate como consultor de AOVA especializado en transformación con IA
        - Haz UNA pregunta específica a la vez
        - Enfócate en problemas reales: atención al cliente lenta, procesos manuales, costos altos
        - Menciona beneficios cuantificables (40 horas ahorradas, ROI en 3 meses, etc.)
        - Adapta la solución según su industria y tamaño
        - Siempre ofrece demo personalizada y gratuita
        - Usa lenguaje mexicano natural y directo
        
        CASOS DE USO POR INDUSTRIA:
        - Call Centers: AOVA Line para automatizar llamadas
        - E-commerce: AOVA Pulse para atención 24/7
        - Educación/Aceleradoras: AOVA Spark para evaluación automática
        - Cualquier empresa: AOVA Lab para automatización específica
        
        NUNCA uses placeholders genéricos. Siempre habla de AOVA específicamente.
        NUNCA uses [TU NOMBRE] como respuesta, responde con "Consultor de AOVA".
        """
        
        # Contexto inteligente del Context Manager
        intelligent_context = ""
        if context_manager:
            personalized_context = context_manager.get_personalized_prompt_context()
            if personalized_context:
                intelligent_context = f"\nCONTEXTO PERSONALIZADO: {personalized_context}\n"
        
        # Contexto de conversación previa (fallback)
        conversation_context = ""
        if context and len(context) > 0:
            conversation_context = "Contexto reciente:\n"
            for msg in context[-4:]:  # Reducido para dar espacio al contexto inteligente
                role = "Usuario" if msg['role'] == 'user' else "Agente"
                conversation_context += f"{role}: {msg['content']}\n"
            conversation_context += "\n"
        
        return f"{system_prompt}{intelligent_context}\n{conversation_context}Usuario: {user_message}\n\nAgente:"