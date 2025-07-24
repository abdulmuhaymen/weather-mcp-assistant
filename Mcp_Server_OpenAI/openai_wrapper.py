import json
import re

class OpenAIWrapper:
    def __init__(self, api_key, model="gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, prompt: str):
        """For structured JSON responses (tool selection)"""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a JSON API router. "
                    "Your only job is to read the user query and return the correct tool name with arguments as a JSON object. "
                    "Only return JSON. Never explain. Never include any text or comments. "
                    "Respond strictly in this format: "
                    '{"tool": "tool_name", "args": {"param": "value"}} '
                    "IMPORTANT: For apply_leave function, use EXACT parameter names: employee_id, leave_type, start_date, end_date, reason "
                    "If employee_id is not provided, ask user to provide it or use a placeholder like 'MISSING_EMP_ID'"
                )
            },
            {
                "role": "user",
                "content": prompt.strip()
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1  # Lower temperature for more consistent formatting
        )

        content = response.choices[0].message.content.strip()

        # Optional: Try to correct common JSON formatting issues
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                # Fix: remove trailing commas, smart quotes, etc.
                fixed = re.sub(r"(\w+):", r'"\1":', content)  # Add quotes around keys if missing
                fixed = fixed.replace(""", '"').replace(""", '"').replace("'", "'")
                return json.loads(fixed)
            except Exception as e:
                raise ValueError(f"Invalid JSON returned by LLM: {content}") from e

    def chat_text(self, prompt: str) -> str:
        """For natural language text responses (response formatting)"""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful meteorological assistant. "
                    "Your job is to explain weather data in clear, conversational language. "
                    "Always provide natural, informative responses that are easy to understand. "
                    "Don't include JSON or raw data in your responses - just natural language explanations."
                )
            },
            {
                "role": "user",
                "content": prompt.strip()
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7  # Higher temperature for more natural responses
        )

        return response.choices[0].message.content.strip()