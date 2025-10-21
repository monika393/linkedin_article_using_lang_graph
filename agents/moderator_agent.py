"""
Moderator Agent for LinkedIn Article Generation
Revises articles based on critique feedback
"""

import os
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)


class ModeratorAgent:
    """Agent responsible for revising articles based on feedback"""
    
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from text file"""
        prompt_file = os.path.join(os.path.dirname(__file__), "..", "text", "moderator_prompt.txt")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Revise article based on critique feedback"""
        
        feedback = state["critique_feedback"]
        logger.info(f"Starting revision {state['revision_count'] + 1} with feedback: {feedback}")
        
        # Log research data length to ensure it includes additional research
        research_length = len(state.get('research_data', ''))
        logger.info(f"Moderator using research data length: {research_length} characters")
        
        # Check if research data contains additional research
        if "--- ADDITIONAL RESEARCH ---" in state.get('research_data', ''):
            logger.info("Moderator detected additional research in research data")
        else:
            logger.info("Moderator using only original research data")
        
        feedback_text = "\n".join([f"- {issue}" for issue in feedback])
        
        prompt = self.prompt_template.format(
            article=state['article'],
            research_data=state['research_data'],
            feedback_text=feedback_text,
            revision_count=state['revision_count'] + 1
        )

        messages = [SystemMessage(content=prompt)]
        logger.info("Calling LLM for article revision")
        response = self.llm.invoke(messages)
        
        old_length = len(state["article"])
        state["article"] = response.content
        state["revision_count"] += 1
        
        logger.info(f"Revision completed - Article length changed from {old_length} to {len(response.content)} chars")
        return state
