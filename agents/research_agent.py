"""
Research Agent for LinkedIn Article Generation
Gathers comprehensive research data for the given topic
"""

import os
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent responsible for researching topics and gathering relevant information"""
    
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from text file"""
        prompt_file = os.path.join(os.path.dirname(__file__), "..", "text", "research_prompt.txt")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research for the given topic"""
        topic = state["topic"]
        
        logger.info(f"Starting research for topic: {topic}")
        prompt = self.prompt_template.format(topic=topic)

        messages = [SystemMessage(content=prompt)]
        logger.info("Calling LLM for research data")
        response = self.llm.invoke(messages)
        
        state["research_data"] = response.content
        state["revision_count"] = 0
        state["max_revisions"] = 3
        state["research_calls"] = state.get("research_calls", 0) + 1
        
        logger.info(f"Research completed - Generated {len(response.content)} characters of research data")
        logger.info(f"Research calls made: {state['research_calls']}")
        return state
    
    def _call_research(self, topic: str, feedback: list) -> str:
        """Conduct additional research based on critique feedback"""
        logger.info("Conducting additional research based on critique feedback")
        
        # Load additional research prompt template
        prompt_file = os.path.join(os.path.dirname(__file__), "..", "text", "additional_research_prompt.txt")
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        # Format the prompt with topic and feedback
        feedback_text = "\n".join([f"- {issue}" for issue in feedback])
        prompt = prompt_template.format(topic=topic, feedback=feedback_text)
        
        messages = [SystemMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        logger.info(f"Additional research completed - Generated {len(response.content)} characters")
        return response.content
