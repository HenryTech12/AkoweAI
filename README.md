# AkoweAI - Complete Technical Documentation

**Project:** AkoweAI - Multilingual AI Financial Bridge for Africa's Invisible MSMEs  
**Created:** April 2026  
**Status:** MVP Development Phase

---

## 📚 Documentation Overview

This repository contains comprehensive technical documentation for the AkoweAI project. Select your role to get started:

### 👥 For Your Role

**Backend Engineers** → Read [BACKEND_ENGINEER_GUIDE.md](./BACKEND_ENGINEER_GUIDE.md)

-   API specifications and endpoints
-   Database design and migrations
-   Message queue system (Celery)
-   Error handling and monitoring
-   Deployment strategies

**AI/ML Engineers** → Read [AI_ENGINEER_GUIDE.md](./AI_ENGINEER_GUIDE.md)

-   Claude 3.5 Sonnet integration
-   Prompt engineering strategies
-   Voice processing (Whisper)
-   Vision-based OCR implementation
-   RAG system design
-   Testing and evaluation

**Frontend Developers** → Read [FRONTEND_DEVELOPER_GUIDE.md](./FRONTEND_DEVELOPER_GUIDE.md)

-   Landing page design and components
-   WhatsApp integration
-   Mobile responsiveness
-   Performance optimization
-   SEO and analytics setup
-   Deployment instructions

**Everyone** → Read [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md)

-   Complete system architecture
-   Technology stack overview
-   Integration patterns
-   Security & compliance
-   Deployment & DevOps

---

## 🚀 Quick Start

### What is AkoweAI?

AkoweAI is an AI-powered financial management system for Nigeria's informal traders (MSMEs). It allows traders to:

1. **Speak their dialect** - Send voice notes in Pidgin, Yoruba, Igbo, or Hausa
2. **Record with photos** - Snap receipts and invoices; AI digitizes them
3. **Get reports** - Generate bank-ready financial statements
4. **Grow their business** - Get real-time insights and credit scores

### The Problem

-   **40M+ MSMEs** in Nigeria power the economy
-   **80% remain "financially invisible"** - no formal records
-   **Banks can't assess credit** without documented history
-   **Traders need formal data** to access capital

### The Solution

AkoweAI transforms WhatsApp into an AI-driven accounting suite using:

-   **Claude 3.5 Sonnet** for multimodal reasoning
-   **OpenAI Whisper** for transcription
-   **ReportLab** for PDF generation
-   **PostgreSQL + Redis** for data management

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│              User Interface (WhatsApp)               │
└──────────────────┬──────────────────────────────────┘
                   │
          ┌────────▼────────┐
          │  Landing Page   │
          │  (React/Next)   │
          └─────────────────┘
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
┌─────────────┐          ┌──────────────────┐
│   Voice     │          │   WhatsApp API   │
│  (Whisper)  │          │  (Twilio/Meta)   │
└─────────────┘          └──────────────────┘
    │                             │
    └──────────────┬──────────────┘
                   ▼
        ┌──────────────────────┐
        │   Backend API        │
        │  (FastAPI/Express)   │
        └──────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌─────────┐  ┌──────────┐   ┌──────────┐
│ Claude  │  │Celery Q  │   │PostgreSQL│
│ 3.5     │  │(Async)   │   │  Redis   │
└─────────┘  └──────────┘   └──────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌─────────────┐ ┌──────────┐ ┌─────────────┐
│ Transcribe  │ │   OCR    │ │  Analysis   │
│ (Whisper)   │ │(Claude)  │ │(Claude RAG) │
└─────────────┘ └──────────┘ └─────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Report Generator    │
        │   (ReportLab)        │
        └──────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
┌──────────────┐          ┌────────────────┐
│  PDF Report  │          │  WhatsApp Send │
│   (S3)       │          │  Back to User  │
└──────────────┘          └────────────────┘
```

---

## 📋 Tech Stack

### Frontend

-   **Framework**: React.js / Next.js
-   **Styling**: Tailwind CSS
-   **Animation**: Framer Motion
-   **Deployment**: Vercel / Netlify

### Backend

-   **API**: FastAPI / Express.js
-   **Database**: PostgreSQL + Redis
-   **Task Queue**: Celery + RabbitMQ
-   **PDF**: ReportLab / WeasyPrint

### AI/ML

-   **Reasoning**: Claude 3.5 Sonnet
-   **Speech-to-Text**: OpenAI Whisper
-   **Vector DB**: Pinecone (for RAG)
-   **Embeddings**: OpenAI Embeddings

### DevOps & Infrastructure

-   **Containerization**: Docker
-   **Orchestration**: Kubernetes
-   **CI/CD**: GitHub Actions
-   **Cloud**: AWS / GCP
-   **CDN**: Cloudflare

---

## 🔄 Data Flow Example

### Scenario: Trader sends voice note

```
1. Trader sends audio message on WhatsApp
   └─> Audio file: "I don buy diesel for 50k"

2. WhatsApp Business API → Backend webhook
   └─> Creates async job

3. Celery worker processes:
   a) Download audio from WhatsApp
   b) Transcribe with OpenAI Whisper
   c) Parse with Claude 3.5
   d) Extract: amount=50000, type=expense, category=fuel

4. Validate transaction
   └─> Check: realistic amount? valid category? complete data?

5. Store in PostgreSQL
   └─> Transaction record created

6. Generate response
   └─> "✓ Transaction recorded: 50,000 NGN - Fuel purchase"

7. Send back via WhatsApp
   └─> User sees confirmation in chat

8. Data available for reports
   └─> Included in next financial report generation
```

---

## 📦 API Overview

### Core Endpoints

**Messages (WhatsApp)**

```
POST /api/v1/webhooks/whatsapp
GET  /api/v1/webhooks/whatsapp (verification)
```

**Transactions**

```
POST   /api/v1/transactions                    # Create
GET    /api/v1/transactions                    # List
GET    /api/v1/transactions/:id                # Get one
PUT    /api/v1/transactions/:id                # Update
DELETE /api/v1/transactions/:id                # Delete
```

**Reports**

```
POST /api/v1/reports/generate                  # Create report
GET  /api/v1/reports/:id                       # Retrieve
POST /api/v1/reports/:id/share                 # Share with bank
```

**Users**

```
POST /api/v1/auth/register                     # Register
GET  /api/v1/users/me                          # Profile
PUT  /api/v1/users/:id/preferences             # Settings
```

See [BACKEND_ENGINEER_GUIDE.md](./BACKEND_ENGINEER_GUIDE.md) for detailed specifications.

---

## 🗄️ Database Schema

### Key Tables

**users**

-   Stores trader accounts
-   Fields: phone, business_name, dialect, business_type

**transactions**

-   Individual trades/sales/expenses
-   Fields: amount, category, type, source, confidence, metadata

**receipt_images**

-   Uploaded receipt photos
-   Fields: s3_key, extracted_data, status

**voice_messages**

-   Voice note recordings
-   Fields: s3_audio_key, transcription, dialect_detected

**reports**

-   Generated financial reports
-   Fields: report_type, period, pdf_s3_key, summary_data

**report_shares**

-   Bank access to reports
-   Fields: report_id, bank_code, share_token, expires_at

See [BACKEND_ENGINEER_GUIDE.md](./BACKEND_ENGINEER_GUIDE.md#database-design) for full schema.

---

## 🤖 AI Models & Prompts

### Claude 3.5 Sonnet

Used for:

-   **Transaction extraction** from voice/text
-   **Receipt OCR** from images
-   **Dialect mapping** (Pidgin→formal English)
-   **Business insights** (with RAG)
-   **Data validation**

Key features:

-   200k token context window (perfect for 6+ months of history)
-   Multimodal (text + images)
-   Superior reasoning in Nigerian context
-   Handles code-switching naturally

### OpenAI Whisper

Used for:

-   **Transcription** of voice notes
-   **Language detection** (Pidgin, Yoruba, Igbo, Hausa)
-   **Handles accents** and informal speech

### Prompt Engineering Strategy

1. **Few-shot examples** - Show 3-5 examples of correct extraction
2. **Explicit format** - Specify exact JSON output structure
3. **Constraints** - Add rules (e.g., "amount must be > 0")
4. **Chain-of-thought** - Ask Claude to reason step-by-step
5. **Temperature control** - Low temp (0.1) for consistency, high for creativity

See [AI_ENGINEER_GUIDE.md](./AI_ENGINEER_GUIDE.md) for detailed prompt strategies.

---

## 🎨 Frontend Structure

### Pages

```
Landing Page (/)
├── Header (navigation)
├── Hero (main CTA)
├── Features (6 key features)
├── How It Works (4-step process)
├── Testimonials (trader stories)
├── FAQ (common questions)
├── CTA Section (secondary CTA)
└── Footer (links, legal)
```

### Key Components

-   **WhatsAppButton** - Smart button that opens WhatsApp with pre-filled message
-   **Hero** - Large headline + subheader + CTA
-   **Features** - 3 or 6 feature cards with icons
-   **HowItWorks** - 4-step visual process flow
-   **CTA** - Conversion-focused call-to-action section

### Mobile Strategy

-   **Mobile-first** design and development
-   **Touch targets** minimum 44x44px
-   **Viewport optimization** for WhatsApp in-app browser
-   **Fast loading** - target LCP < 2.5s
-   **Reduced JS** - aim for < 100kb gzipped

See [FRONTEND_DEVELOPER_GUIDE.md](./FRONTEND_DEVELOPER_GUIDE.md) for full frontend guide.

---

## 🔐 Security & Compliance

### Data Protection

-   **Encryption at rest** - All PII encrypted in database
-   **Encryption in transit** - HTTPS/TLS for all API calls
-   **Secure storage** - S3 bucket private, no public access
-   **Data retention** - Delete on user request (GDPR compliance)

### API Security

-   **Authentication** - JWT tokens with short expiration
-   **Authorization** - Users can only access own data
-   **Rate limiting** - Prevent abuse and DoS
-   **Input validation** - Sanitize all user inputs
-   **CORS** - Restrict cross-origin requests

### Compliance

-   **GDPR** - Data deletion on request
-   **CCPA** - Privacy policy and opt-out
-   **CBN** - Central Bank of Nigeria regulations for financial data
-   **WhatsApp ToS** - Comply with Business API terms
-   **PII Handling** - Extra care with financial and personal data

---

## 🚀 Deployment Guide

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d  # Start PostgreSQL, Redis
flask db upgrade
python app.py

# Frontend
cd frontend
npm install
npm run dev

# Access at http://localhost:3000
```

### Production Deployment

```bash
# Backend (Kubernetes)
kubectl apply -f k8s/

# Frontend (Vercel)
vercel --prod

# Database migrations
kubectl exec -it pod/akowe-backend -- flask db upgrade

# Check health
curl https://api.akowe.ai/health
curl https://akowe.ai
```

See role-specific guides for detailed deployment steps.

---

## 📊 Performance Targets

### Frontend

-   **Lighthouse Score**: > 90
-   **LCP (Largest Contentful Paint)**: < 2.5s
-   **FID (First Input Delay)**: < 100ms
-   **CLS (Cumulative Layout Shift)**: < 0.1
-   **Bundle Size**: < 100kb gzipped

### Backend

-   **API Latency**: < 200ms (p95)
-   **Database Query**: < 50ms
-   **Claude API Response**: < 5s
-   **Uptime**: > 99.5%

### AI Model

-   **Extraction Accuracy**: > 95%
-   **Confidence Score**: > 0.8 for 80% of transactions
-   **Processing Time**: < 10 seconds per request

---

## 🧪 Testing Strategy

### Unit Tests

-   Test individual functions (transaction extraction, validation)
-   Mock Claude API calls
-   Test database migrations

### Integration Tests

-   Test full workflows (voice → storage → report)
-   Test API endpoints with real database
-   Test WhatsApp webhook handling

### E2E Tests (Selenium/Cypress)

-   Test user flows from landing page to report generation
-   Test WhatsApp integration
-   Test responsiveness on real devices

## 📈 Monitoring & Observability

### Logging

-   All API requests logged
-   All Claude API calls tracked
-   Error logging with stack traces
-   Structured logging with context

### Metrics

-   API request count, latency, errors
-   Claude API costs per user
-   Database query performance
-   Active users, transactions per day

### Alerting

-   Downtime alerts (Slack)
-   Error rate > 5% alert
-   Database disk space alert
-   API latency alerts (p95 > 500ms)

---

## 🎯 Key Success Metrics

### User Adoption

-   Traders registered
-   Daily active users
-   Transactions recorded per user per day
-   Feature adoption rate (voice vs image vs text)

### Financial Metrics

-   Cost per transaction processed
-   Claude API spend per user
-   Bank report generation cost
-   Revenue per bank partnership

### Quality Metrics

-   Extraction accuracy (predicted vs. actual)
-   Report generation success rate
-   WhatsApp integration uptime
-   Customer support volume

---

## 🤝 Team Collaboration

### Communication Channels

-   **Slack** - Daily updates, quick questions
-   **GitHub Issues** - Bug reports and feature requests
-   **Weekly Sync** - Monday 10am + Friday 3pm
-   **Slack Threads** - Technical discussions

### Code Review Process

1. Create feature branch (`git checkout -b feature/xyz`)
2. Make changes with clear commit messages
3. Push and create pull request
4. Get 1 approval from same team + 1 from different team
5. Run CI/CD checks
6. Merge to develop
7. Deploy to staging for testing
8. Merge to main for production

### Documentation

-   Update README.md for all new features
-   Add code comments for complex logic
-   Document API changes with examples
-   Keep roles' guides updated

---

## 🆘 Getting Help

### Documentation First

1. Check role-specific guide first
2. Look at TECHNICAL_DOCUMENTATION.md for overview
3. Search GitHub issues for similar problems
4. Check team communication history

### Ask for Help

1. Post in Slack with error log
2. Include what you tried
3. Reference relevant documentation
4. Tag relevant team members

### Common Issues & Solutions

| Issue                        | Solution                                                   |
| ---------------------------- | ---------------------------------------------------------- |
| Claude API rate limit        | Implement exponential backoff retry logic                  |
| WhatsApp webhook not working | Verify webhook URL, check access token, review logs        |
| Database connection timeout  | Check PostgreSQL is running, verify connection string      |
| Frontend build failing       | Clear node_modules, reinstall, check Node version          |
| Image not loading in browser | Check image path, verify CDN working, check S3 permissions |

---

## 📞 Contact & Resources

### Project Lead

-   Name: [Your Project Lead]
-   Email: [email]
-   Slack: @[handle]

### Backend Team Lead

-   Name: [Backend Lead]
-   Focus: API, database, infrastructure

### AI Team Lead

-   Name: [AI Lead]
-   Focus: Claude integration, prompt optimization, OCR

### Frontend Team Lead

-   Name: [Frontend Lead]
-   Focus: Landing page, UX, mobile responsiveness

---

## 📄 Legal & License

### Privacy Policy

-   Users' financial data is private
-   Data encryption with secure keys
-   No sharing without explicit consent
-   Deletion on request

### Terms of Service

-   Free for traders
-   Banks pay for credit reports
-   Responsible usage policy
-   Dispute resolution

### License

[License name and terms]

---

## 🎓 Learning Resources

### For Backend Engineers

-   FastAPI documentation: https://fastapi.tiangolo.com/
-   PostgreSQL best practices: https://www.postgresql.org/docs/
-   Celery async tasks: https://docs.celeryproject.org/
-   Docker containers: https://docs.docker.com/

### For AI Engineers

-   Claude API docs: https://docs.anthropic.com/
-   Prompt engineering guide: https://platform.openai.com/docs/guides/prompt-engineering
-   Whisper API: https://platform.openai.com/docs/guides/speech-to-text
-   RAG systems: https://docs.langchain.com/

### For Frontend Developers

-   React best practices: https://react.dev/
-   Next.js guide: https://nextjs.org/docs
-   Tailwind CSS: https://tailwindcss.com/docs
-   Web performance: https://web.dev/performance/

---

## 🗺️ Roadmap

### Phase 1: MVP (Current)

-   ✅ WhatsApp integration
-   ✅ Voice transcription
-   ✅ Receipt OCR
-   ✅ Basic transaction recording
-   🔄 Report generation

### Phase 2: Scaling (Q2 2026)

-   Expand to more languages
-   Multi-currency support
-   Mobile app (iOS/Android)
-   Bank integrations (API)

### Phase 3: Growth (Q3-Q4 2026)

-   Microfinance partnerships
-   Automated loan recommendations
-   Analytics dashboard
-   Business expense categorization

---

## ✅ Deployment Checklist

-   [ ] All tests passing
-   [ ] Code reviewed and approved
-   [ ] Documentation updated
-   [ ] Environment variables set
-   [ ] Database migrations run
-   [ ] API health check passing
-   [ ] Frontend builds successfully
-   [ ] Screenshots/demos recorded
-   [ ] Performance metrics acceptable
-   [ ] Security audit completed
-   [ ] Team notified of deployment

---

## 📞 Support

### Bug Report

Create an issue on GitHub with:

-   Reproduction steps
-   Expected vs actual behavior
-   Error logs
-   Screenshots if applicable

### Feature Request

Create an issue with:

-   Clear problem statement
-   Proposed solution
-   Use cases
-   Acceptance criteria

---

**Last Updated:** April 15, 2026  
**Next Review:** May 1, 2026

---

## Quick Reference

| What You Need        | Where to Find It                                                                        |
| -------------------- | --------------------------------------------------------------------------------------- |
| API Specs            | [BACKEND_ENGINEER_GUIDE.md](./BACKEND_ENGINEER_GUIDE.md)                                |
| Database Schema      | [BACKEND_ENGINEER_GUIDE.md#database-design](./BACKEND_ENGINEER_GUIDE.md)                |
| Claude Integration   | [AI_ENGINEER_GUIDE.md](./AI_ENGINEER_GUIDE.md)                                          |
| Prompt Examples      | [AI_ENGINEER_GUIDE.md#prompt-engineering](./AI_ENGINEER_GUIDE.md)                       |
| Landing Page Code    | [FRONTEND_DEVELOPER_GUIDE.md](./FRONTEND_DEVELOPER_GUIDE.md)                            |
| WhatsApp Integration | [FRONTEND_DEVELOPER_GUIDE.md#whatsapp-integration](./FRONTEND_DEVELOPER_GUIDE.md)       |
| System Architecture  | [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md)                              |
| Deployment           | All role guides + [TECHNICAL_DOCUMENTATION.md#deployment](./TECHNICAL_DOCUMENTATION.md) |

---

**Let's build the financial bridge Africa needs! 🌍💪**
