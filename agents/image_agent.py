"""
Image Generator Agent for LinkedIn Article Generation
Creates actual images using DALL-E API
"""

import os
import base64
import requests
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage


class ImageGeneratorAgent:
    """Agent responsible for generating image prompts"""
    
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.9):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from text file"""
        prompt_file = os.path.join(os.path.dirname(__file__), "..", "text", "image_prompt.txt")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actual image using DALL-E API"""
        
        # First, generate the image prompt
        prompt = self.prompt_template.format(
            topic=state['topic'],
            article_summary=state['article'][:500] + "..."
        )

        messages = [SystemMessage(content=prompt)]
        response = self.llm.invoke(messages)
        image_prompt = response.content
        
        # Now generate the actual image using DALL-E
        try:
            from openai import OpenAI
            client = OpenAI()
            
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="hd",
                n=1
            )
            
            image_url = image_response.data[0].url
            state["image_prompt"] = image_prompt
            state["image_url"] = image_url
            
        except Exception as e:
            # Fallback to placeholder if DALL-E fails
            print(f"DALL-E generation failed: {e}")
            state["image_prompt"] = image_prompt
            state["image_url"] = f"[DALL-E Error: {str(e)}]"
        
        return state
