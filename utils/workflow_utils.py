"""
Workflow Utilities
Helper functions for workflow execution and state management
"""

import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def log_agent_call(state: dict, agent_name: str, call_type: str = "main") -> dict:
    """Log agent call and update state"""
    if "agent_call_log" not in state or not isinstance(state.get("agent_call_log"), list):
        state["agent_call_log"] = []
    
    call_id = len(state["agent_call_log"]) + 1
    call_time = time.time()
    
    call_log = {
        "call_id": call_id,
        "agent_name": agent_name,
        "call_type": call_type,
        "timestamp": call_time,
        "revision_count": state.get("revision_count", 0),
        "research_calls": state.get("research_calls", 0),
        "additional_research_calls": state.get("additional_research_calls", 0)
    }
    
    state["agent_call_log"].append(call_log)
    
    logger.info(f"Agent Call #{call_id}: {agent_name} ({call_type}) - Revision: {state.get('revision_count', 0)}")
    return state


def should_continue_revision(state: Dict[str, Any]) -> str:
    """Decide whether to revise, do additional research, or proceed to generation"""
    
    logger.info(f"Conditional edge decision - Critique passed: {state.get('critique_passed', False)}")
    logger.info(f"Revision count: {state.get('revision_count', 0)}/{state.get('max_revisions', 3)}")
    logger.info(f"Research calls: {state.get('research_calls', 0)}, Additional: {state.get('additional_research_calls', 0)}")
    
    if state["critique_passed"]:
        logger.info("Article passed critique - proceeding to generation")
        return "generate"
    elif state["revision_count"] >= state["max_revisions"]:
        logger.warning(f"Max revisions ({state['max_revisions']}) reached. Proceeding anyway.")
        print(f"Max revisions ({state['max_revisions']}) reached. Proceeding anyway.")
        return "generate"
    else:
        feedback = state.get('critique_feedback', [])
        research_calls = state.get('research_calls', 0)
        additional_research_calls = state.get('additional_research_calls', 0)
        research_data_length = len(state.get('research_data', ''))
        
        logger.info(f"Evaluating research needs - Feedback: {len(feedback)} issues, Research data: {research_data_length} chars")
        
        needs_more_research = any(keyword in str(feedback).lower() for keyword in [
            'insufficient research', 'lack of data', 'missing sources', 'outdated information',
            'need more research', 'incomplete research', 'limited sources', 'more data needed',
            'insufficient data', 'lack of sources', 'missing research', 'incomplete data',
            'limited research', 'need more data', 'insufficient sources', 'more research needed',
            'recent developments', 'current trends', 'latest information', 'up-to-date sources',
            'research integration', 'utilize research', 'use research data', 'incorporate research'
        ])
        
        research_data_insufficient = research_data_length < 2000
        no_additional_research_yet = additional_research_calls == 0
        multiple_research_attempts = research_calls + additional_research_calls >= 2
        
        if needs_more_research and (no_additional_research_yet or research_data_insufficient):
            logger.info("Additional research needed based on critique feedback")
            return "additional_research"
        elif needs_more_research and multiple_research_attempts:
            logger.info("Research already attempted multiple times - proceeding with revision")
            return "revise"
        else:
            logger.info("Proceeding with revision based on feedback")
            return "revise"


def create_initial_state(topic: str, max_revisions: int) -> Dict[str, Any]:
    """Create initial state for workflow execution"""
    return {
        "topic": topic,
        "research_data": "",
        "article": "",
        "critique_feedback": [],
        "critique_passed": False,
        "revision_count": 0,
        "max_revisions": max_revisions,
        "research_calls": 0,
        "additional_research_calls": 0,
        "agent_call_log": [],
        "image_prompt": "",
        "image_url": "",
        "linkedin_post": "",
        "hashtags": [],
        "seo_keywords": [],
        "final_output": {}
    }


def create_final_output(state: Dict[str, Any]) -> Dict[str, Any]:
    """Create final output from state"""
    return {
        "article": state["article"],
        "research_data": state["research_data"],
        "critique_feedback": state["critique_feedback"],
        "image_prompt": state["image_prompt"],
        "image_url": state["image_url"],
        "linkedin_post": state["linkedin_post"],
        "hashtags": state["hashtags"],
        "seo_keywords": state["seo_keywords"],
        "revisions_made": state["revision_count"],
        "research_calls": state.get("research_calls", 0),
        "additional_research_calls": state.get("additional_research_calls", 0),
        "agent_call_log": state.get("agent_call_log", []),
        "topic": state["topic"]
    }
