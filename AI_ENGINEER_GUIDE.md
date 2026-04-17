# AkoweAI - AI Engineer Implementation Guide

**Target Audience:** AI/ML Engineers & Prompt Engineers  
**Date:** April 2026  
**Project:** AkoweAI - Multilingual AI Financial Bridge for Africa's Invisible MSMEs

---

## Table of Contents

1. [Overview](#overview)
2. [Claude 3.5 Sonnet Integration](#claude-35-sonnet-integration)
3. [Prompt Engineering](#prompt-engineering)
4. [Voice Processing (Whisper)](#voice-processing-whisper)
5. [Vision-Based OCR](#vision-based-ocr)
6. [RAG & Context Management](#rag--context-management)
7. [Performance Optimization](#performance-optimization)
8. [Testing & Evaluation](#testing--evaluation)

---

## Overview

### AI Architecture

AkoweAI uses a multi-modal AI pipeline to process financial data from Nigerian informal traders:

```
User Input (Voice/Image/Text)
        ↓
┌───────┴────────┐
│                │
▼                ▼
Audio           Image
(Whisper)     (Claude Vision)
│                │
└───────┬────────┘
        ▼
  Transcription/
  Extracted Text
        ▼
┌─────────────────────────────────┐
│   Claude 3.5 (Logic Engine)     │
│   - Parse transaction details   │
│   - Map to categories           │
│   - Extract entities            │
│   - Validate data               │
└─────────────────────────────────┘
        ▼
  Structured JSON
  (Transaction Data)
        ▼
  Database Storage
```

### Key Capabilities

| Capability                | Purpose                      | Model                           |
| ------------------------- | ---------------------------- | ------------------------------- |
| **Multimodal Processing** | Handle voice, images, text   | Claude 3.5 Sonnet               |
| **Speech-to-Text**        | Transcribe voice notes       | OpenAI Whisper                  |
| **Image Recognition**     | Extract data from receipts   | Claude 3.5 Vision               |
| **Dialect Mapping**       | Understand local languages   | Claude 3.5 + Prompt Engineering |
| **Financial Analysis**    | Generate business insights   | Claude 3.5 + RAG                |
| **PDF Report Generation** | Create bank-standard reports | ReportLab + Claude              |

---

## Claude 3.5 Sonnet Integration

### 1. Setup & Configuration

```python
# ai/claude_client.py
import anthropic
import os
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 2000

    def call_claude(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = None,
        temperature: float = 0.3,
        images: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generic Claude API call with error handling

        Args:
            system_prompt: System instruction
            user_message: User query
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0=deterministic, 1=creative)
            images: List of image data for vision tasks

        Returns:
            Claude response with metadata
        """
        try:
            content = [{"type": "text", "text": user_message}]

            # Add images if provided
            if images:
                for image in images:
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image["media_type"],
                            "data": image["data"]
                        }
                    })

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": content}
                ],
                temperature=temperature
            )

            return {
                "success": True,
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except anthropic.APIError as e:
            logger.error(f"Claude API Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

claude_client = ClaudeClient()
```

### 2. Core AI Processing Functions

```python
# ai/transaction_extractor.py
from ai.claude_client import claude_client
import json
from typing import Dict, Any

class TransactionExtractor:
    """Extract financial transactions from various sources"""

    SYSTEM_PROMPT_TRANSACTION = """You are a financial data extraction specialist for African informal traders.
Your task is to extract structured transaction information from unstructured Nigerian text/dialect.

Rules:
1. Always respond with VALID JSON only - no markdown, no extra text
2. Amount is always in NGN (Nigerian Naira) unless explicitly stated otherwise
3. Confidence: 0-1 score (1.0 = very confident, 0.5 = uncertain, <0.5 = unclear data)
4. If you cannot determine a field, use null
5. Map informal phrases to formal categories
6. For debts: identify creditor, amount owed, and purpose
7. For income: identify source and customer if mentioned
8. For expenses: identify category and supplier if mentioned

Common Category Mappings:
- Fuel/petrol/diesel → Expense: Fuel
- Buy goods/stock/inventory → Expense: Inventory
- Sold goods/sales/market → Income: Sales
- Electricity/water → Expense: Utilities
- Transport/logistics → Expense: Transportation
- Borrowed/debtor/due → Debt
"""

    def extract_from_text(
        self,
        text: str,
        dialect: str = "pidgin",
        user_context: Dict = None
    ) -> Dict[str, Any]:
        """
        Extract transaction details from text/transcription

        Args:
            text: Transcribed or typed text
            dialect: Language dialect (pidgin, yoruba, igbo, hausa, english)
            user_context: User's business context for better accuracy

        Returns:
            Structured transaction data
        """
        user_message = f"""Extract transaction details from this {dialect} text:

"{text}"

Respond with ONLY this JSON structure:
{{
  "amount": <number or null>,
  "currency": "NGN",
  "type": "<income|expense|debt|null>",
  "category": "<category name or null>",
  "description": "<what transaction is about>",
  "items": [
    {{"name": "<item>", "quantity": <number>, "unit_price": <number>}}
  ],
  "counterparty": "<person or business name or null>",
  "confidence": <0-1 float>,
  "flags": ["warning1", "warning2"],
  "extracted_raw": "{text}"
}}"""

        response = claude_client.call_claude(
            system_prompt=self.SYSTEM_PROMPT_TRANSACTION,
            user_message=user_message,
            temperature=0.1  # Low temperature for consistency
        )

        if not response["success"]:
            return {"success": False, "error": response["error"]}

        try:
            data = json.loads(response["content"])
            data["success"] = True
            data["source"] = "voice_text"
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {response['content']}")
            return {
                "success": False,
                "error": "Invalid JSON from Claude",
                "raw_response": response["content"]
            }

    def validate_transaction(self, transaction: Dict) -> Dict[str, Any]:
        """
        Validate extracted transaction using Claude

        Returns validation report with corrections
        """
        validation_prompt = f"""Review this extracted transaction for accuracy:

{json.dumps(transaction, indent=2)}

Check for:
1. Logical consistency (amount > 0, valid categories)
2. Realistic values for Nigerian MSME context
3. Complete required fields
4. Potential data entry errors

Respond with JSON:
{{
  "is_valid": <true|false>,
  "confidence": <0-1>,
  "issues": ["issue1", "issue2"],
  "suggestions": {{"field": "suggested_value"}},
  "reasoning": "<explanation>"
}}"""

        response = claude_client.call_claude(
            system_prompt=self.SYSTEM_PROMPT_TRANSACTION,
            user_message=validation_prompt,
            temperature=0.2
        )

        if response["success"]:
            return json.loads(response["content"])
        return {"success": False, "error": response["error"]}

transaction_extractor = TransactionExtractor()
```

### 3. Dialect & Intent Recognition

```python
# ai/dialect_handler.py
class DialectHandler:
    """Handle Nigerian dialects and language variations"""

    DIALECT_MAPPING = {
        "pidgin": "Nigerian Pidgin English",
        "yoruba": "Yoruba language (Nigeria)",
        "igbo": "Igbo language (Nigeria)",
        "hausa": "Hausa language (Nigeria)",
        "english": "English (Nigerian variant)"
    }

    SYSTEM_PROMPT_DIALECT = """You are an expert in Nigerian dialects and informal speech patterns.
Your task is to:
1. Detect the dialect/language
2. Extract financial meaning from informal/colloquial expressions
3. Map dialectal phrases to formal business categories

Common Expressions:
Pidgin:
- "I don use 50k" = I spent 50,000 NGN
- "I done sell for im" = I sold to him/her
- "E nor pure" = It's not genuine/quality issue

Yoruba:
- "Owo owo" = Money/payment
- "Tú ra" = Buy/purchase
- "Je" = Sell

Igbo:
- "Ego" = Money
- "Zụ" = Buy
- "Ere" = Sell
"""

    def detect_dialect(self, text: str) -> Dict[str, Any]:
        """Detect which dialect/language the text is in"""
        prompt = f"""Identify the dialect/language of this text: "{text}"

Respond with JSON:
{{
  "detected_dialect": "<pidgin|yoruba|igbo|hausa|english>",
  "confidence": <0-1>,
  "language_markers": ["marker1", "marker2"]
}}"""

        response = claude_client.call_claude(
            system_prompt=self.SYSTEM_PROMPT_DIALECT,
            user_message=prompt,
            temperature=0.1
        )

        return json.loads(response["content"])

    def extract_intent(self, text: str, dialect: str) -> Dict[str, Any]:
        """Extract user's intent from message"""
        prompt = f"""What is the user trying to do in this {dialect} message?

Message: "{text}"

Classify the intent and extract key financial information.

Respond with JSON:
{{
  "primary_intent": "<record_transaction|view_balance|request_loan|get_advice|other>",
  "transaction_type": "<income|expense|debt|null>",
  "amount": <number or null>,
  "description": "<what they're doing>",
  "confidence": <0-1>
}}"""

        response = claude_client.call_claude(
            system_prompt=self.SYSTEM_PROMPT_DIALECT,
            user_message=prompt
        )

        return json.loads(response["content"])

dialect_handler = DialectHandler()
```

---

## Prompt Engineering

### 1. Effective Prompt Strategies

```python
# prompts/templates.py

class PromptTemplates:
    """Collection of optimized prompts for different tasks"""

    # Few-shot examples for consistency
    FEW_SHOT_EXAMPLES = """
Example 1:
Input: "I don buy fuel for 50k yesterday"
Output: {"amount": 50000, "type": "expense", "category": "fuel", "description": "Fuel purchase"}

Example 2:
Input: "Customer pay me 200000 for the goods wey I sell am"
Output: {"amount": 200000, "type": "income", "category": "sales", "description": "Sales revenue"}

Example 3:
Input: "I don debt my brother 80k for business"
Output: {"amount": 80000, "type": "debt", "description": "Loan from brother", "counterparty": "brother"}
"""

    @staticmethod
    def transaction_extraction_prompt(text: str, dialect: str) -> str:
        """Prompt for extracting transactions with few-shot learning"""
        return f"""You are a financial analyst specializing in informal Nigerian businesses.

{PromptTemplates.FEW_SHOT_EXAMPLES}

Now extract transaction from this {dialect} text:
"{text}"

Return ONLY valid JSON with: amount, type, category, description, counterparty, confidence"""

    @staticmethod
    def business_insight_prompt(transactions: list) -> str:
        """Prompt for generating business insights"""
        return f"""Analyze this business's financial pattern over the given period.

Transactions:
{json.dumps(transactions, indent=2)}

Provide insights on:
1. Revenue trends
2. Spending patterns
3. Profitability
4. Cash flow health
5. Loan repayment capacity
6. Growth recommendations

Return as JSON with: insights, recommendations, credit_score (0-100)"""

    @staticmethod
    def anomaly_detection_prompt(transactions: list, new_transaction: dict) -> str:
        """Detect unusual transactions"""
        return f"""Check if this transaction is anomalous for this trader.

Historical average transactions:
{json.dumps(transactions[-10:], indent=2)}

New transaction:
{json.dumps(new_transaction, indent=2)}

Respond with JSON: {{
  "is_anomalous": true/false,
  "anomaly_score": 0-1,
  "reasoning": "explanation",
  "suggestion": "action to take"
}}"""

    @staticmethod
    def dialect_translation_prompt(text: str, source_dialect: str, target_dialect: str = "formal_english") -> str:
        """Translate dialect to formal English"""
        return f"""Translate this {source_dialect} text to formal {target_dialect}.

Text: "{text}"

Preserve all financial information and provide the formal version."""
```

### 2. Prompt Optimization Best Practices

```python
# ai/prompt_optimizer.py

class PromptOptimizer:
    """Strategies for optimizing prompt quality"""

    @staticmethod
    def apply_chain_of_thought(prompt: str) -> str:
        """Add chain-of-thought reasoning"""
        return prompt + "\n\nThink step by step before providing your answer."

    @staticmethod
    def add_context_constraints(prompt: str, constraints: list) -> str:
        """Add constraints to improve accuracy"""
        constraint_text = "\nConstraints:\n" + "\n".join([f"- {c}" for c in constraints])
        return prompt + constraint_text

    @staticmethod
    def add_output_format(prompt: str, format_spec: str) -> str:
        """Explicitly specify output format"""
        return prompt + f"\n\nOutput Format:\n{format_spec}"

    @staticmethod
    def optimize_for_speed(prompt: str) -> str:
        """Reduce prompt length while maintaining quality"""
        # Remove unnecessary context
        # Use abbreviations
        # Focus on essential information
        return prompt

    @staticmethod
    def optimize_for_accuracy(prompt: str) -> str:
        """Add examples and detailed instructions"""
        return prompt

    @staticmethod
    def test_prompt_variations(base_prompt: str, variations: dict) -> Dict[str, Any]:
        """A/B test prompt variations"""
        results = {}
        for name, prompt_modifier in variations.items():
            modified_prompt = prompt_modifier(base_prompt)
            response = claude_client.call_claude(
                system_prompt="",
                user_message=modified_prompt
            )
            results[name] = response
        return results
```

### 3. Conversation Management

```python
# ai/conversation_manager.py

class ConversationManager:
    """Manage multi-turn conversations with users"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.conversation_history = []
        self.system_prompt = "You are a helpful financial assistant for Nigerian traders."

    def add_user_message(self, message: str):
        """Add user message to conversation"""
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, message: str):
        """Add assistant response to conversation"""
        self.conversation_history.append({
            "role": "assistant",
            "content": message
        })

    def get_response(self, user_message: str) -> str:
        """Get Claude's response in conversation context"""
        self.add_user_message(user_message)

        response = claude_client.client.messages.create(
            model=claude_client.model,
            max_tokens=claude_client.max_tokens,
            system=self.system_prompt,
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text
        self.add_assistant_message(assistant_message)

        return assistant_message

    def get_conversation_summary(self) -> str:
        """Summarize conversation for context"""
        summary_prompt = f"""Summarize the key financial decisions discussed in this conversation:

{json.dumps(self.conversation_history, indent=2)}

Provide a brief summary of: transactions discussed, amounts, and decisions made."""

        response = claude_client.call_claude(
            system_prompt="You are a financial summarization expert.",
            user_message=summary_prompt
        )

        return response["content"]
```

---

## Voice Processing (Whisper)

### 1. Audio Transcription

```python
# ai/voice_processor.py
import openai
from typing import Dict, Any
import os

class VoiceProcessor:
    """Process voice notes using OpenAI Whisper"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def transcribe_audio(
        self,
        audio_file_path: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text

        Args:
            audio_file_path: Path to audio file
            language: Language code (en, yo, ig, ha, pcm for Pidgin)

        Returns:
            Transcription with metadata
        """
        # Language code mapping
        language_codes = {
            "english": "en",
            "pidgin": "pcm",  # ISO 639-3 code for Pidgin
            "yoruba": "yo",
            "igbo": "ig",
            "hausa": "ha"
        }

        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language_codes.get(language, "en"),
                    response_format="verbose_json"
                )

            return {
                "success": True,
                "text": transcript.text,
                "language": language,
                "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                "confidence": 0.9  # Whisper doesn't provide confidence
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def detect_language(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Detect language of audio file

        Returns:
            Detected language and confidence
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                # Use Whisper to detect language
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=None  # Auto-detect
                )

            # Map language code to our dialect
            language_mapping = {
                "en": "english",
                "yo": "yoruba",
                "ig": "igbo",
                "ha": "hausa",
                "pcm": "pidgin"  # May not auto-detect pidgin well
            }

            return {
                "success": True,
                "detected_language": transcript.language,
                "dialect": language_mapping.get(transcript.language, "unknown")
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_voice_message(
        self,
        audio_file_path: str,
        user_context: Dict = None
    ) -> Dict[str, Any]:
        """
        Full pipeline: transcribe → extract transaction → validate
        """
        # Detect language
        lang_detection = self.detect_language(audio_file_path)
        if not lang_detection["success"]:
            return {"success": False, "error": "Failed to detect language"}

        dialect = lang_detection.get("dialect", "english")

        # Transcribe
        transcription = self.transcribe_audio(audio_file_path, dialect)
        if not transcription["success"]:
            return {"success": False, "error": "Transcription failed"}

        # Extract transaction
        transaction = transaction_extractor.extract_from_text(
            transcription["text"],
            dialect=dialect,
            user_context=user_context
        )

        return {
            "success": True,
            "dialect": dialect,
            "transcription": transcription["text"],
            "transaction": transaction
        }

voice_processor = VoiceProcessor()
```

---

## Vision-Based OCR

### 1. Receipt Image Processing

```python
# ai/receipt_processor.py
import base64
from typing import Dict, Any

class ReceiptProcessor:
    """Process receipt images using Claude Vision"""

    SYSTEM_PROMPT_RECEIPT = """You are an expert in analyzing Nigerian business receipts and invoices.
Your task is to extract ALL financial information from receipt images.

Rules:
1. Extract each item: name, quantity, unit price, line total
2. Identify total amount prominently
3. Detect business details if visible
4. Extract payment information and balance due
5. Identify date if present
6. Flag any unclear or low-quality data
7. Return VALID JSON ONLY

Handle various receipt formats:
- Handwritten receipts
- Printed invoices
- Modern POS receipts
- Traditional market slips
- School exercise book notes
"""

    def process_receipt_image(
        self,
        image_path: str,
        image_format: str = "jpeg"
    ) -> Dict[str, Any]:
        """
        Extract data from receipt image

        Args:
            image_path: Path to receipt image
            image_format: Image format (jpeg, png)

        Returns:
            Extracted receipt data
        """
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')

        prompt = """Analyze this receipt image carefully.

Extract and return ONLY this JSON structure:
{
  "items": [
    {"description": "<item name>", "quantity": <number>, "unit_price": <number>, "line_total": <number>}
  ],
  "subtotal": <number>,
  "tax": <number or null>,
  "total_amount": <number>,
  "currency": "NGN",
  "date": "<date or null>",
  "seller_name": "<business name or null>",
  "seller_phone": "<phone or null>",
  "buyer_name": "<name or null>",
  "payment_method": "<cash|card|transfer|null>",
  "amount_paid": <number or null>,
  "change": <number or null>,
  "balance_due": <number or null>,
  "receipt_number": "<number or null>",
  "quality_score": <0-1>,
  "confidence": <0-1>,
  "notes": "<any unclear items or quality issues>"
}"""

        response = claude_client.call_claude(
            system_prompt=self.SYSTEM_PROMPT_RECEIPT,
            user_message=prompt,
            images=[{
                "media_type": f"image/{image_format}",
                "data": image_data
            }]
        )

        if not response["success"]:
            return {"success": False, "error": response["error"]}

        try:
            data = json.loads(response["content"])
            data["success"] = True
            data["processing_cost"] = response["usage"]["input_tokens"]
            return data
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "raw_response": response["content"]
            }

    def batch_process_receipts(self, image_paths: list) -> list:
        """Process multiple receipt images"""
        results = []
        for image_path in image_paths:
            result = self.process_receipt_image(image_path)
            results.append({
                "image": image_path,
                "data": result
            })
        return results

    def validate_receipt_data(self, receipt_data: Dict) -> Dict[str, Any]:
        """Validate extracted receipt data for consistency"""
        validation_prompt = f"""Validate this extracted receipt data for mathematical consistency:

{json.dumps(receipt_data, indent=2)}

Check:
1. Sum of line totals = subtotal
2. subtotal + tax = total
3. Reasonable prices for Nigerian market
4. Quantity > 0
5. Prices realistic for items

Respond with JSON:
{{
  "is_valid": true/false,
  "issues": ["issue1"],
  "suggested_corrections": {{"field": "corrected_value"}},
  "confidence": <0-1>
}}"""

        response = claude_client.call_claude(
            system_prompt=self.SYSTEM_PROMPT_RECEIPT,
            user_message=validation_prompt
        )

        return json.loads(response["content"])

receipt_processor = ReceiptProcessor()
```

---

## RAG & Context Management

### 1. Transaction History Retrieval

```python
# ai/rag_system.py
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class RAGSystem:
    """Retrieval Augmented Generation using transaction history"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.index_name = "akowe-transactions"

    def index_transactions(self, user_id: str, transactions: list) -> bool:
        """Index user's transaction history for retrieval"""
        try:
            # Convert transactions to documents
            documents = []
            metadata_list = []

            for tx in transactions:
                doc_text = f"""
Date: {tx.get('transaction_date')}
Amount: {tx.get('amount')} NGN
Category: {tx.get('category')}
Type: {tx.get('type')}
Description: {tx.get('description')}
Counterparty: {tx.get('counterparty', 'N/A')}
"""
                documents.append(doc_text)
                metadata_list.append({
                    "user_id": user_id,
                    "transaction_id": tx.get('id'),
                    "transaction_date": str(tx.get('transaction_date')),
                    "amount": tx.get('amount'),
                    "category": tx.get('category')
                })

            # Split and embed
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=200,
                chunk_overlap=50
            )

            chunks = text_splitter.create_documents(documents)

            # Store in vector database (would use Pinecone in production)
            # vector_store.add_documents(chunks, metadatas=metadata_list)

            return True
        except Exception as e:
            logger.error(f"Failed to index transactions: {str(e)}")
            return False

    def retrieve_context(self, user_id: str, query: str, k: int = 5) -> str:
        """Retrieve relevant transaction context"""
        # Example query: "What was my average daily sales last month?"

        context_docs = []  # Would retrieve from vector store
        context_text = "\n".join([f"- {doc}" for doc in context_docs])

        return context_text

    def generate_insight_with_context(self, user_id: str, query: str) -> Dict[str, Any]:
        """Generate business insight using transaction history"""
        # Retrieve relevant transactions
        context = self.retrieve_context(user_id, query)

        insight_prompt = f"""Based on this trader's transaction history:

{context}

Answer this question: {query}

Provide insights that are:
1. Specific and actionable
2. Grounded in the transaction data
3. Relevant to Nigerian MSME context
4. Formatted as clear, simple advice"""

        response = claude_client.call_claude(
            system_prompt="You are a financial advisor for Nigerian traders. Provide clear, actionable insights.",
            user_message=insight_prompt
        )

        return {
            "query": query,
            "insight": response["content"],
            "context_used": context
        }

rag_system = RAGSystem()
```

---

## Performance Optimization

### 1. Caching & Batch Processing

```python
# ai/optimization.py
import hashlib
import redis
from functools import wraps

class CacheOptimization:
    """Optimize Claude API calls with caching"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379))
        )
        self.ttl = 86400  # 24 hours

    def get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()

    def cache_decorator(self, ttl: int = None):
        """Decorator to cache Claude API responses"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.get_cache_key(str(args) + str(kwargs))

                # Try cache first
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Call function
                result = func(*args, **kwargs)

                # Cache result
                self.redis_client.setex(
                    cache_key,
                    ttl or self.ttl,
                    json.dumps(result)
                )

                return result
            return wrapper
        return decorator

    def batch_process_transactions(
        self,
        transactions: list,
        batch_size: int = 10
    ) -> list:
        """Process multiple transactions efficiently"""
        results = []

        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i+batch_size]

            # Process batch with single Claude call
            batch_prompt = f"""Process these {len(batch)} transactions and return results as JSON array:

{json.dumps(batch, indent=2)}

For each transaction return: {{
  "original_index": <index>,
  "processed_data": <extracted data>,
  "confidence": <0-1>
}}"""

            response = claude_client.call_claude(
                system_prompt="You are a batch transaction processor.",
                user_message=batch_prompt
            )

            if response["success"]:
                batch_results = json.loads(response["content"])
                results.extend(batch_results)

        return results

cache_optimization = CacheOptimization()
```

---

## Testing & Evaluation

### 1. Prompt Testing

```python
# tests/test_prompts.py
import pytest
from ai.transaction_extractor import transaction_extractor

class TestPrompts:
    """Test prompt effectiveness"""

    @pytest.fixture
    def test_cases(self):
        """Test cases with expected outputs"""
        return [
            {
                "input": "I don buy fuel for 50k",
                "dialect": "pidgin",
                "expected": {
                    "amount": 50000,
                    "type": "expense",
                    "category": "fuel"
                }
            },
            {
                "input": "Na im sell my goods for 200k",
                "dialect": "pidgin",
                "expected": {
                    "amount": 200000,
                    "type": "income",
                    "category": "sales"
                }
            }
        ]

    def test_transaction_extraction(self, test_cases):
        """Test transaction extraction accuracy"""
        for case in test_cases:
            result = transaction_extractor.extract_from_text(
                case["input"],
                dialect=case["dialect"]
            )

            assert result["amount"] == case["expected"]["amount"]
            assert result["type"] == case["expected"]["type"]
            assert result["category"] == case["expected"]["category"]

    def test_confidence_scores(self, test_cases):
        """Verify confidence scores"""
        for case in test_cases:
            result = transaction_extractor.extract_from_text(
                case["input"],
                dialect=case["dialect"]
            )

            assert 0 <= result["confidence"] <= 1
            # High confidence for clear cases
            assert result["confidence"] > 0.8

class TestImageProcessing:
    """Test receipt image processing"""

    def test_receipt_extraction(self):
        """Test receipt image extraction"""
        result = receipt_processor.process_receipt_image("test_receipt.jpg")

        assert result["success"]
        assert "items" in result
        assert "total_amount" in result
        assert result["quality_score"] > 0.7

    def test_receipt_validation(self):
        """Verify extracted data consistency"""
        result = receipt_processor.process_receipt_image("test_receipt.jpg")
        validation = receipt_processor.validate_receipt_data(result)

        assert validation["is_valid"]
```

### 2. Performance Metrics

```python
# ai/metrics.py
import time
from typing import Dict, Any

class AIMetrics:
    """Track AI system performance"""

    @staticmethod
    def measure_extraction_time(func):
        """Decorator to measure extraction time"""
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start

            result["execution_time_ms"] = duration * 1000
            return result
        return wrapper

    @staticmethod
    def calculate_accuracy(predictions: list, ground_truth: list) -> float:
        """Calculate extraction accuracy"""
        correct = sum(
            1 for pred, true in zip(predictions, ground_truth)
            if pred == true
        )
        return correct / len(predictions)

    @staticmethod
    def track_claude_costs(response: Dict) -> float:
        """Calculate API costs"""
        # Claude 3.5 Sonnet pricing (April 2026)
        input_cost_per_1k = 0.003  # $3 per 1M input tokens
        output_cost_per_1k = 0.015  # $15 per 1M output tokens

        input_tokens = response.get("usage", {}).get("input_tokens", 0)
        output_tokens = response.get("usage", {}).get("output_tokens", 0)

        cost = (
            (input_tokens / 1000000) * input_cost_per_1k +
            (output_tokens / 1000000) * output_cost_per_1k
        )

        return cost
```

---

## Summary

As an AI Engineer working on AkoweAI, you'll:

1. **Optimize Claude prompts** for dialect understanding and transaction extraction
2. **Fine-tune Whisper** for Nigerian languages (Pidgin, Yoruba, Igbo, Hausa)
3. **Develop vision pipelines** for receipt OCR and validation
4. **Implement RAG systems** for contextual financial analysis
5. **Monitor AI costs** and optimize API usage
6. **Test and evaluate** model performance continuously
7. **Handle edge cases** and unusual dialects

The key to success is deep understanding of Nigerian business context, informal language patterns, and financial terminology across different dialects.
