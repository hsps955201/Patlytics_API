# -*- coding: utf-8 -*-
import json
import google.generativeai as genai

from config import GEMINI_API_KEY


class GeminiService:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.api_key = GEMINI_API_KEY
        genai.configure(api_key=self.api_key)

        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config
        )

    def analyze_patent(self, prompt: str) -> dict:
        try:
            formatted_prompt = f"""You are a patent analysis expert. Analyze potential patent infringement based on the given information.
            
            Important: Your response must be a valid JSON object.
            
            {prompt}
            
            Remember to format your response as a valid JSON object."""

            chat = self.model.start_chat(history=[])
            response = chat.send_message(formatted_prompt)

            try:
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.replace(
                        "```json", "").replace("```", "")
                return json.loads(response_text)

            except json.JSONDecodeError:
                return {
                    "analyses": [{
                        "infringement_likelihood": "Low",
                        "claims_at_issue": [],
                        "explanation": "Error parsing patent analysis response."
                    }]
                }

        except Exception as e:
            return {
                "analyses": [{
                    "infringement_likelihood": "Low",
                    "claims_at_issue": [],
                    "explanation": f"Error during analysis: {str(e)}"
                }]
            }
