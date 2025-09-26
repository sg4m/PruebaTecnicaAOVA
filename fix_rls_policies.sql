-- Script (opcional) para corregir políticas de Row Level Security
-- Ejecutar en Supabase SQL Editor

                                    -- =============================================
                                    -- DESHABILITAR RLS TEMPORALMENTE PARA TESTING
                                    -- =============================================
-- EXCLUSIVO PARA TESTS, NO USAR EN PRODUCCION

ALTER TABLE leads DISABLE ROW LEVEL SECURITY;
ALTER TABLE conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_metrics DISABLE ROW LEVEL SECURITY;
ALTER TABLE system_events DISABLE ROW LEVEL SECURITY;

                                    -- =============================================
                                    -- POLÍTICAS MÁS PERMISIVAS PARA DESARROLLO
                                    -- =============================================

-- Eliminar políticas existentes
DROP POLICY IF EXISTS "Enable all operations for authenticated users" ON leads;
DROP POLICY IF EXISTS "Enable all operations for authenticated users" ON conversations;
DROP POLICY IF EXISTS "Enable all operations for authenticated users" ON messages;
DROP POLICY IF EXISTS "Enable all operations for authenticated users" ON interaction_metrics;

-- Crear políticas que permitan operaciones anónimas
CREATE POLICY "Allow all operations" ON leads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations" ON conversations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations" ON messages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations" ON interaction_metrics FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations" ON system_events FOR ALL USING (true) WITH CHECK (true);

-- Habilitar RLS de nuevo
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_events ENABLE ROW LEVEL SECURITY;

-- Verificar que las políticas están activas
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;