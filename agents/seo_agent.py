"""
SEO and Hashtag Agent for LinkedIn Article Generation
Generates SEO keywords and hashtags
"""

import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage


class SEOHashtagAgent:
    """Agent responsible for generating SEO keywords and hashtags"""
    
    def __init__(self, llm_model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load prompt template from text file"""
        prompt_file = os.path.join(os.path.dirname(__file__), "..", "text", "seo_prompt.txt")
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO keywords and hashtags"""
        
        prompt = self.prompt_template.format(
            topic=state['topic'],
            article_content=state['article'][:800] + "..."
        )

        messages = [SystemMessage(content=prompt)]
        response = self.llm.invoke(messages)
        
        content = response.content
        
        # Parse hashtags and keywords
        hashtags = []
        keywords = []
        
        if "HASHTAGS:" in content:
            hashtag_line = content.split("HASHTAGS:")[1].split("\n")[0]
            hashtags = [tag.strip() for tag in hashtag_line.split(",")]
        
        if "KEYWORDS:" in content:
            keyword_line = content.split("KEYWORDS:")[1].split("\n")[0]
            keywords = [kw.strip() for kw in keyword_line.split(",")]
        
        state["hashtags"] = hashtags
        state["seo_keywords"] = keywords
        
        return state
