"""
Centralized logging utilities for the LinkedIn Article Generation system
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime


class WorkflowLogger:
    """Centralized logging for workflow execution"""
    
    def __init__(self, name: str = "linkedin_article_workflow", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers for console and file output"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        file_handler = logging.FileHandler('workflow_execution.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def log_workflow_start(self, topic: str, execution_id: str = None):
        """Log workflow start"""
        self.logger.info(f"Starting LinkedIn Article Generation Workflow")
        self.logger.info(f"Topic: {topic}")
        if execution_id:
            self.logger.info(f"Execution ID: {execution_id}")
    
    def log_workflow_complete(self, execution_id: str = None, duration: float = None):
        """Log workflow completion"""
        self.logger.info("LinkedIn Article Generation Workflow completed")
        if execution_id:
            self.logger.info(f"Execution ID: {execution_id}")
        if duration:
            self.logger.info(f"Total duration: {duration:.2f}s")
    
    def log_agent_call(self, agent_name: str, call_type: str = "main", revision: int = 0):
        """Log agent call"""
        self.logger.info(f"Agent Call: {agent_name} ({call_type}) - Revision: {revision}")
    
    def log_agent_completion(self, agent_name: str, result_length: int = None, duration: float = None):
        """Log agent completion"""
        message = f"Completed: {agent_name}"
        if result_length:
            message += f" - Output length: {result_length} chars"
        if duration:
            message += f" - Duration: {duration:.2f}s"
        self.logger.info(message)
    
    def log_critique_result(self, passed: bool, issues_count: int = 0):
        """Log critique evaluation result"""
        if passed:
            self.logger.info("Article passed critique - no issues found")
        else:
            self.logger.warning(f"Article failed critique - {issues_count} issues found")
    
    def log_revision_decision(self, decision: str, feedback: list = None):
        """Log revision decision"""
        self.logger.info(f"Revision decision: {decision}")
        if feedback:
            self.logger.info(f"Feedback items: {len(feedback)}")
    
    def log_research_call(self, call_type: str, research_length: int):
        """Log research agent call"""
        self.logger.info(f"Research call ({call_type}) - Data length: {research_length} chars")
    
    def log_export_attempt(self, output_dir: str, file_types: list):
        """Log export attempt"""
        self.logger.info(f"Starting export to directory: {output_dir}")
        self.logger.info(f"Exporting file types: {', '.join(file_types)}")
    
    def log_export_success(self, export_paths: Dict[str, str]):
        """Log successful export"""
        self.logger.info("Export successful")
        for file_type, path in export_paths.items():
            self.logger.info(f"  {file_type}: {path}")
    
    def log_export_failure(self, error: Exception):
        """Log export failure"""
        self.logger.error(f"Export failed: {error}")
        self.logger.error(f"Export error traceback: {error}")
    
    def log_conditional_edge(self, from_node: str, decision: str, state: Dict[str, Any]):
        """Log conditional edge decision"""
        self.logger.info(f"Conditional edge: {from_node} -> {decision}")
        
        if decision == "additional_research":
            self.logger.info("  Reason: Need more research data")
        elif decision == "revise":
            self.logger.info("  Reason: Article needs revision")
        elif decision == "generate":
            self.logger.info("  Reason: Article passed or max revisions reached")
    
    def log_runtime_stats(self, stats: Dict[str, Any]):
        """Log runtime statistics"""
        self.logger.info("Runtime statistics:")
        for key, value in stats.items():
            self.logger.info(f"  {key}: {value}")
    
    def log_visualization_generation(self, graph_type: str, output_file: str, success: bool):
        """Log visualization generation"""
        if success:
            self.logger.info(f"{graph_type} visualization saved to: {output_file}")
        else:
            self.logger.error(f"Failed to generate {graph_type} visualization")
    
    def log_langgraph_workflow_info(self, nodes: list, edges: list):
        """Log LangGraph workflow information"""
        self.logger.info(f"LangGraph workflow - Nodes: {len(nodes)}, Edges: {len(edges)}")
        self.logger.info(f"Nodes: {nodes}")
        self.logger.info(f"Edges: {edges}")
    
    def log_execution_summary(self, execution_id: str, summary: Dict[str, Any]):
        """Log execution summary"""
        self.logger.info(f"Execution summary for {execution_id}:")
        for key, value in summary.items():
            self.logger.info(f"  {key}: {value}")
    
    def log_workflow_visualization(self, graph_type: str, output_file: str, success: bool):
        """Log workflow visualization generation"""
        if success:
            self.logger.info(f"{graph_type} visualization saved to: {output_file}")
        else:
            self.logger.error(f"Failed to generate {graph_type} visualization")
    
    def log_langgraph_workflow_info(self, nodes: list, edges: list):
        """Log LangGraph workflow information"""
        self.logger.info(f"LangGraph workflow - Nodes: {len(nodes)}, Edges: {len(edges)}")
        self.logger.info(f"Nodes: {nodes}")
        self.logger.info(f"Edges: {edges}")
    
    def log_runtime_inspection(self, execution_id: str, execution_summary: Dict[str, Any], stats: Dict[str, Any]):
        """Log runtime inspection results"""
        self.logger.info(f"Runtime inspection for execution {execution_id}")
        if execution_summary:
            self.logger.info(f"Nodes executed: {len(execution_summary.get('nodes_executed', []))}")
            for node_exec in execution_summary.get('nodes_executed', []):
                node = node_exec['node']
                state_snapshot = node_exec['state_snapshot']
                self.logger.info(f"  {node}: revision={state_snapshot['revision_count']}, research_calls={state_snapshot['research_calls']}")
        self.logger.info(f"Runtime stats: {stats}")


def get_workflow_logger(name: str = "linkedin_article_workflow") -> WorkflowLogger:
    """Get a workflow logger instance"""
    return WorkflowLogger(name)


def setup_logging(level: int = logging.INFO) -> WorkflowLogger:
    """Setup centralized logging for the workflow"""
    return WorkflowLogger(level=level)
