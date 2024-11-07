import json
from openai import OpenAI

from config import OPENAI_API_KEY


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def analyze_patent(self, prompt: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "I am a patent analysis expert. Analyze potential patent infringement based on the given information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            print("response: ", response)
            r = response.choices[0].message.content
            print(r)
            return json.loads(response.choices[0].message.content)

        except json.JSONDecodeError:
            return {
                "infringement_likelihood": "Low",
                "claims_at_issue": [],
                "explanation": "Error analyzing patent infringement."
            }
        except Exception as e:
            return {
                "infringement_likelihood": "Low",
                "claims_at_issue": [],
                "explanation": f"Error during analysis: {str(e)}"
            }
