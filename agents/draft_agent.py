"""
Draft Writer Agent for LinkedIn Article Generation
Creates initial article drafts from research data
"""

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage


class DraftWriterAgent:
    """Agent responsible for creating initial article drafts"""
    
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from text file"""
        prompt_file = os.path.join(os.path.dirname(__file__), "..", "text", "draft_prompt.txt")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create initial article draft from research"""
        
        prompt = self.prompt_template.format(
            topic=state['topic'],
            research_data=state['research_data']
        )

        messages = [SystemMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        state["article"] = response.content
        return state
