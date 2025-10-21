"""
Image Generator Agent for LinkedIn Article Generation
Creates image prompts for article visuals
"""

import os
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
        """Generate HD abstract image prompt for the article"""
        
        prompt = self.prompt_template.format(
            topic=state['topic'],
            article_summary=state['article'][:500] + "..."
        )

        messages = [SystemMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        state["image_prompt"] = response.content
        state["image_url"] = f"[Generated image from: {response.content[:100]}...]"
        
        return state
