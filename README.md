# 🇲🇹 Autonomous AI Tax Agent for Malta

This is a full-stack production-grade AI agent designed to automate tax advisory and compliance services for entities operating under the Maltese jurisdiction.

## 📦 Features

✳️ **Smart Onboarding Wizard**

📄 **Document Parser & OCR**

🧠 **GPT-4o-based Agent Interaction**

📊 **Tax Calculator for Malta**

🔐 **Supabase Auth & Role-Based Access**

🧾 **Vector Search with Pinecone**

📈 **Analytics & Compliance Dashboard**

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite |
| Backend | FastAPI / Python |
| AI Engine | OpenAI GPT-4o |
| DB & Auth | Supabase (PostgreSQL) |
| Search | Pinecone Vector DB |

## 🔧 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Ahorucoms/autonomous-tax-ai-agent.git
cd autonomous-tax-ai-agent

# 2. Install Node dependencies
npm install

# 3. Install Python dependencies (if backend included)
pip install -r requirements.txt

# 4. Add your .env file (see below)
```

## 🔐 .env File Sample

Create a `.env` file with:

```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=your-openai-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENV=your-pinecone-env
```

## 🧪 Testing

```bash
# Run unit tests
pytest

# Run Vite frontend
npm run dev
```

## 🤖 Agent Interaction Flow

1. Splash screen → Role Selector
2. User selects interaction: onboarding / query / file upload
3. Agent begins chat based on:
   - Persona
   - Task Type
   - Jurisdiction
4. Agent fetches documents / policies via vector search
5. Executes tax calculations or returns compliance result
6. Logs task to Firestore and Supabase

## 📄 License

MIT © Ahorucoms 