# WhatsApp-First Registration Flow Implementation

## 📱 Overview

Users now register directly through WhatsApp! The bot guides them through a multi-step conversation to collect necessary information.

## 🔄 Registration Flow

```
User: Sends any message to bot
  ↓
Bot: Detects new user, asks for business name
  ↓
User: Replies with business name
  ↓
Bot: Asks for language preference (1-5)
  ↓
User: Selects language
  ↓
Bot: Asks for business type (1-5)
  ↓
User: Selects business type
  ↓
Bot: Creates account, sends confirmation & tokens
  ↓
User: Account ready! Can track transactions
```

## 📑 Database Changes

### New Table: `registration_sessions`

Tracks multi-step registration conversations:

```sql
CREATE TABLE registration_sessions (
  id UUID PRIMARY KEY,
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  step VARCHAR(50),  -- awaiting_business_name, awaiting_dialect, awaiting_business_type, completed
  business_name VARCHAR(255),
  preferred_dialect VARCHAR(50),
  business_type VARCHAR(100),
  conversation_state JSONB,
  started_at TIMESTAMP,
  expires_at TIMESTAMP,  -- 24 hours from start
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**Indexes:**

-   `phone_number` - Fast lookup for active sessions
-   `step, updated_at` - Track registration progress

## 🔧 Implementation Details

### 1. **Conversation Manager** (`service/whatsapp_conversation.py`)

Handles the multi-step registration flow:

-   `start_registration()` - Initiates flow, sends first prompt
-   `handle_registration_step()` - Processes user input at each step
-   `get_or_detect_registration_step()` - Determines user state
-   `cancel_registration()` - Cancels and clears session

### 2. **Multilingual Support**

Bot responds in user's preferred language:

**Supported Languages:**

-   English
-   Pidgin
-   Yoruba
-   Igbo
-   Hausa

All prompts translated for each language:

-   Business name request
-   Language selection options
-   Business type options
-   Account confirmation

### 3. **Updated Webhook** (`routers/webhooks.py`)

Now handles three user states:

**State 1: New User (No Account, No Session)**

```
Action: Start registration flow
Response: Send business name prompt
```

**State 2: User in Registration (Session Active)**

```
Action: Capture response
Response: Validate, move to next step
         Send next prompt
```

**State 3: Registered User**

```
Action: Process normally (transactions, audio, images, etc.)
```

### 4. **CRUD Operations** (`db/crud.py`)

New functions for registration management:

```python
get_registration_session(phone, db)
create_registration_session(phone, db)
update_registration_session(phone, data, db)
delete_registration_session(phone, db)
```

## 📊 Registration Steps

### Step 1: Business Name

```
Bot: "Welcome to AkoweAI! 👋 Let's set up your account. What's the name of your business?"

User Input: "John's Trading"
Validation: Must be 2+ characters
```

### Step 2: Language Preference

```
Bot: "Great! Which language do you prefer? Reply with a number:
1️⃣ English
2️⃣ Pidgin
3️⃣ Yoruba
4️⃣ Igbo
5️⃣ Hausa"

User Input: "2"
Validation: Must be 1-5
```

### Step 3: Business Type

```
Bot: "What type of business do you run? Reply with a number:
1️⃣ Retail
2️⃣ Food
3️⃣ Transport
4️⃣ Electronics
5️⃣ Other"

User Input: "1"
Validation: Must be 1-5
```

### Step 4: Account Creation & Confirmation

```
Bot: "✅ Account created successfully!
📊 Business: John's Trading
🗣️ Language: Pidgin
💼 Type: Retail

You can now track your transactions! Send receipts, record expenses, or upload voice notes.

🔐 Your account is ready! Here are your tokens:

Access Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Refresh Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Keep these safe! Use the access token for API requests."
```

## 💾 Data Storage Flow

1. **Session Created**

    - `registration_sessions` table gets new record
    - Status: `awaiting_business_name`
    - Expires in 24 hours

2. **Each Step**

    - Collects data
    - Updates `registration_sessions`
    - Advances `step` field

3. **Completion**
    - Validates all data
    - Creates user in `users` table
    - Generates JWT tokens
    - Updates session `step` to `completed`

## 🔐 Security Features

1. **Session Expiration**

    - Sessions expire after 24 hours
    - Prevents stale conversations

2. **Input Validation**

    - Business name: 2+ characters
    - Dialect/Type: Numeric 1-5 validation
    - Re-prompts on invalid input

3. **Token Generation**

    - Access tokens: 24 hours expiry
    - Refresh tokens: 7 days expiry
    - Secure JWT signing

4. **Phone Verification**
    - Phone number must be unique
    - Only one registration per phone

## 🔧 Configuration

Add to `.env`:

```env
# WhatsApp (already configured)
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_ID=your_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id
WHATSAPP_VERIFY_TOKEN=akowe_webhook_secret
```

## 📱 User Experience Examples

### Example 1: English User

```
User: Hello
Bot: Welcome to AkoweAI! 👋 Let's set up your account. What's the name of your business?
User: ABC Store
Bot: Great! Which language do you prefer? Reply with a number:
      1️⃣ English 2️⃣ Pidgin 3️⃣ Yoruba 4️⃣ Igbo 5️⃣ Hausa
User: 1
Bot: What type of business do you run? Reply with a number:
     1️⃣ Retail 2️⃣ Food 3️⃣ Transport 4️⃣ Electronics 5️⃣ Other
User: 1
Bot: ✅ Account created successfully!
     📊 Business: ABC Store
     🗣️ Language: English
     💼 Type: Retail
     [tokens...]
```

### Example 2: Pidgin User

```
User: Hi
Bot: Welcome to AkoweAI! 👋 Make we set up your account. Wetin be your business name?
User: Mama Amina Shop
Bot: Nice! Wetin language you prefer? Reply amidst number:
     1️⃣ English 2️⃣ Pidgin 3️⃣ Yoruba 4️⃣ Igbo 5️⃣ Hausa
User: 2
Bot: Wetin kinda business you dey manage? Reply amidst number:
     1️⃣ Retail 2️⃣ Food 3️⃣ Transport 4️⃣ Electronics 5️⃣ Other
User: 2
Bot: ✅ Account don create sharp sharp!
     📊 Business: Mama Amina Shop
     🗣️ Language: Pidgin
     💼 Type: Food
     [tokens...]
```

## 🔊 Bot Interactions AFTER Registration

Once registered, users can send:

### 1️⃣ **Text Messages**

```
User: "I spent 5000 naira on rice today from Shoprite"
Bot: [Processes via Claude to extract transaction]
Response: "✅ Recorded: 5000 NGN expense"
```

### 2️⃣ **Voice Messages**

```
User: [Sends voice note: "Today I sold goods worth fifty thousand naira"]
Bot: [Transcribes via Whisper, extracts via Claude]
Response: "✅ Recorded: 50,000 NGN income"
```

### 3️⃣ **Receipt Images**

```
User: [Sends receipt photo]
Bot: [Extracts via Claude Vision]
Response: "✅ Recorded: 12,500 NGN expense for supplies"
```

## 🧪 Testing the Flow

### Using Browser/cURL

1. **Start development server:**

    ```bash
    uvicorn main:app --reload
    ```

2. **Verify WhatsApp webhook:**

    ```bash
    curl "http://localhost:8000/webhooks/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=akowe_webhook_secret"
    ```

3. **Send test message:**
    ```bash
    curl -X POST http://localhost:8000/webhooks/whatsapp \
      -H "Content-Type: application/json" \
      -d '{
        "object": "whatsapp_business_account",
        "entry": [{
          "id": "123",
          "changes": [{
            "value": {
              "messaging_product": "whatsapp",
              "messages": [{
                "from": "254712345678",
                "id": "wamid.123",
                "type": "text",
                "text": {"body": "Hello"}
              }]
            }
          }]
        }]
      }'
    ```

### Using WhatsApp

1. Get WhatsApp Business Account credentials
2. Configure webhook URL in Meta Developer Console
3. Send message from WhatsApp to your business phone
4. Follow bot prompts

## 📊 Database Queries

### Find active registrations

```sql
SELECT phone_number, step, business_name, created_at
FROM registration_sessions
WHERE step != 'completed'
ORDER BY updated_at DESC;
```

### Find completed registrations (converted to users)

```sql
SELECT rs.phone_number, u.business_name, u.business_type, rs.created_at
FROM registration_sessions rs
JOIN users u ON rs.phone_number = u.phone_number
WHERE rs.step = 'completed'
ORDER BY rs.created_at DESC;
```

### Cleanup expired sessions

```sql
DELETE FROM registration_sessions
WHERE expires_at < NOW() AND step != 'completed';
```

## 🚀 Next Steps

Once registered, users can:

1. **Send Receipts** - Auto-extract expenses
2. **Record Voice** - Transcribe transactions
3. **Generate Reports** - Get credit-ready reports
4. **Share with Banks** - Get loans!

## 📝 Summary

✅ **WhatsApp-First Registration**

-   New users automatically guided through setup
-   Multilingual support (5 languages)
-   3-step process
-   Instant account creation
-   Tokens generated automatically
-   Session tracking with 24-hour expiry

✅ **Seamless Integration**

-   No API endpoints needed for registration
-   All via WhatsApp chat
-   User never leaves WhatsApp

✅ **Production Ready**

-   Input validation
-   Error handling
-   Session management
-   Multilingual prompts
-   Automatic token generation
