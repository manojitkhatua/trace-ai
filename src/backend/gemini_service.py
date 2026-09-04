import json
import os

from dotenv import load_dotenv
from google import genai


class GeminiService:
    def __init__(self, model="gemini-2.5-flash"):
        load_dotenv()

        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=key)
        self.model = model

    def explain(self, risk_data):
        prompt = f"""
You are TRACE's fraud-risk explanation layer.

TRACE has already made the final decision.
You MUST NOT change, override, or question it.

Use ONLY the supplied evidence.
Do not invent facts.

Return ONLY valid JSON in this exact structure:

{{
  "summary": "2 short sentences explaining the final risk and decision.",
  "key_factors": [
    "Most important factor.",
    "Second important factor.",
    "Important anomaly/entity observation."
  ],
  "analyst_action": "One short practical recommendation."
}}

Rules:
- Keep the language simple and professional.
- Do not use numbered sections.
- Do not use markdown.
- Do not dump raw SHAP values.
- Explain technical features in plain language.
- Do not say one SHAP feature alone caused the decision.
- Do not invent transaction history.
- Distinguish model, anomaly, and entity evidence.
- Mention the final risk score and decision.
- Keep the response concise.

TRACE evidence:
{json.dumps(risk_data, indent=2, default=str)}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = response.text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "summary": text,
                "key_factors": [],
                "analyst_action": "Review TRACE evidence if needed.",
            }