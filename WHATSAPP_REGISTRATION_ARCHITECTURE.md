# WhatsApp Registration - Technical Architecture

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      WhatsApp User                              │
│                   (Sends any message)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│            WhatsApp Business API                                │
│         (Receives and routes message)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│         POST /webhooks/whatsapp                                 │
│         (FastAPI Webhook Handler)                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
              ┌───────┴────────┐
              │                │
              ▼                ▼
         Text Message     Other Type
              │            (Audio/Image)
              │            │
              ▼            ▼
    Check User State    [For registered
         │               users only]
         │
    ┌────┴─────────────────┐
    │                      │
    ▼                      ▼
New User            Registered User
    │                      │
    ▼                      ▼
Check if Session   Process Transaction
    │                Download Media
    ├─ Has Session   │ Process Receipt
    │   └─► Continue  │ Transcribe Audio
    │       Registration
    │
    └─ No Session
        └─► START REGISTRATION FLOW

                        │
                        ▼
    ┌──────────────────────────────────────┐
    │    Start Registration                │
    │  (save session, step=await_name)     │
    │    Send: "What's your business name?"│
    └──────────────┬───────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
    User Replies...   Timeout (24hr)
         │                   │
         ▼                   ▼
    Handle Step       Delete Session
         │
    ┌────┴──────────────────────┐
    │                           │
    ▼                           ▼
Step 1: Business Name    NEXT STEP...
  └─► Validate
  └─► Save to session
  └─► Set step = await_dialect
  └─► Send dialect options

    ▼
┌──────────────────────────────────────┐
│    Step 2: Language Preference       │
│    (1=English, 2=Pidgin, etc.)       │
│    └─► Validate (must be 1-5)        │
│    └─► Save dialect to session       │
│    └─► Set step = await_business_type│
│    └─► Send business type options    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│    Step 3: Business Type             │
│    (1=Retail, 2=Food, etc.)          │
│    └─► Validate (must be 1-5)        │
│    └─► Save type to session          │
│    └─► Proceed to completion         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│    ACCOUNT CREATION                      │
│    ├─ Get all data from session          │
│    ├─ Create User in database            │
│    ├─ Generate JWT tokens                │
│    ├─ Set session step = completed       │
│    └─ Send confirmation + tokens         │
└──────────────┬───────────────────────────┘
               │
               ▼
        ✅ USER REGISTERED
        (Can now use WhatsApp)
        - Send receipts
        - Record transactions
        - Generate reports
```

## 📦 Files & Components

```
NEW FILES:
├── model/database.py
│   └── + RegistrationSession model
│
├── service/whatsapp_conversation.py
│   ├── start_registration()
│   ├── handle_registration_step()
│   ├── get_or_detect_registration_step()
│   └── cancel_registration()

UPDATED FILES:
├── routers/webhooks.py
│   └── Updated _process_whatsapp_message()
│       to detect and handle registration
│
├── db/crud.py
│   └── + Registration session CRUD:
│       - get_registration_session()
│       - create_registration_session()
│       - update_registration_session()
│       - delete_registration_session()

DOCUMENTATION:
├── WHATSAPP_REGISTRATION.md
│   └── Complete flow & examples
│
└── WHATSAPP_REGISTRATION_ARCHITECTURE.md
    └── This file
```

## 🔄 State Transitions

```
                    ┌─ Registration Check ─┐
                    │                      │
              [User Message]               │
                    │                      │
        ┌───────────┴───────────┐         │
        │                       │         │
        ▼                       ▼         │
   Is Registered?         In Session?    │
        │                       │         │
   YES  │   NO             YES  │   NO   │
        │                       │         │
        ▼                       ▼         ▼
     Process             Continue      START
     Normally          Registration   REGISTRATION
     (Transactions)
        │                    │            │
        └────────┬───────────┴────────────┘
                 │
                 ▼
          Handle Message
                 │
        ┌────────┴───────────┐
        │                    │
        ▼                    ▼
   Transaction           Registration
   Operations            Operations
   ├─ Audio                ├─ Step 1: Name
   ├─ Images               ├─ Step 2: Dialect
   ├─ Storage              ├─ Step 3: Type
   └─ Reports              └─ Complete
```

## 💾 Database Flow

### Session Lifecycle

```
1. NEW USER SENDS MESSAGE
   ↓
2. CREATE registration_sessions RECORD
   {
     phone_number: "+254712345678",
     step: "awaiting_business_name",
     expires_at: NOW + 24 hours,
     created_at: NOW
   }
   ↓
3. STORE RESPONSES (Step 1 → Step 2 → Step 3)

   Step 1 Complete:
   ├─ business_name: "ABC Store"
   └─ step: "awaiting_dialect"

   Step 2 Complete:
   ├─ preferred_dialect: "english"
   └─ step: "awaiting_business_type"

   Step 3 Complete:
   ├─ business_type: "retail"
   └─ step: "completed"
   ↓
4. CREATE USER IN users TABLE
   {
     id: UUID,
     phone_number: "+254712345678",
     business_name: "ABC Store",
     preferred_dialect: "english",
     business_type: "retail",
     is_active: true,
     created_at: NOW
   }
   ↓
5. GENERATE TOKENS
   ├─ access_token: JWT (24hr)
   └─ refresh_token: JWT (7d)
   ↓
6. SEND CONFIRMATION + TOKENS
   ↓
7. USER CAN NOW USE WHATSAPP FEATURES
```

## 🧮 State Machine

```
                    ┌─────────────────────────┐
                    │                         │
                    ▼                         │
            ┌──────────────────┐             │
            │  NOT_REGISTERED  │             │
            │  NO_SESSION      │             │
            └──────────────────┘             │
                    │                         │
          (Send Message)                      │
                    │                         │
                    ▼                         │
            ┌──────────────────┐             │
            │   IN_REGISTRATION│             │
            │   STEP_1         │             │
            │  (Await Name)    │             │
            └──────────────────┘             │
                    │                         │
          (Send Business Name)                │
                    │                         │
                    ▼                         │
            ┌──────────────────┐             │
            │   IN_REGISTRATION│             │
            │   STEP_2         │             │
            │ (Await Dialect)  │             │
            └──────────────────┘             │
                    │                         │
        (Send Dialect Number 1-5)            │
                    │                         │
                    ▼                         │
            ┌──────────────────┐             │
            │   IN_REGISTRATION│             │
            │   STEP_3         │             │
            │ (Await Type)     │             │
            └──────────────────┘             │
                    │                         │
        (Send Business Type Number 1-5)      │
                    │                         │
                    ▼                         │
            ┌──────────────────┐             │
            │   REGISTERED     │─────────────┘
            │   CAN_USE_APP    │
            └──────────────────┘
                    │
           (Can access all features)
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   Send Voice  Send Receipt Generate
   Messages    Images      Reports
```

## 🔐 Security Considerations

### Input Validation

```
Business Name:
├─ Length: 2-255 chars
├─ Type: String
└─ Nullable: No

Dialect:
├─ Values: {1,2,3,4,5}
├─ Maps to: {english, pidgin, yoruba, igbo, hausa}
└─ Nullable: No

Business Type:
├─ Values: {1,2,3,4,5}
├─ Maps to: {retail, food, transport, electronics, other}
└─ Nullable: No
```

### Session Management

```
Session Lifetime:
├─ Start: Created on first message
├─ Duration: 24 hours
├─ Expiry: Auto-delete if expired
└─ Cleanup: Background job can run

Session Isolation:
├─ One session per phone_number (UNIQUE)
├─ Only active registrations tracked (step != completed)
├─ Multiple attempts allowed (create new after timeout)
```

### Token Security

```
Access Token:
├─ Payload: {sub: user_id, type: "access"}
├─ Duration: 24 hours (configurable)
├─ Algorithm: HS256
└─ Secret: JWT_SECRET (must be strong in production)

Refresh Token:
├─ Payload: {sub: user_id, type: "refresh"}
├─ Duration: 7 days
├─ Algorithm: HS256
└─ Secret: JWT_SECRET (same as access)
```

## 📊 Scalability

### Database Indexes

```
registration_sessions:
├─ PRIMARY KEY: id (UUID)
├─ UNIQUE: phone_number
├─ INDEX: step, updated_at (for cleanup queries)
└─ INDEX: phone_number (for fast lookup)

Expected Query Times:
├─ Find session by phone: ~1ms (UNIQUE index)
├─ Find all pending registrations: ~5ms (step index)
└─ Cleanup expired: ~10ms (expires_at index)
```

### Celery Tasks

```
No direct Celery tasks needed for registration
└─ All operations are synchronous
└─ S3 upload only happens AFTER user is registered

Future Async Tasks:
├─ send_welcome_email()
├─ validate_phone_number()
└─ cleanup_expired_sessions()
```

## 🧪 Testing Scenarios

### Happy Path

```
1. New number → Start registration → Complete all steps → Account created ✅
2. Send text → Bot responds ✅
3. Send audio → Bot processes ✅
4. Send image → Bot processes ✅
```

### Edge Cases

```
1. Invalid input → Re-prompt ✅
2. Timeout → Auto-expire session ✅
3. Duplicate phone → Conflict prevention ✅
4. Session resume → Continue from last step ✅
5. Already registered → Skip to normal flow ✅
```

### Error Handling

```
1. Database error → Log & retry ✅
2. WhatsApp API error → Log & fail gracefully ✅
3. Invalid phone → Validation error ✅
4. Network timeout → Celery retry ✅
5. S3 upload failed → Async retry ✅
```

## 📈 Metrics to Track

```
Registration Funnel:
├─ Total new users: Count of distinct phone_numbers
├─ Step 1 completion: % who submit business name
├─ Step 2 completion: % who select dialect
├─ Step 3 completion: % who complete registration
├─ Dropout rate: % who don't complete
└─ Avg time to register: Median registration duration

Usage Metrics:
├─ Registered users: Count in users table
├─ Active sessions: Count WHERE step != 'completed'
├─ Expired sessions: Count WHERE expires_at < NOW
└─ Most common dialect: Mode of preferred_dialect
```

## 🚀 Deployment Checklist

-   [ ] Database migration (add RegistrationSession table)
-   [ ] Environment variables set (.env)
-   [ ] WhatsApp webhook configured
-   [ ] Redis running
-   [ ] Celery workers running
-   [ ] S3 credentials valid
-   [ ] JWT_SECRET strong and secret
-   [ ] CORS configured
-   [ ] Rate limiting (optional)
-   [ ] Monitoring enabled
-   [ ] Backups configured
-   [ ] Test with real WhatsApp number

## 🔗 Related Files

-   [WHATSAPP_REGISTRATION.md](./WHATSAPP_REGISTRATION.md) - User-facing flow
-   [BACKEND_SETUP.md](./BACKEND_SETUP.md) - General setup
-   [BACKEND_ENGINEER_GUIDE.md](./BACKEND_ENGINEER_GUIDE.md) - Original architecture
-   `/routers/webhooks.py` - Webhook handler
-   `/service/whatsapp_conversation.py` - Conversation logic
-   `/model/database.py` - RegistrationSession model
