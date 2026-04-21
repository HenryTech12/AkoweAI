"""Claude AI service for transaction extraction."""
from anthropic import Anthropic
from config import settings
import logging
import json

logger = logging.getLogger(__name__)

client = Anthropic(api_key=settings.claude_api_key)


async def extract_transaction_from_text(text: str, dialect: str = "english", user_id: str = None) -> dict:
    """
    Extract transaction information from text using Claude.

    Args:
        text: The text to extract transaction data from
        dialect: User's preferred dialect
        user_id: User ID for context

    Returns:
        Dictionary with extracted transaction data
    """
    try:
        prompt = f"""Extract financial transaction information from the following text.
User dialect: {dialect}

Text: {text}

Please extract and return a JSON object with the following fields:
- amount (float): The transaction amount
- currency (string): Currency code (default "NGN")
- category (string): "income", "expense", or "debt"
- description (string): Brief description of the transaction
- counterparty (string, optional): The other party involved
- transaction_date (ISO format, optional): When the transaction occurred

Return ONLY valid JSON, no additional text."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse Claude's response
        response_text = message.content[0].text
        transaction_data = json.loads(response_text)

        logger.info(f"Transaction extracted for user {user_id}: {transaction_data}")
        return transaction_data

    except Exception as e:
        logger.error(f"Error extracting transaction: {str(e)}")
        raise


async def analyze_dialect(text: str) -> str:
    """
    Detect the dialect/language of the text.

    Args:
        text: Text to analyze

    Returns:
        Detected dialect
    """
    try:
        prompt = f"""Analyze the following text and determine which dialect/language it's written in.
Possible dialects: pidgin, yoruba, igbo, hausa, english

Text: {text}

Return ONLY the dialect name in lowercase, nothing else."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        dialect = message.content[0].text.strip().lower()
        return dialect

    except Exception as e:
        logger.error(f"Error detecting dialect: {str(e)}")
        return "english"


async def generate_financial_insights(transactions: list, user_dialect: str = "english") -> dict:
    """
    Generate financial insights from transactions.

    Args:
        transactions: List of transactions
        user_dialect: User's preferred dialect

    Returns:
        Dictionary with financial insights
    """
    try:
        transactions_summary = "\n".join([
            f"- {t['amount']} {t['currency']} {t['category']}: {t['description']}"
            for t in transactions
        ])

        prompt = f"""Analyze these financial transactions and provide insights in {user_dialect} English.
User's dialect preference: {user_dialect}

Transactions:
{transactions_summary}

Provide the following in JSON format:
- summary (string): Overall financial summary
- strengths (array): Positive financial indicators
- concerns (array): Areas of concern
- recommendations (array): Recommendations for improving finances
- credit_score_estimate (int): Estimated credit score 0-100"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        insights = json.loads(response_text)
        return insights

    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return {
            "summary": "Unable to generate insights at this time",
            "strengths": [],
            "concerns": [],
            "recommendations": [],
            "credit_score_estimate": 50
        }


async def generate_whatsapp_response(user_message: str, user_context: dict, dialect: str = "english") -> str:
    """
    Generate a WhatsApp response message.

    Args:
        user_message: User's message
        user_context: Context about the user (name, business type, etc.)
        dialect: User's preferred dialect

    Returns:
        Response message
    """
    try:
        prompt = f"""You are an AI assistant for AkoweAI, helping small business owners track their finances.
The user is a {user_context.get('business_type', 'business owner')} named {user_context.get('business_name', 'valued customer')}.
They prefer communication in {dialect}.

User message: {user_message}

Respond in a friendly, helpful manner in {dialect}. Keep responses concise for WhatsApp (under 200 characters if possible).
Be encouraging and practical in your financial advice."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response = message.content[0].text
        return response

    except Exception as e:
        logger.error(f"Error generating WhatsApp response: {str(e)}")
        return "I'm having trouble processing your message. Please try again."
