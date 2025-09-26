                                        -- ============================================= --
                                        -- Ejecutar este script en Supabase SQL Editor   --
                                        -- ============================================= --



                                        -- =============================================
                                        -- TABLA DE LEADS O PROSPECTO
                                        -- =============================================
CREATE TABLE IF NOT EXISTS leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Información Personal
    nombre VARCHAR(255),
    cargo VARCHAR(255),
    empresa VARCHAR(255),
    industria VARCHAR(255),
    tamaño_empresa VARCHAR(100),
    
    -- Información de Contacto
    email VARCHAR(255),
    telefono VARCHAR(50),
    preferencia_contacto VARCHAR(50),
    
    -- Necesidades y Comercial
    necesidades_descripcion TEXT,
    urgencia VARCHAR(50),
    problemas_actuales TEXT,
    presupuesto VARCHAR(100),
    timeline VARCHAR(100),
    autoridad_compra BOOLEAN,
    decision_maker BOOLEAN,
    
    -- Puntuación y Clasificación
    lead_score INTEGER DEFAULT 0 CHECK (lead_score >= 0 AND lead_score <= 100),
    categoria VARCHAR(50),
    quality_grade VARCHAR(10),
    priority VARCHAR(20),
    
    -- Estado del Lead
    status VARCHAR(50) DEFAULT 'new',
    assigned_to UUID,
    
    -- Datos JSON completos
    raw_lead_data JSONB,
    
    -- Metadatos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para leads
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(lead_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_empresa ON leads(empresa);
CREATE INDEX IF NOT EXISTS idx_leads_categoria ON leads(categoria);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);

                                        -- =============================================
                                        -- TABLA DE CONVERSACIONES
                                        -- =============================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    
    -- Información de la conversación
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    total_interactions INTEGER DEFAULT 0,
    final_phase VARCHAR(100),
    messages_count INTEGER DEFAULT 0,
    
    -- Datos de resumen y contexto
    summary_data JSONB,
    conversation_data JSONB,
    
    -- Metadatos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para conversaciones
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_lead ON conversations(lead_id);
CREATE INDEX IF NOT EXISTS idx_conversations_phase ON conversations(final_phase);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

-- =============================================
-- TABLA DE MENSAJES
-- =============================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Contenido del mensaje
    message_type VARCHAR(50) NOT NULL, -- 'user' o 'assistant'
    content TEXT NOT NULL,
    audio_duration DECIMAL(5,2), -- duración en segundos si es audio
    
    -- Análisis del mensaje
    intent VARCHAR(100),
    sentiment VARCHAR(50),
    confidence_score DECIMAL(4,3),
    extracted_info JSONB,
    
    -- Metadatos
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER
);

-- Índices para mensajes
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);

                                        -- =============================================
                                        -- TABLA DE INTERACCIÓN
                                        -- =============================================
CREATE TABLE IF NOT EXISTS interaction_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    
    -- Métricas de la sesión
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    metrics_data JSONB NOT NULL,
    
    -- Metadatos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para métricas
CREATE INDEX IF NOT EXISTS idx_metrics_session ON interaction_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON interaction_metrics(timestamp DESC);

                                    -- =============================================
                                    -- TABLA DE EVENTOS DEL SISTEMA
                                    -- =============================================
CREATE TABLE IF NOT EXISTS system_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Información del evento
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Contexto del evento
    session_id VARCHAR(255),
    user_id VARCHAR(255),
    metadata JSONB,
    
    -- Severidad
    severity VARCHAR(20) DEFAULT 'info', -- info, warning, error, critical
    
    -- Metadatos
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para eventos
CREATE INDEX IF NOT EXISTS idx_events_type ON system_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_category ON system_events(event_category);
CREATE INDEX IF NOT EXISTS idx_events_severity ON system_events(severity);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON system_events(timestamp DESC);

                                        -- =============================================
                                        -- FUNCIONES Y TRIGGERS
                                        -- =============================================

-- Función para actualizar el timestamp updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at automáticamente
CREATE TRIGGER update_leads_updated_at 
    BEFORE UPDATE ON leads 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

                                        -- =============================================
                                        -- POLÍTICAS DE SEGURIDAD (RLS)
                                        -- =============================================

-- Habilitar RLS en las tablas principales
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_metrics ENABLE ROW LEVEL SECURITY;

-- Política básica: permitir todas las operaciones (ajustar según necesidades)
CREATE POLICY "Enable all operations for authenticated users" ON leads
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON conversations
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON messages
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all operations for authenticated users" ON interaction_metrics
    FOR ALL USING (auth.role() = 'authenticated');

                                -- =============================================
                                -- VISTAS ÚTILES
                                -- =============================================

-- Vista de leads con información de conversaciones
CREATE OR REPLACE VIEW leads_with_conversations AS
SELECT 
    l.*,
    COUNT(c.id) as total_conversations,
    MAX(c.created_at) as last_conversation_date,
    AVG(c.total_interactions) as avg_interactions
FROM leads l
LEFT JOIN conversations c ON l.id = c.lead_id
GROUP BY l.id;

-- Vista de métricas diarias
CREATE OR REPLACE VIEW daily_metrics AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_leads,
    AVG(lead_score) as avg_lead_score,
    COUNT(*) FILTER (WHERE lead_score >= 80) as high_quality_leads,
    COUNT(*) FILTER (WHERE lead_score >= 60 AND lead_score < 80) as medium_quality_leads,
    COUNT(*) FILTER (WHERE lead_score < 60) as low_quality_leads
FROM leads
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Mensaje de finalización
SELECT 'Esquema de base de datos creado exitosamente' as status;