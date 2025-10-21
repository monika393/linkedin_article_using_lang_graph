"""
Runtime Monitor for LangGraph Workflow Execution
Tracks node executions, state changes, and provides runtime inspection
"""

import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RuntimeMonitor:
    """Runtime monitor for tracking workflow execution"""
    
    def __init__(self):
        self.execution_log = []
        self.node_executions = {}
        self.current_execution_id = None
    
    def start_execution(self, execution_id: str):
        """Start tracking a new execution"""
        self.current_execution_id = execution_id
        self.execution_log.append({
            "execution_id": execution_id,
            "start_time": time.time(),
            "nodes_executed": [],
            "state_changes": []
        })
        logger.info(f"Started execution tracking: {execution_id}")
    
    def log_node_execution(self, node_name: str, state: Dict[str, Any]):
        """Log a node execution"""
        if self.current_execution_id:
            execution = self.execution_log[-1]
            execution["nodes_executed"].append({
                "node": node_name,
                "timestamp": time.time(),
                "state_snapshot": {
                    "revision_count": state.get("revision_count", 0),
                    "research_calls": state.get("research_calls", 0),
                    "additional_research_calls": state.get("additional_research_calls", 0),
                    "critique_passed": state.get("critique_passed", False),
                    "article_length": len(state.get("article", "")),
                    "research_data_length": len(state.get("research_data", ""))
                }
            })
            
            if node_name not in self.node_executions:
                self.node_executions[node_name] = []
            self.node_executions[node_name].append({
                "execution_id": self.current_execution_id,
                "timestamp": time.time(),
                "state": state
            })
            
            logger.info(f"Node {node_name} executed - State: revision={state.get('revision_count', 0)}, research_calls={state.get('research_calls', 0)}")
    
    def log_conditional_edge(self, from_node: str, decision: str, state: Dict[str, Any]):
        """Log conditional edge decision"""
        if self.current_execution_id:
            execution = self.execution_log[-1]
            execution["state_changes"].append({
                "type": "conditional_edge",
                "from_node": from_node,
                "decision": decision,
                "timestamp": time.time(),
                "state_snapshot": {
                    "critique_passed": state.get("critique_passed", False),
                    "revision_count": state.get("revision_count", 0),
                    "research_calls": state.get("research_calls", 0),
                    "additional_research_calls": state.get("additional_research_calls", 0)
                }
            })
            
            logger.info(f"Conditional edge: {from_node} -> {decision}")
            print(f"CONDITIONAL EDGE: {from_node} -> {decision}")
    
    def get_execution_summary(self, execution_id: str = None):
        """Get execution summary"""
        if execution_id:
            for execution in self.execution_log:
                if execution["execution_id"] == execution_id:
                    return execution
        return self.execution_log[-1] if self.execution_log else None
    
    def get_node_executions(self, node_name: str):
        """Get all executions for a specific node"""
        return self.node_executions.get(node_name, [])
    
    def get_runtime_stats(self):
        """Get runtime statistics"""
        if not self.execution_log:
            return {"message": "No executions tracked"}
        
        total_executions = len(self.execution_log)
        node_counts = {}
        for execution in self.execution_log:
            for node_exec in execution["nodes_executed"]:
                node = node_exec["node"]
                node_counts[node] = node_counts.get(node, 0) + 1
        
        return {
            "total_executions": total_executions,
            "node_execution_counts": node_counts,
            "current_execution": self.current_execution_id
        }
