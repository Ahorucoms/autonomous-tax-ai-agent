-- Malta Tax AI Learning - Supabase Database Schema
-- Comprehensive schema for document management, knowledge base, and learning system

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'tax_professional')),
    jurisdiction TEXT DEFAULT 'malta',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table for storing parsed documents
CREATE TABLE public.documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size BIGINT,
    document_type TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    parsed_content JSONB,
    extracted_data JSONB,
    processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    vector_id TEXT, -- Reference to Pinecone vector ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge base table for tax regulations and rules
CREATE TABLE public.knowledge_base (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'regulation' CHECK (content_type IN ('regulation', 'form', 'guidance', 'case_law', 'faq')),
    jurisdiction TEXT DEFAULT 'malta',
    category TEXT,
    tags TEXT[],
    source_url TEXT,
    effective_date DATE,
    expiry_date DATE,
    version TEXT DEFAULT '1.0',
    metadata JSONB DEFAULT '{}',
    vector_id TEXT, -- Reference to Pinecone vector ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learning sessions table for tracking user interactions
CREATE TABLE public.learning_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    session_type TEXT DEFAULT 'chat' CHECK (session_type IN ('chat', 'calculation', 'form_filling', 'research')),
    context JSONB DEFAULT '{}',
    messages JSONB DEFAULT '[]',
    outcomes JSONB DEFAULT '{}',
    feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
    feedback_text TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent interactions table for tracking AI agent performance
CREATE TABLE public.agent_interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.learning_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    interaction_type TEXT NOT NULL,
    user_input TEXT,
    agent_response TEXT,
    context_used JSONB DEFAULT '{}',
    confidence_score REAL,
    response_time_ms INTEGER,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Source connectors table for external data sources
CREATE TABLE public.source_connectors (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    connector_type TEXT NOT NULL CHECK (connector_type IN ('web_scraper', 'api', 'file_watcher', 'rss_feed')),
    configuration JSONB NOT NULL,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error')),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_frequency TEXT DEFAULT 'daily',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sync jobs table for tracking data synchronization
CREATE TABLE public.sync_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    connector_id UUID REFERENCES public.source_connectors(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    records_processed INTEGER DEFAULT 0,
    records_added INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Personas table for different AI agent personalities/specializations
CREATE TABLE public.personas (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    jurisdiction TEXT DEFAULT 'malta',
    specialization TEXT[], -- e.g., ['income_tax', 'vat', 'corporate_tax']
    personality_traits JSONB DEFAULT '{}',
    knowledge_base_filters JSONB DEFAULT '{}',
    prompt_template TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES public.user_profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fine-tuning jobs table for model improvement
CREATE TABLE public.fine_tuning_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_name TEXT NOT NULL,
    model_base TEXT DEFAULT 'gpt-3.5-turbo',
    training_data_path TEXT,
    validation_data_path TEXT,
    hyperparameters JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    model_id TEXT, -- OpenAI fine-tuned model ID
    performance_metrics JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table for collecting user feedback
CREATE TABLE public.feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    interaction_id UUID REFERENCES public.agent_interactions(id) ON DELETE CASCADE,
    feedback_type TEXT DEFAULT 'rating' CHECK (feedback_type IN ('rating', 'correction', 'suggestion', 'bug_report')),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    suggested_response TEXT,
    metadata JSONB DEFAULT '{}',
    is_processed BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance optimization
CREATE INDEX idx_documents_user_id ON public.documents(user_id);
CREATE INDEX idx_documents_document_type ON public.documents(document_type);
CREATE INDEX idx_documents_created_at ON public.documents(created_at DESC);
CREATE INDEX idx_knowledge_base_jurisdiction ON public.knowledge_base(jurisdiction);
CREATE INDEX idx_knowledge_base_category ON public.knowledge_base(category);
CREATE INDEX idx_knowledge_base_tags ON public.knowledge_base USING GIN(tags);
CREATE INDEX idx_learning_sessions_user_id ON public.learning_sessions(user_id);
CREATE INDEX idx_learning_sessions_created_at ON public.learning_sessions(created_at DESC);
CREATE INDEX idx_agent_interactions_session_id ON public.agent_interactions(session_id);
CREATE INDEX idx_agent_interactions_user_id ON public.agent_interactions(user_id);
CREATE INDEX idx_feedback_user_id ON public.feedback(user_id);
CREATE INDEX idx_feedback_is_processed ON public.feedback(is_processed);

-- Row Level Security (RLS) policies
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;

-- User profiles policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Documents policies
CREATE POLICY "Users can view own documents" ON public.documents
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents" ON public.documents
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own documents" ON public.documents
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own documents" ON public.documents
    FOR DELETE USING (auth.uid() = user_id);

-- Learning sessions policies
CREATE POLICY "Users can view own learning sessions" ON public.learning_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own learning sessions" ON public.learning_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own learning sessions" ON public.learning_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Agent interactions policies
CREATE POLICY "Users can view own agent interactions" ON public.agent_interactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own agent interactions" ON public.agent_interactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Feedback policies
CREATE POLICY "Users can view own feedback" ON public.feedback
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own feedback" ON public.feedback
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON public.documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON public.knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_sessions_updated_at BEFORE UPDATE ON public.learning_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_source_connectors_updated_at BEFORE UPDATE ON public.source_connectors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personas_updated_at BEFORE UPDATE ON public.personas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default knowledge base entries for Malta tax system
INSERT INTO public.knowledge_base (title, content, content_type, jurisdiction, category, tags) VALUES
('Malta Income Tax Rates 2025', 'Malta income tax is calculated using progressive rates: 0% on first €9,100, 15% on €9,101-€14,500, 25% on €14,501-€19,500, 25% on €19,501-€60,000, 35% on income above €60,000. Married couples benefit from joint taxation.', 'regulation', 'malta', 'income_tax', ARRAY['income_tax', 'rates', '2025']),
('Malta VAT Rates', 'Malta VAT rates: Standard rate 18%, Reduced rates 12% (accommodation), 7% (books, newspapers), 5% (energy-saving materials), 0% (exports, intra-EU supplies).', 'regulation', 'malta', 'vat', ARRAY['vat', 'rates', 'standard', 'reduced']),
('FS3 Form Requirements', 'Form FS3 is the annual income tax return for individuals in Malta. Must be filed by June 30th following the tax year. Required for all residents with income above €9,100.', 'form', 'malta', 'forms', ARRAY['fs3', 'income_tax', 'filing', 'deadline']),
('Malta Social Security Contributions', 'Class 1 contributions: Employee 10%, Employer 10%. Class 2 contributions: Self-employed 15% on annual income. Maximum weekly contribution caps apply.', 'regulation', 'malta', 'social_security', ARRAY['social_security', 'class1', 'class2', 'contributions']),
('Malta Stamp Duty on Property', 'Stamp duty rates: 2% up to €150,000, 5% from €150,001-€300,000, 8% above €300,000. First-time buyers: 0% up to €150,000, 2% from €150,001-€300,000, 5% above €300,000.', 'regulation', 'malta', 'stamp_duty', ARRAY['stamp_duty', 'property', 'first_time_buyer']);

-- Insert default personas
INSERT INTO public.personas (name, description, jurisdiction, specialization, personality_traits, prompt_template) VALUES
('Malta Tax Expert', 'Comprehensive Malta tax specialist with expertise in all tax types', 'malta', ARRAY['income_tax', 'vat', 'corporate_tax', 'social_security', 'stamp_duty'], '{"tone": "professional", "expertise_level": "expert", "communication_style": "detailed"}', 'You are a Malta tax expert with comprehensive knowledge of Malta tax laws and regulations. Provide accurate, detailed, and practical tax advice.'),
('VAT Specialist', 'Specialized in Malta VAT regulations and compliance', 'malta', ARRAY['vat'], '{"tone": "friendly", "expertise_level": "specialist", "communication_style": "practical"}', 'You are a Malta VAT specialist. Focus on VAT-related questions and provide clear, actionable guidance on VAT compliance and calculations.'),
('Individual Tax Advisor', 'Personal tax advisor for individual taxpayers in Malta', 'malta', ARRAY['income_tax', 'social_security'], '{"tone": "supportive", "expertise_level": "advisor", "communication_style": "simple"}', 'You are a personal tax advisor helping individual taxpayers in Malta. Explain tax concepts in simple terms and provide step-by-step guidance.');

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Storage bucket for documents
INSERT INTO storage.buckets (id, name, public) VALUES ('documents', 'documents', false);

-- Storage policies
CREATE POLICY "Users can upload own documents" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view own documents" ON storage.objects
    FOR SELECT USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can update own documents" ON storage.objects
    FOR UPDATE USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own documents" ON storage.objects
    FOR DELETE USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

