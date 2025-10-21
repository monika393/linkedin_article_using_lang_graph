"""
Graph Execution Logger
Provides real-time logging of LangGraph workflow execution
"""

import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class GraphExecutionLogger:
    """Logger for real-time graph execution monitoring"""
    
    def __init__(self):
        self.execution_start_time = None
        self.node_start_times = {}
        self.conditional_decisions = []
    
    def start_execution(self, execution_id: str):
        """Log start of workflow execution"""
        self.execution_start_time = time.time()
        self.conditional_decisions = []
        logger.info(f"Starting workflow execution: {execution_id}")
        print(f"WORKFLOW EXECUTION STARTED: {execution_id}")
        print("=" * 60)
    
    def log_node_start(self, node_name: str, state: Dict[str, Any]):
        """Log start of node execution"""
        self.node_start_times[node_name] = time.time()
        logger.info(f"Starting node: {node_name}")
        print(f"EXECUTING NODE: {node_name}")
        
        # Log relevant state information
        if node_name == "critique":
            print(f"   Article length: {len(state.get('article', ''))} chars")
            print(f"   Research data: {len(state.get('research_data', ''))} chars")
            print(f"   Revision: {state.get('revision_count', 0)}")
        elif node_name == "research":
            print(f"   Topic: {state.get('topic', 'N/A')}")
        elif node_name == "moderator":
            print(f"   Revision: {state.get('revision_count', 0)}")
            print(f"   Feedback items: {len(state.get('critique_feedback', []))}")
    
    def log_node_complete(self, node_name: str, state: Dict[str, Any]):
        """Log completion of node execution"""
        if node_name in self.node_start_times:
            duration = time.time() - self.node_start_times[node_name]
            logger.info(f"Completed node: {node_name} (took {duration:.2f}s)")
            print(f"COMPLETED NODE: {node_name} ({duration:.2f}s)")
            
            # Log node-specific results
            if node_name == "critique":
                passed = state.get("critique_passed", False)
                feedback_count = len(state.get("critique_feedback", []))
                print(f"   Result: {'PASSED' if passed else 'FAILED'}")
                print(f"   Issues: {feedback_count}")
            elif node_name == "research":
                research_length = len(state.get("research_data", ""))
                print(f"   Research data: {research_length} chars")
            elif node_name == "moderator":
                article_length = len(state.get("article", ""))
                print(f"   Article length: {article_length} chars")
    
    def log_conditional_edge(self, from_node: str, decision: str, state: Dict[str, Any]):
        """Log conditional edge decision"""
        self.conditional_decisions.append({
            "from_node": from_node,
            "decision": decision,
            "timestamp": time.time(),
            "state": {
                "critique_passed": state.get("critique_passed", False),
                "revision_count": state.get("revision_count", 0),
                "research_calls": state.get("research_calls", 0),
                "additional_research_calls": state.get("additional_research_calls", 0)
            }
        })
        
        logger.info(f"Conditional edge: {from_node} -> {decision}")
        print(f"CONDITIONAL EDGE: {from_node} -> {decision}")
        
        # Log decision context
        if decision == "additional_research":
            print(f"   Reason: Need more research data")
        elif decision == "revise":
            print(f"   Reason: Article needs revision")
        elif decision == "generate":
            print(f"   Reason: Article passed or max revisions reached")
    
    def log_execution_complete(self, execution_id: str, final_state: Dict[str, Any]):
        """Log completion of workflow execution"""
        if self.execution_start_time:
            total_duration = time.time() - self.execution_start_time
            logger.info(f"Workflow execution completed: {execution_id} (took {total_duration:.2f}s)")
            print("=" * 60)
            print(f"WORKFLOW EXECUTION COMPLETED: {execution_id}")
            print(f"Total duration: {total_duration:.2f}s")
            
            # Log execution summary
            revisions = final_state.get("revision_count", 0)
            research_calls = final_state.get("research_calls", 0)
            additional_research = final_state.get("additional_research_calls", 0)
            article_length = len(final_state.get("article", ""))
            
            print(f"Final stats:")
            print(f"   Article length: {article_length} chars")
            print(f"   Revisions made: {revisions}")
            print(f"   Research calls: {research_calls}")
            print(f"   Additional research: {additional_research}")
            print(f"   Conditional decisions: {len(self.conditional_decisions)}")
            
            print("=" * 60)
    
    def get_execution_summary(self):
        """Get execution summary"""
        return {
            "execution_duration": time.time() - self.execution_start_time if self.execution_start_time else 0,
            "conditional_decisions": self.conditional_decisions,
            "node_executions": len(self.node_start_times)
        }
