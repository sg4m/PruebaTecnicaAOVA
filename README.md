# 🤖 AI Voice Agent para Lead Generation

Un asistente de IA conversacional por voz que califica leads automáticamente mediante conversaciones naturales, con integración completa de base de datos y analytics en tiempo real.

## 🌟 Características Principales

- 🗣️ **Conversación por voz natural** (Speech-to-Text + Text-to-Speech)
- 🤖 **IA conversacional avanzada** con Google Gemini
- 📊 **Extracción automática de leads** con scoring inteligente (0-100 puntos)
- 🧠 **Gestión de contexto** con 7 fases de conversación de ventas
- 🗄️ **Base de datos Supabase** para persistencia completa
- 📈 **Analytics profesional** con métricas en tiempo real
- 🔄 **Modo offline** funcional sin base de datos

## 🎯 Demo en Vivo

- **Interface Web:** Streamlit con controles de voz intuitivos
- **Conversación Natural:** Habla con el agente como con una persona real
- **Análisis Automático:** Obtén puntuación y categorización de leads al instante
- **Dashboard en Vivo:** Métricas y estadísticas actualizadas en tiempo real

---

## 🛠️ Instalación Rápida

### Prerrequisitos
- Python 3.9+ 
- Cuenta de Google (para API de Gemini)
- Cuenta de Supabase (opcional, funciona sin BD)

### 1. Clonar el repositorio
```bash
git clone https://github.com/sg4m/PruebaTecnicaAOVA

```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
```

**Contenido mínimo de `.env`:**
```bash
# OBLIGATORIO - Obtener en https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=tu_google_api_key_aqui

# OPCIONAL - Para base de datos (funciona sin esto)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_supabase_anon_key_aqui
```

### 5. Ejecutar la aplicación
```bash
streamlit run app.py
```

**¡Listo! 🎉** 

---

## ⚡ Uso Rápido (Sin Base de Datos)

### Configuración Mínima
Solo necesitas configurar `GOOGLE_API_KEY` en `.env` para empezar:

1. **Obtén API Key de Google Gemini:**
   - Ve a https://aistudio.google.com/app/apikey
   - Crea una nueva API key
   - Cópiala a tu archivo `.env`

2. **Ejecutar:**
```bash
streamlit run app.py
```

3. **Usar el agente:**
   - Haz clic en "🎤 Grabar Audio" 
   - Habla naturalmente sobre tus necesidades de negocio
   - Ve los resultados en tiempo real
   - El agente extraerá información y puntuará automáticamente el lead

---

## 🗄️ Configuración Completa con Base de Datos

### Paso 1: Configurar Supabase

1. **Crear cuenta en [Supabase](https://supabase.com)**
2. **Crear nuevo proyecto**
3. **Ejecutar schema de base de datos:**
   - Ve a SQL Editor en Supabase
   - Ejecuta el contenido de `database_schema.sql`
4. **Obtener credenciales:**
   - Ve a Settings > API
   - Copia URL y anon key a tu `.env`

### Paso 2: Probar integración
```bash
python test_database_integration.py
```

### Paso 3: Corrección de permisos (si es necesario)
Si ves errores de Row Level Security:
- Ejecuta `fix_rls_policies.sql` en Supabase SQL Editor

---

## 🎮 Cómo Usar la Aplicación

### Interfaz Principal

#### 🎤 Conversación por Voz
1. **Hacer clic en "🎤 Grabar Audio"**
2. **Hablar naturalmente** sobre tu negocio, necesidades, presupuesto, etc.
3. **Ver transcripción** automática de tu voz
4. **Escuchar respuesta** del agente IA
5. **Continuar conversación** hasta obtener información completa

#### 💬 Chat de Texto (Opcional)
- Escribir mensaje en el campo de texto
- Presionar Enter o hacer clic en "Enviar"
- Ver respuesta inmediata del agente

#### 📊 Analytics en Sidebar
- **Estado del Agente:** Verificar que todos los componentes funcionen
- **Base de Datos:** Estadísticas en tiempo real si está configurada
- **Información del Lead:** Análisis automático con puntuación
- **Contexto Inteligente:** Fase actual de conversación y métricas

### Ejemplo de Conversación

```
👤 Usuario: "Hola, soy María García, directora de TI de TechInnovate"

🤖 Agente: "¡Hola María! Encantado de conocerte. ¿En qué puedo ayudarte hoy?"

👤 Usuario: "Necesitamos automatizar nuestros procesos, tenemos 100 empleados"

🤖 Agente: "Perfecto, la automatización puede generar grandes beneficios. 
¿Podrías contarme más sobre qué procesos específicos quieren automatizar?"

👤 Usuario: "Principalmente facturación y gestión de inventario. Nuestro presupuesto es de 50,000 EUR"

🤖 Agente: "Excelente, ese presupuesto permite implementar soluciones robustas. 
¿Cuál es su timeline ideal para la implementación?"

📊 RESULTADO: Lead con puntuación 88/100 - Alta prioridad
```

---

## 🧪 Testing y Verificación

### Tests Disponibles

```bash
# Test básico de extracción de leads
python test_lead_extraction.py

# Test completo del sistema
python test_complete_system.py

# Test de base de datos (requiere Supabase configurado)
python test_database_integration.py

# Test específico de context manager + BD
python test_context_with_db.py

# Test simple de conexión BD
python test_database_simple.py
```

### Verificar Funcionalidad

#### ✅ Sin Base de Datos
```bash
python test_complete_system.py
```
Debe mostrar: conversación exitosa y extracción de leads funcionando.

#### ✅ Con Base de Datos
```bash
python test_database_integration.py
```
Debe mostrar: creación de leads, conversaciones guardadas, analytics funcionando.

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### ❌ "Error inicializando Gemini"
- **Causa:** API Key de Google incorrecta o faltante
- **Solución:** Verifica `GOOGLE_API_KEY` en `.env`
- **Test:** `python -c "from src.ai.gemini_client import GeminiClient; GeminiClient()"`

#### ❌ "Error en Speech-to-Text"  
- **Causa:** Problemas con micrófono o PyAudio
- **Solución Windows:** `pip install pipwin && pipwin install pyaudio`
- **Solución macOS:** `brew install portaudio && pip install pyaudio`

#### ❌ "Base de datos no disponible"
- **Causa:** Credenciales Supabase incorrectas (opcional)
- **Solución:** Verificar `SUPABASE_URL` y `SUPABASE_KEY` en `.env`
- **Nota:** La aplicación funciona perfectamente sin BD

#### ❌ "Row Level Security Policy"
- **Causa:** Permisos de Supabase restrictivos
- **Solución:** Ejecutar `fix_rls_policies.sql` en Supabase SQL Editor

#### ❌ "Streamlit no encontrado"
- **Causa:** Dependencias no instaladas correctamente
- **Solución:** `pip install -r requirements.txt`

### Logs de Debug
```bash
# Activar logs detallados
export PYTHONPATH=$PWD/src
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
streamlit run app.py
```

---

## 📁 Estructura del Proyecto

```
ai-voice-agent/
├── app.py                          # 🚀 Aplicación principal Streamlit
├── requirements.txt                # 📦 Dependencias Python
├── database_schema.sql             # 🗄️ Esquema completo de BD
├── fix_rls_policies.sql           # 🔧 Corrección permisos Supabase
├── .env.example                   # ⚙️ Plantilla de configuración
├── DATABASE_GUIDE.md              # 📖 Guía detallada de BD
├── src/
│   ├── ai/
│   │   ├── gemini_client.py       # 🤖 Cliente IA con extracción de leads
│   │   └── context_manager.py     # 🧠 Gestión inteligente de contexto
│   ├── audio/
│   │   ├── speech_to_text.py      # 🎤 Reconocimiento de voz
│   │   └── text_to_speech.py      # 🔊 Síntesis de voz
│   ├── database/
│   │   └── supabase_client.py     # 🗄️ Cliente completo de BD
│   └── utils/
│       └── config.py              # ⚙️ Configuración centralizada
└── tests/
    ├── test_lead_extraction.py    # 🧪 Test extracción de leads
    ├── test_complete_system.py    # 🧪 Test sistema completo
    ├── test_database_integration.py # 🧪 Test integración BD
    └── test_context_with_db.py    # 🧪 Test context + BD
```

---

## 🎯 Características Técnicas

### Componentes Principales

- **🤖 Motor IA:** Google Gemini (models/gemini-flash-latest)
- **🎤 ASR:** Google Speech Recognition
- **🔊 TTS:** pyttsx3 + Google Cloud TTS opcional
- **🗄️ Base de Datos:** Supabase (PostgreSQL)
- **🖥️ Interface:** Streamlit
- **🧠 Context Management:** Sistema propio con 7 fases de conversación

### Flujo de Conversación

1. **Introducción** - Saludo y presentación inicial
2. **Descubrimiento** - Exploración de necesidades
3. **Cualificación** - Validación de presupuesto y autoridad
4. **Presentación** - Mostrar soluciones relevantes
5. **Manejo de Objeciones** - Resolver dudas y preocupaciones
6. **Cierre** - Definir próximos pasos
7. **Seguimiento** - Planificar contacto futuro

### Métricas Automáticas

- **Lead Score:** 0-100 puntos basado en completitud y calidad
- **Categorización:** High/Medium/Low priority automática
- **Engagement:** Análisis de participación en conversación
- **Fase Detection:** Identificación automática de etapa actual
- **Analytics:** Distribución por calidad, conversiones por fase

---

## 🚀 Casos de Uso

### Para Empresas de Software B2B
- Calificación automática de leads entrantes
- Reducción de carga en equipo de ventas
- Mejora en calidad de leads pasados a sales

### Para Consultorías
- Evaluación inicial de necesidades de clientes
- Segmentación automática por tamaño y presupuesto
- Personalización de propuestas basada en conversación

### Para Agencias de Marketing
- Lead generation automatizada 24/7  
- Análisis de sentiment y objeciones comunes
- Optimización de scripts de ventas basada en datos

---

## 📝 Licencia

Este proyecto está bajo la licencia de Santiago Gamborino Morales © 2025

---

## 💡 Soporte

¿Problemas o preguntas?

1. **Issues:** Abre un issue en GitHub con detalles del problema
2. **Documentación:** Revisa `DATABASE_GUIDE.md` para BD
3. **Tests:** Ejecuta `python test_complete_system.py` para diagnóstico
4. **Logs:** Verifica la consola de Streamlit para errores detallados

---

## 🏆 Créditos

Desarrollado con ❤️ usando:
- [Google Gemini](https://ai.google.dev/) para IA conversacional
- [Streamlit](https://streamlit.io/) para interface web
- [Supabase](https://supabase.com/) para base de datos
- [PyAudio](https://pypi.org/project/PyAudio/) para procesamiento de audio

---

**¡Comienza a generar leads inteligentemente! 🚀**
