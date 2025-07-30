import re
import json
import os
from typing import Dict, Any


class PIIRedactor:
    """PII redactor that uses regex patterns to identify and replace PII."""
    
    def __init__(self):
        
        # Build regex patterns
        self._build_patterns()
    
    def _build_patterns(self):
        """Build regex patterns for PII detection."""
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        # Credit card pattern (basic - matches 13-19 digits with optional spaces/dashes)
        self.credit_card_pattern = re.compile(
            r'\b(?:\d[ -]*?){13,19}\b'
        )
        
        # Phone number pattern (US-style, but flexible)
        self.phone_pattern = re.compile(
            r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        )
        
        # SSN pattern
        self.ssn_pattern = re.compile(
            r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'
        )
        
        # Password/secret pattern (matches patterns like "password: xxx" or "secret: xxx")
        self.password_pattern = re.compile(
            r'\b(pass(word|phrase)?|secret|pwd|passwd)\s*[:=]\s*\S+',
            re.IGNORECASE
        )
        
        # Street address pattern (simplified)
        self.address_pattern = re.compile(
            r'\b\d+\s+[A-Za-z\s]+\s+(street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|court|ct|plaza|pl|terrace|ter|place|pl|way|parkway|pkwy)\b',
            re.IGNORECASE
        )
        
        # Greeting/closing patterns for name detection
        self.greeting_pattern = re.compile(
            r'(^|\.\s+)(dear|hi|hello|greetings|hey|hey there)[\s-]*',
            re.IGNORECASE
        )
        
        self.closing_pattern = re.compile(
            r'(thx|thanks|thank you|regards|best|[a-z]+ly|[a-z]+ regards|all the best|happy [a-z]+ing|take care|have a [a-z]+ (weekend|night|day))\s*[,.!]*',
            re.IGNORECASE
        )
        
        # Generic name pattern (capitalized words)
        self.generic_name_pattern = re.compile(
            r'( ?(([A-Z][a-z]+)|([A-Z]\.))+)([,.]|[,.]?$)',
            re.MULTILINE
        )
        
        
        # Credentials pattern (API keys, tokens, etc.)
        self.credentials_pattern = re.compile(
            r'\b(api[_-]?key|token|bearer|authorization|auth[_-]?token|access[_-]?token|secret[_-]?key)\s*[:=]\s*["\']?[\w-]+["\']?',
            re.IGNORECASE
        )

    def redact(self, text: str) -> str:
        """Redact PII from the given text using regex patterns."""
        if not isinstance(text, str):
            return text
        
        # Apply redactions in order
        # Credentials
        text = self.credentials_pattern.sub('<REDACTED_CREDENTIALS>', text)
        
        # Credit card numbers
        text = self.credit_card_pattern.sub('<REDACTED_CREDIT_CARD>', text)
        
        # Email addresses
        text = self.email_pattern.sub('<REDACTED_EMAIL>', text)
        
        # Phone numbers
        text = self.phone_pattern.sub('<REDACTED_PHONE>', text)
        
        # SSN
        text = self.ssn_pattern.sub('<REDACTED_SSN>', text)
        
        # Passwords/secrets
        text = self.password_pattern.sub('<REDACTED_SECRET>', text)
        
        # Street addresses
        text = self.address_pattern.sub('<REDACTED_ADDRESS>', text)
        
        # Note: IPs, URLs, usernames, and zipcodes are disabled by default
        # to match JS SDK behavior
        
        return text


def perform_pii_redaction(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact PII from event data, specifically targeting ai_data input and output fields.
    
    Args:
        event_data: The event data dictionary to redact PII from
        
    Returns:
        The event data with PII redacted
    """
    redactor = PIIRedactor()
    
    # Create a copy to avoid modifying the original
    event_copy = event_data.copy()
    
    # Redact PII from ai_data fields if they exist
    if 'ai_data' in event_copy and event_copy['ai_data']:
        ai_data = event_copy['ai_data'].copy() if event_copy['ai_data'] else {}
        
        if 'input' in ai_data and ai_data['input']:
            ai_data['input'] = redactor.redact(ai_data['input'])
        
        if 'output' in ai_data and ai_data['output']:
            ai_data['output'] = redactor.redact(ai_data['output'])
        
        event_copy['ai_data'] = ai_data
    
    return event_copy 