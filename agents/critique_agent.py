"""
Critique Agent for LinkedIn Article Generation
Evaluates article quality and provides feedback
"""

import os
import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)


class CritiqueAgent:
    """Agent responsible for evaluating article quality"""
    
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from text file"""
        prompt_file = os.path.join(os.path.dirname(__file__), "..", "text", "critique_prompt.txt")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate article quality against criteria"""
        
        logger.info(f"Starting critique evaluation for article length: {len(state.get('article', ''))} chars")
        
        prompt = self.prompt_template.format(
            article=state['article'],
            topic=state['topic']
        )

        messages = [SystemMessage(content=prompt)]
        logger.info("Calling LLM for critique evaluation")
        response = self.llm.invoke(messages)
        
        critique_text = response.content
        logger.info(f"Critique response length: {len(critique_text)} chars")
        
        # Parse critique
        if "PASS: YES" in critique_text and "ISSUES:" not in critique_text:
            state["critique_passed"] = True
            state["critique_feedback"] = []
            logger.info("Article passed critique - no issues found")
        else:
            state["critique_passed"] = False
            # Extract issues
            issues = []
            if "ISSUES:" in critique_text:
                issues_section = critique_text.split("ISSUES:")[1].strip()
                issues = [line.strip("- ").strip() for line in issues_section.split("\n") if line.strip()]
            state["critique_feedback"] = issues
            logger.info(f"Article failed critique - {len(issues)} issues found: {issues}")
        
        return state
