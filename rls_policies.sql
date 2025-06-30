-- Row Level Security (RLS) Policies for AI Tax Agent
-- Comprehensive security policies to protect user data and ensure proper access control

-- =============================================
-- ENABLE RLS ON ALL TABLES
-- =============================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jurisdictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tax_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- =============================================
-- USERS TABLE POLICIES
-- =============================================

-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- Admins can view all users
CREATE POLICY "Admins can view all users" ON public.users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Admins can update user roles and status
CREATE POLICY "Admins can update users" ON public.users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- USER PROFILES TABLE POLICIES
-- =============================================

-- Users can view their own profile
CREATE POLICY "Users can view own user_profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own profile
CREATE POLICY "Users can insert own user_profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own profile
CREATE POLICY "Users can update own user_profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own profile
CREATE POLICY "Users can delete own user_profile" ON public.user_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- Admins can view all profiles
CREATE POLICY "Admins can view all user_profiles" ON public.user_profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- CONVERSATIONS TABLE POLICIES
-- =============================================

-- Users can view their own conversations
CREATE POLICY "Users can view own conversations" ON public.conversations
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own conversations
CREATE POLICY "Users can insert own conversations" ON public.conversations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own conversations
CREATE POLICY "Users can update own conversations" ON public.conversations
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own conversations
CREATE POLICY "Users can delete own conversations" ON public.conversations
    FOR DELETE USING (auth.uid() = user_id);

-- Admins and tax experts can view all conversations
CREATE POLICY "Admins can view all conversations" ON public.conversations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role IN ('admin', 'tax_expert')
        )
    );

-- =============================================
-- MESSAGES TABLE POLICIES
-- =============================================

-- Users can view messages from their own conversations
CREATE POLICY "Users can view own messages" ON public.messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.conversations 
            WHERE id = conversation_id AND user_id = auth.uid()
        )
    );

-- Users can insert messages to their own conversations
CREATE POLICY "Users can insert own messages" ON public.messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.conversations 
            WHERE id = conversation_id AND user_id = auth.uid()
        )
    );

-- System can insert assistant messages (service role)
CREATE POLICY "System can insert assistant messages" ON public.messages
    FOR INSERT WITH CHECK (
        auth.jwt() ->> 'role' = 'service_role' OR
        type = 'user'
    );

-- Admins and tax experts can view all messages
CREATE POLICY "Admins can view all messages" ON public.messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role IN ('admin', 'tax_expert')
        )
    );

-- =============================================
-- DOCUMENTS TABLE POLICIES
-- =============================================

-- Users can view their own documents
CREATE POLICY "Users can view own documents" ON public.documents
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own documents
CREATE POLICY "Users can insert own documents" ON public.documents
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own documents
CREATE POLICY "Users can update own documents" ON public.documents
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own documents
CREATE POLICY "Users can delete own documents" ON public.documents
    FOR DELETE USING (auth.uid() = user_id);

-- System can update document processing status
CREATE POLICY "System can update document processing" ON public.documents
    FOR UPDATE USING (
        auth.jwt() ->> 'role' = 'service_role'
    );

-- Admins can view all documents
CREATE POLICY "Admins can view all documents" ON public.documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- KNOWLEDGE BASE TABLE POLICIES
-- =============================================

-- All authenticated users can read knowledge base
CREATE POLICY "Authenticated users can read knowledge_base" ON public.knowledge_base
    FOR SELECT USING (auth.role() = 'authenticated' AND is_active = true);

-- Only admins can modify knowledge base
CREATE POLICY "Admins can modify knowledge_base" ON public.knowledge_base
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- System can insert/update knowledge base entries
CREATE POLICY "System can modify knowledge_base" ON public.knowledge_base
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- =============================================
-- JURISDICTIONS TABLE POLICIES
-- =============================================

-- All authenticated users can read jurisdictions
CREATE POLICY "Authenticated users can read jurisdictions" ON public.jurisdictions
    FOR SELECT USING (auth.role() = 'authenticated' AND is_active = true);

-- Only admins can modify jurisdictions
CREATE POLICY "Admins can modify jurisdictions" ON public.jurisdictions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- TAX FORMS TABLE POLICIES
-- =============================================

-- All authenticated users can read tax forms
CREATE POLICY "Authenticated users can read tax_forms" ON public.tax_forms
    FOR SELECT USING (auth.role() = 'authenticated' AND is_active = true);

-- Only admins can modify tax forms
CREATE POLICY "Admins can modify tax_forms" ON public.tax_forms
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- FEEDBACK TABLE POLICIES
-- =============================================

-- Users can view their own feedback
CREATE POLICY "Users can view own feedback" ON public.feedback
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own feedback
CREATE POLICY "Users can insert own feedback" ON public.feedback
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own feedback
CREATE POLICY "Users can update own feedback" ON public.feedback
    FOR UPDATE USING (auth.uid() = user_id);

-- Admins can view all feedback
CREATE POLICY "Admins can view all feedback" ON public.feedback
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- ANALYTICS TABLE POLICIES
-- =============================================

-- Users can view their own analytics
CREATE POLICY "Users can view own analytics" ON public.analytics
    FOR SELECT USING (auth.uid() = user_id);

-- System can insert analytics
CREATE POLICY "System can insert analytics" ON public.analytics
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Admins can view all analytics
CREATE POLICY "Admins can view all analytics" ON public.analytics
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- AUDIT LOGS TABLE POLICIES
-- =============================================

-- Users can view their own audit logs
CREATE POLICY "Users can view own audit_logs" ON public.audit_logs
    FOR SELECT USING (auth.uid() = user_id);

-- System can insert audit logs
CREATE POLICY "System can insert audit_logs" ON public.audit_logs
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Admins can view all audit logs
CREATE POLICY "Admins can view all audit_logs" ON public.audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- =============================================
-- STORAGE POLICIES
-- =============================================

-- Documents bucket policies
INSERT INTO storage.buckets (id, name, public) VALUES ('documents', 'documents', false);
INSERT INTO storage.buckets (id, name, public) VALUES ('knowledge-base', 'knowledge-base', false);
INSERT INTO storage.buckets (id, name, public) VALUES ('generated-forms', 'generated-forms', false);

-- Users can upload to their own folder in documents bucket
CREATE POLICY "Users can upload own documents" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'documents' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can view their own documents
CREATE POLICY "Users can view own documents" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'documents' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can update their own documents
CREATE POLICY "Users can update own documents" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'documents' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can delete their own documents
CREATE POLICY "Users can delete own documents" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'documents' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- All authenticated users can read knowledge base
CREATE POLICY "Authenticated users can read knowledge base" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'knowledge-base' AND
        auth.role() = 'authenticated'
    );

-- Only admins can modify knowledge base
CREATE POLICY "Admins can modify knowledge base" ON storage.objects
    FOR ALL USING (
        bucket_id = 'knowledge-base' AND
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Users can access their generated forms
CREATE POLICY "Users can access own generated forms" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'generated-forms' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- System can create generated forms
CREATE POLICY "System can create generated forms" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'generated-forms' AND
        auth.jwt() ->> 'role' = 'service_role'
    );

-- =============================================
-- HELPER FUNCTIONS FOR RLS
-- =============================================

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.users 
        WHERE id = auth.uid() AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user owns conversation
CREATE OR REPLACE FUNCTION owns_conversation(conversation_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.conversations 
        WHERE id = conversation_id AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user can access document
CREATE OR REPLACE FUNCTION can_access_document(document_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.documents 
        WHERE id = document_id AND user_id = auth.uid()
    ) OR is_admin();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

