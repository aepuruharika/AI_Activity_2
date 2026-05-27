# Simple PII Consent Handler (5 minutes of work)
# Add to main.py imports

from datetime import datetime
from typing import Dict, Any

class ConsentHandler:
    """Track and validate user consent for PII handling."""

    def __init__(self):
        self.consents = []

    def record_consent(self, user_consent: bool) -> Dict[str, Any]:
        """Record user consent for external LLM processing."""
        if not user_consent:
            return {
                "error": "User must consent to external LLM processing",
                "accepted": False
            }

        record = {
            "timestamp": datetime.now().isoformat(),
            "accepted": True,
            "data_shared": [
                "Skills (technical proficiencies)",
                "Years of experience",
                "Education level",
                "Experience summary",
                "Certifications"
            ],
            "data_protected": [
                "Name - NOT SENT to LLM",
                "Email - NOT SENT to LLM",
                "Phone - NOT SENT to LLM",
                "Full resume text - NOT SENT to LLM"
            ],
            "external_processor": "HuggingFace (Llama 3.1 8B)",
            "privacy_policy": "https://huggingface.co/privacy"
        }

        self.consents.append(record)
        print(f"[CONSENT] Recorded at {record['timestamp']}")
        return record

# Create global instance
consent_handler = ConsentHandler()

def get_consent_handler() -> ConsentHandler:
    return consent_handler
