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
        
        article_length = len(state.get('article', ''))
        research_length = len(state.get('research_data', ''))
        revision_count = state.get('revision_count', 0)
        research_calls = state.get('research_calls', 0)
        additional_research_calls = state.get('additional_research_calls', 0)
        
        logger.info(f"Starting critique evaluation:")
        logger.info(f"  - Article length: {article_length} chars")
        logger.info(f"  - Research data length: {research_length} chars")
        logger.info(f"  - Revision count: {revision_count}")
        logger.info(f"  - Research calls: {research_calls}")
        logger.info(f"  - Additional research calls: {additional_research_calls}")
        
        # Extract all relevant state information
        max_revisions = state.get('max_revisions', 3)
        agent_call_log = state.get('agent_call_log', [])
        previous_feedback = state.get('critique_feedback', [])
        
        prompt = self.prompt_template.format(
            article=state['article'],
            topic=state['topic'],
            research_data=state.get('research_data', ''),
            revision_count=revision_count,
            max_revisions=max_revisions,
            research_calls=research_calls,
            additional_research_calls=additional_research_calls,
            agent_call_log=agent_call_log,
            previous_feedback=previous_feedback
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
