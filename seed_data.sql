-- Seed Data for AI Tax Agent System
-- Initial data to populate the system for testing and production

-- =============================================
-- JURISDICTIONS DATA
-- =============================================

INSERT INTO public.jurisdictions (code, name, full_name, currency_code, tax_year_start, tax_year_end, supported_languages, tax_authority_name, tax_authority_url, e_filing_available, configuration) VALUES
(
    'MT',
    'Malta',
    'Republic of Malta',
    'EUR',
    '2025-01-01',
    '2025-12-31',
    ARRAY['en', 'mt'],
    'Inland Revenue Department',
    'https://ird.gov.mt',
    true,
    '{
        "tax_brackets": [
            {"min": 0, "max": 9100, "rate": 0.0},
            {"min": 9101, "max": 14500, "rate": 0.15},
            {"min": 14501, "max": 19500, "rate": 0.25},
            {"min": 19501, "max": 60000, "rate": 0.25},
            {"min": 60001, "max": null, "rate": 0.35}
        ],
        "standard_deduction": 1200,
        "married_deduction": 1800,
        "child_allowance": 300,
        "vat_rates": {
            "standard": 0.18,
            "reduced": 0.05,
            "super_reduced": 0.07
        },
        "corporate_tax_rate": 0.35,
        "social_security": {
            "employee_rate": 0.10,
            "employer_rate": 0.10,
            "self_employed_rate": 0.15
        }
    }'
),
(
    'FR',
    'France',
    'French Republic',
    'EUR',
    '2025-01-01',
    '2025-12-31',
    ARRAY['fr', 'en'],
    'Direction générale des Finances publiques',
    'https://www.impots.gouv.fr',
    true,
    '{
        "tax_brackets": [
            {"min": 0, "max": 10777, "rate": 0.0},
            {"min": 10778, "max": 27478, "rate": 0.11},
            {"min": 27479, "max": 78570, "rate": 0.30},
            {"min": 78571, "max": 168994, "rate": 0.41},
            {"min": 168995, "max": null, "rate": 0.45}
        ],
        "standard_deduction": 0,
        "married_deduction": 0,
        "child_allowance": 0,
        "vat_rates": {
            "standard": 0.20,
            "reduced": 0.055,
            "super_reduced": 0.021
        },
        "corporate_tax_rate": 0.25,
        "social_security": {
            "employee_rate": 0.22,
            "employer_rate": 0.42,
            "self_employed_rate": 0.45
        }
    }'
);

-- =============================================
-- KNOWLEDGE BASE DATA
-- =============================================

-- Malta Tax Knowledge Base
INSERT INTO public.knowledge_base (title, content, document_type, jurisdiction, language, source_authority, effective_date, tags, metadata) VALUES
(
    'Malta Income Tax Rates 2025',
    'Malta operates a progressive income tax system with the following rates for 2025:
    
    Tax-free threshold: €9,100
    15% on income from €9,101 to €14,500
    25% on income from €14,501 to €19,500
    25% on income from €19,501 to €60,000
    35% on income above €60,000
    
    Married couples filing jointly receive an additional deduction of €600 on top of the standard €1,200 personal allowance.
    
    Self-employed individuals can deduct business expenses including:
    - Home office expenses (proportional to business use)
    - Professional development and training
    - Business equipment and software
    - Travel expenses for business purposes
    - Professional insurance premiums',
    'regulation',
    'MT',
    'en',
    'Inland Revenue Department',
    '2025-01-01',
    ARRAY['income_tax', 'rates', 'deductions', 'self_employed'],
    '{"section": "Income Tax Act", "chapter": "Chapter 123"}'
),
(
    'Malta VAT Rates and Registration',
    'Value Added Tax (VAT) in Malta for 2025:
    
    Standard Rate: 18%
    Reduced Rate: 5% (applies to accommodation, books, newspapers, certain food items)
    Super Reduced Rate: 7% (applies to certain medical equipment, cultural events)
    Zero Rate: 0% (applies to exports, international transport)
    
    VAT Registration Requirements:
    - Mandatory registration if annual turnover exceeds €35,000
    - Voluntary registration available for lower turnovers
    - Registration must be completed within 10 days of exceeding threshold
    
    VAT Returns:
    - Monthly returns for businesses with turnover > €700,000
    - Quarterly returns for smaller businesses
    - Annual returns for very small businesses (turnover < €56,000)',
    'regulation',
    'MT',
    'en',
    'Inland Revenue Department',
    '2025-01-01',
    ARRAY['vat', 'registration', 'rates', 'returns'],
    '{"section": "VAT Act", "chapter": "Chapter 406"}'
),
(
    'Malta Corporate Tax and Business Registration',
    'Corporate Income Tax in Malta:
    
    Standard Corporate Tax Rate: 35%
    
    Tax Refund System:
    - Shareholders may claim refunds of tax paid by the company
    - Full imputation system reduces effective tax rate
    - Refunds available for: 6/7ths for trading income, 5/7ths for passive income
    
    Business Registration Requirements:
    - All companies must register with Malta Business Registry
    - Minimum share capital: €1,165 for private companies
    - At least one director must be resident in Malta or EU
    - Annual returns must be filed by March 31st
    
    Allowable Business Deductions:
    - Salaries and wages
    - Rent and utilities
    - Professional fees
    - Depreciation on business assets
    - Research and development expenses',
    'regulation',
    'MT',
    'en',
    'Inland Revenue Department',
    '2025-01-01',
    ARRAY['corporate_tax', 'business_registration', 'deductions', 'refunds'],
    '{"section": "Income Tax Act", "chapter": "Chapter 123"}'
),
(
    'Malta Social Security Contributions',
    'Social Security Contributions in Malta for 2025:
    
    Class 1 (Employed Persons):
    - Employee contribution: 10% of gross salary
    - Employer contribution: 10% of gross salary
    - Maximum weekly contribution: €48.65 (employee) + €48.65 (employer)
    
    Class 2 (Self-Employed):
    - Contribution rate: 15% of net income
    - Minimum annual contribution: €600
    - Maximum annual contribution: €3,794.40
    
    Benefits:
    - Unemployment benefit
    - Sickness benefit
    - Maternity benefit
    - Retirement pension
    - Disability pension
    
    Payment Schedule:
    - Employed persons: deducted monthly from salary
    - Self-employed: paid quarterly or annually',
    'regulation',
    'MT',
    'en',
    'Department of Social Security',
    '2025-01-01',
    ARRAY['social_security', 'contributions', 'benefits', 'self_employed'],
    '{"section": "Social Security Act", "chapter": "Chapter 318"}'
);

-- France Tax Knowledge Base
INSERT INTO public.knowledge_base (title, content, document_type, jurisdiction, language, source_authority, effective_date, tags, metadata) VALUES
(
    'Barème de l''impôt sur le revenu France 2025',
    'Le barème progressif de l''impôt sur le revenu en France pour 2025 :
    
    Tranche exonérée : jusqu''à 10 777 €
    Taux de 11% : de 10 778 € à 27 478 €
    Taux de 30% : de 27 479 € à 78 570 €
    Taux de 41% : de 78 571 € à 168 994 €
    Taux de 45% : au-delà de 168 995 €
    
    Abattements et déductions :
    - Abattement de 10% sur les salaires (minimum 448 €, maximum 13 522 €)
    - Frais réels déductibles sur justificatifs
    - Quotient familial selon le nombre de parts
    
    Dates importantes :
    - Déclaration en ligne : avant mi-mai à fin mai selon le département
    - Paiement : septembre pour l''acompte, octobre pour le solde',
    'regulation',
    'FR',
    'fr',
    'Direction générale des Finances publiques',
    '2025-01-01',
    ARRAY['impot_revenu', 'bareme', 'abattements', 'declaration'],
    '{"section": "Code général des impôts", "article": "Article 197"}'
),
(
    'TVA en France - Taux et obligations 2025',
    'Taux de TVA applicables en France en 2025 :
    
    Taux normal : 20%
    Taux réduit : 5,5% (produits alimentaires, livres, médicaments)
    Taux super réduit : 2,1% (médicaments remboursés, presse)
    Taux particulier : 10% (restauration, travaux de rénovation)
    
    Obligations des assujettis :
    - Seuil de franchise : 36 800 € (services) / 91 900 € (ventes)
    - Déclaration mensuelle si CA > 4 000 000 €
    - Déclaration trimestrielle pour les autres
    - Facturation obligatoire avec mention de la TVA
    
    Déductions possibles :
    - TVA sur achats professionnels
    - TVA sur immobilisations
    - TVA sur frais généraux',
    'regulation',
    'FR',
    'fr',
    'Direction générale des Finances publiques',
    '2025-01-01',
    ARRAY['tva', 'taux', 'obligations', 'franchise'],
    '{"section": "Code général des impôts", "article": "Article 278"}'
),
(
    'Impôt sur les sociétés France 2025',
    'Taux de l''impôt sur les sociétés en France pour 2025 :
    
    Taux normal : 25%
    Taux réduit : 15% sur les premiers 42 500 € de bénéfice (sous conditions)
    
    Conditions pour le taux réduit :
    - Chiffre d''affaires < 10 000 000 €
    - Capital entièrement libéré
    - Détention continue par des personnes physiques ≥ 75%
    
    Obligations déclaratives :
    - Liasse fiscale à déposer dans les 3 mois de la clôture
    - Acomptes trimestriels si IS > 3 000 €
    - Télédéclaration obligatoire
    
    Déductions autorisées :
    - Charges d''exploitation
    - Amortissements
    - Provisions pour risques et charges
    - Frais financiers',
    'regulation',
    'FR',
    'fr',
    'Direction générale des Finances publiques',
    '2025-01-01',
    ARRAY['impot_societes', 'taux', 'obligations', 'deductions'],
    '{"section": "Code général des impôts", "article": "Article 219"}'
);

-- =============================================
-- TAX FORMS DATA
-- =============================================

-- Malta Tax Forms
INSERT INTO public.tax_forms (jurisdiction, form_code, form_name, form_type, language, tax_year, fields_schema, validation_rules) VALUES
(
    'MT',
    'IT1',
    'Individual Income Tax Return',
    'income_tax',
    'en',
    2025,
    '{
        "personal_details": {
            "full_name": {"type": "text", "required": true},
            "id_number": {"type": "text", "required": true, "pattern": "^[0-9]{7}[A-Z]$"},
            "address": {"type": "text", "required": true},
            "marital_status": {"type": "select", "options": ["single", "married", "divorced", "widowed"]}
        },
        "income": {
            "employment_income": {"type": "number", "min": 0},
            "self_employment_income": {"type": "number", "min": 0},
            "rental_income": {"type": "number", "min": 0},
            "investment_income": {"type": "number", "min": 0},
            "other_income": {"type": "number", "min": 0}
        },
        "deductions": {
            "business_expenses": {"type": "number", "min": 0},
            "charitable_donations": {"type": "number", "min": 0},
            "medical_expenses": {"type": "number", "min": 0},
            "education_expenses": {"type": "number", "min": 0}
        }
    }',
    '{
        "total_income_required": true,
        "max_charitable_deduction": 0.1,
        "filing_deadline": "2025-06-30"
    }'
),
(
    'MT',
    'VAT1',
    'VAT Return',
    'vat',
    'en',
    2025,
    '{
        "business_details": {
            "vat_number": {"type": "text", "required": true, "pattern": "^MT[0-9]{8}$"},
            "business_name": {"type": "text", "required": true},
            "period_from": {"type": "date", "required": true},
            "period_to": {"type": "date", "required": true}
        },
        "sales": {
            "standard_rate_sales": {"type": "number", "min": 0},
            "reduced_rate_sales": {"type": "number", "min": 0},
            "zero_rate_sales": {"type": "number", "min": 0},
            "exempt_sales": {"type": "number", "min": 0}
        },
        "purchases": {
            "vat_on_purchases": {"type": "number", "min": 0},
            "vat_on_imports": {"type": "number", "min": 0},
            "vat_on_acquisitions": {"type": "number", "min": 0}
        }
    }',
    '{
        "quarterly_filing": true,
        "filing_deadline_days": 15,
        "payment_deadline_days": 15
    }'
);

-- France Tax Forms
INSERT INTO public.tax_forms (jurisdiction, form_code, form_name, form_type, language, tax_year, fields_schema, validation_rules) VALUES
(
    'FR',
    '2042',
    'Déclaration de revenus',
    'income_tax',
    'fr',
    2025,
    '{
        "identite": {
            "nom": {"type": "text", "required": true},
            "prenom": {"type": "text", "required": true},
            "numero_fiscal": {"type": "text", "required": true, "pattern": "^[0-9]{13}$"},
            "adresse": {"type": "text", "required": true},
            "situation_famille": {"type": "select", "options": ["celibataire", "marie", "divorce", "veuf"]}
        },
        "revenus": {
            "salaires": {"type": "number", "min": 0},
            "pensions": {"type": "number", "min": 0},
            "revenus_fonciers": {"type": "number", "min": 0},
            "revenus_capitaux": {"type": "number", "min": 0},
            "benefices_commerciaux": {"type": "number", "min": 0}
        },
        "charges": {
            "frais_reels": {"type": "number", "min": 0},
            "pensions_alimentaires": {"type": "number", "min": 0},
            "dons": {"type": "number", "min": 0},
            "frais_garde": {"type": "number", "min": 0}
        }
    }',
    '{
        "declaration_en_ligne_obligatoire": true,
        "date_limite": "2025-05-31",
        "abattement_salaires": 0.10
    }'
);

-- =============================================
-- SAMPLE USER DATA (for testing)
-- =============================================

-- Note: In production, users will be created through Supabase Auth
-- This is just for reference and testing purposes

-- Sample admin user profile (will be created after auth signup)
-- INSERT INTO public.user_profiles (user_id, employment_status, marital_status, annual_income, tax_residency, preferences) VALUES
-- (
--     '00000000-0000-0000-0000-000000000001', -- Replace with actual user ID after signup
--     'employed',
--     'single',
--     45000.00,
--     'MT',
--     '{"notifications": true, "language": "en", "theme": "light"}'
-- );

-- =============================================
-- ANALYTICS EVENTS SETUP
-- =============================================

-- Insert initial analytics events for tracking
INSERT INTO public.analytics (event_type, metadata) VALUES
('system_initialized', '{"version": "1.0.0", "timestamp": "2025-01-01T00:00:00Z"}'),
('knowledge_base_seeded', '{"documents_count": 7, "jurisdictions": ["MT", "FR"]}'),
('tax_forms_loaded', '{"forms_count": 3, "jurisdictions": ["MT", "FR"]}');

