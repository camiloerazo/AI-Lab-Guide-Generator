import os
import requests
from typing import Dict, Optional
from lab_guide_format import get_lab_guide_structure, format_lab_guide_content

class AIConfig:
    """Configuration and interaction with OpenRouter's Llama Maverick model."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-4-maverick:free"  # Llama Maverick model ID
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:5000",  # Your application's URL
            "X-Title": "Lab Guide AI"  # Your application's name
        }
        self.lab_guide_structure = get_lab_guide_structure()

    def generate_lab_guide(self, 
                          subject_name: str,
                          topic_title: str,
                          topic_description: str,
                          lab_number: int,
                          difficulty_level: str,
                          estimated_duration: int,
                          additional_notes: str = "",
                          lab_guide_title: str = "") -> Optional[str]:
        """
        Generate a lab guide using the AI model.
        
        Args:
            subject_name: Name of the subject
            topic_title: Title of the weekly topic
            topic_description: Description of the weekly topic
            lab_number: Number of the lab guide
            difficulty_level: Difficulty level of the lab
            estimated_duration: Estimated duration in minutes
            additional_notes: Any additional notes for the AI
            lab_guide_title: The title of the lab guide
            
        Returns:
            Generated lab guide content or None if generation fails
        """
        try:
            # Construct the prompt
            prompt = self._construct_prompt(
                subject_name=subject_name,
                topic_title=topic_title,
                topic_description=topic_description,
                lab_number=lab_number,
                difficulty_level=difficulty_level,
                estimated_duration=estimated_duration,
                additional_notes=additional_notes,
                lab_guide_title=lab_guide_title
            )

            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert in creating detailed and educational laboratory guides.
                                 Your guides must follow a specific structure and format.
                                 IMPORTANT: Use plain text only - NO markdown, NO HTML, NO special formatting.
                                 Just use regular text with capital letters for section titles.
                                 Include all required sections and subsections.
                                 Be precise and professional in your language.
                                 Ensure all content is in Spanish.
                                 DO NOT include institutional information, headers, or formatting - focus only on the content structure."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            print("Sending prompt to AI:\n", prompt)
            print("\nAPI Request Payload:\n", payload)

            # Make the API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            print("\nAPI Response Status Code:", response.status_code)
            print("API Response Headers:\n", response.headers)
            print("API Response Body:\n", response.text)

            response.raise_for_status()

            # Extract the generated content
            result = response.json()
            print("\nAPI Response JSON:\n", result)
            
            content = result['choices'][0]['message']['content']
            print("\nGenerated Content:\n", content)

            return content

        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {str(e)}")
            if e.response is not None:
                print(f"Request Error Details - Status Code: {e.response.status_code}")
                print(f"Request Error Details - Response Body: {e.response.text}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Error parsing API response: {str(e)}")
            if 'result' in locals():
                 print("Response JSON structure:", result)
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None

    def _construct_prompt(self, 
                         subject_name: str,
                         topic_title: str,
                         topic_description: str,
                         lab_number: int,
                         difficulty_level: str,
                         estimated_duration: int,
                         additional_notes: str = "",
                         lab_guide_title: str = "") -> str:
        """Construct a detailed prompt for the AI model."""
        
        # Get the lab guide structure - we will not strictly enforce this structure now
        # structure = self.lab_guide_structure
        
        # Start building a simpler prompt
        prompt = f"""Generate a lab guide based on the following information:

Subject: {subject_name}
Weekly Topic Title: {topic_title}
Weekly Topic Description: {topic_description}
Lab Guide Title: {lab_guide_title}
Estimated Duration: {estimated_duration} minutes

"""

        prompt += """Please generate the content for the lab guide in Spanish. Focus on the core elements relevant to the topic and difficulty. Provide a title, objectives, theoretical background, materials, procedure, and analysis/conclusions. Use plain text only, no markdown or HTML."""

        return prompt

# Create a singleton instance
ai_config = AIConfig() 