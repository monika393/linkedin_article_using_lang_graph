"""
LinkedIn Article Generation Workflow using LangGraph
Orchestrates the sequential and parallel agent execution
"""

import logging
import uuid
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END
from agents import (
    ResearchAgent, DraftWriterAgent, CritiqueAgent, ModeratorAgent,
    ImageGeneratorAgent, PostCreatorAgent, SEOHashtagAgent
)
from utils import create_article_package, get_config, validate_config
from utils.workflow_utils import log_agent_call, should_continue_revision, create_initial_state, create_final_output
from utils.visualization_utils import WorkflowVisualizer
from utils.logging_utils import WorkflowLogger
from monitoring import RuntimeMonitor
from graph_logging import GraphExecutionLogger

logger = logging.getLogger(__name__)


class ArticleState(TypedDict):
    topic: str
    research_data: str
    article: str
    critique_feedback: list
    critique_passed: bool
    revision_count: int
    max_revisions: int
    # Execution tracking
    research_calls: int
    additional_research_calls: int
    agent_call_log: list
    # Parallel outputs
    image_prompt: str
    image_url: str
    linkedin_post: str
    hashtags: list
    seo_keywords: list
    final_output: dict


class LinkedInArticleWorkflow:
    """Main workflow orchestrator for LinkedIn article generation"""
    
    def __init__(self):
        # Load configuration
        self.config = get_config()
        
        # Validate configuration
        if not validate_config():
            raise ValueError("Invalid configuration. Please check your .env file and set OPENAI_API_KEY.")
        
        # Initialize runtime monitoring and logging
        self.runtime_monitor = RuntimeMonitor()
        self.graph_logger = GraphExecutionLogger()
        self.workflow_logger = WorkflowLogger()
        self.visualizer = WorkflowVisualizer()
        
        # Initialize agents with configuration
        model_config = self.config.get_model_config()
        creative_config = self.config.get_creative_model_config()
        
        self.research_agent = ResearchAgent(
            llm_model=model_config["model"],
            temperature=model_config["temperature"]
        )
        self.draft_agent = DraftWriterAgent(
            llm_model=model_config["model"],
            temperature=model_config["temperature"]
        )
        self.critique_agent = CritiqueAgent(
            llm_model=model_config["model"],
            temperature=model_config["temperature"]
        )
        self.moderator_agent = ModeratorAgent(
            llm_model=model_config["model"],
            temperature=model_config["temperature"]
        )
        self.image_agent = ImageGeneratorAgent(
            llm_model=creative_config["model"],
            temperature=creative_config["temperature"]
        )
        self.post_agent = PostCreatorAgent(
            llm_model=model_config["model"],
            temperature=model_config["temperature"]
        )
        self.seo_agent = SEOHashtagAgent(
            llm_model=model_config["model"],
            temperature=model_config["temperature"]
        )
    
    def _research_node(self, state: ArticleState) -> ArticleState:
        """Research agent wrapper for LangGraph"""
        state = self.research_agent(state)
        log_agent_call(state, "ResearchAgent", "research")
        return state
    
    def _draft_node(self, state: ArticleState) -> ArticleState:
        """Draft agent wrapper for LangGraph"""
        state = self.draft_agent(state)
        log_agent_call(state, "DraftWriterAgent", "draft")
        return state
    
    def _critique_node(self, state: ArticleState) -> ArticleState:
        """Critique agent wrapper for LangGraph"""
        state = self.critique_agent(state)
        log_agent_call(state, "CritiqueAgent", "critique")
        return state
    
    def _moderator_node(self, state: ArticleState) -> ArticleState:
        """Moderator agent wrapper for LangGraph"""
        state = self.moderator_agent(state)
        log_agent_call(state, "ModeratorAgent", "moderator")
        return state
    
    def _image_node(self, state: ArticleState) -> ArticleState:
        """Image agent wrapper for LangGraph"""
        state = self.image_agent(state)
        log_agent_call(state, "ImageGeneratorAgent", "image")
        return state
    
    def _post_node(self, state: ArticleState) -> ArticleState:
        """Post agent wrapper for LangGraph"""
        state = self.post_agent(state)
        log_agent_call(state, "PostCreatorAgent", "post")
        return state
    
    def _seo_node(self, state: ArticleState) -> ArticleState:
        """SEO agent wrapper for LangGraph"""
        state = self.seo_agent(state)
        log_agent_call(state, "SEOHashtagAgent", "seo")
        return state
    
    def _additional_research_node(self, state: ArticleState) -> ArticleState:
        """Additional research node wrapper for LangGraph"""
        # Call research agent for additional research
        state = self.research_agent(state)
        state["additional_research_calls"] = state.get("additional_research_calls", 0) + 1
        log_agent_call(state, "ResearchAgent", "additional_research")
        return state
    
    def _final_assembly_node(self, state: ArticleState) -> ArticleState:
        """Final assembly node wrapper for LangGraph"""
        final_output = create_final_output(state)
        state["final_output"] = final_output
        log_agent_call(state, "FinalAssembly", "final_assembly")
        return state
    
    def _log_agent_call(self, state: dict, agent_name: str, call_type: str = "main") -> dict:
        """Log agent call and update state"""
        return log_agent_call(state, agent_name, call_type)
    
    def _build_langgraph_workflow(self):
        """Build the LangGraph StateGraph workflow for visualization"""
        
        # Create the StateGraph
        workflow = StateGraph(ArticleState)
        
        # Add nodes (agents)
        workflow.add_node("research", self._research_node)
        workflow.add_node("draft", self._draft_node)
        workflow.add_node("critique", self._critique_node)
        workflow.add_node("moderator", self._moderator_node)
        workflow.add_node("additional_research", self._additional_research_node)
        workflow.add_node("image", self._image_node)
        workflow.add_node("post", self._post_node)
        workflow.add_node("seo", self._seo_node)
        workflow.add_node("final_assembly", self._final_assembly_node)
        
        # Add explicit START and END edges
        workflow.add_edge(START, "research")
        
        # Add edges
        workflow.add_edge("research", "draft")
        workflow.add_edge("draft", "critique")
        
        # Conditional edge from critique
        workflow.add_conditional_edges(
            "critique",
            self._should_continue_revision,
            {
                "revise": "moderator",
                "additional_research": "additional_research", 
                "generate": "image"
            }
        )
        
        # Additional research flow
        workflow.add_edge("additional_research", "moderator")
        workflow.add_edge("moderator", "critique")
        
        # Parallel generation after critique passes
        workflow.add_edge("image", "post")
        workflow.add_edge("post", "seo")
        workflow.add_edge("seo", "final_assembly")
        workflow.add_edge("final_assembly", END)
        
        compiled_workflow = workflow.compile()
        
        # Visualize the compiled graph
        self._visualize_compiled_graph(compiled_workflow)
        
        return compiled_workflow
    
    def _visualize_compiled_graph(self, compiled_workflow):
        """Visualize the compiled LangGraph workflow"""
        try:
            graph = compiled_workflow.get_graph()
            
            print("\nLANGGRAPH COMPILED WORKFLOW VISUALIZATION")
            print("=" * 50)
            
            if hasattr(graph, 'nodes'):
                nodes = graph.nodes() if callable(graph.nodes) else graph.nodes
                nodes_list = list(nodes)
                print(f"Nodes ({len(nodes_list)}): {nodes_list}")
                self.workflow_logger.log_langgraph_workflow_info(nodes_list, [])
            
            if hasattr(graph, 'edges'):
                edges = graph.edges() if callable(graph.edges) else graph.edges
                edges_list = list(edges)
                print(f"Edges ({len(edges_list)}): {edges_list}")
            
            # Generate PNG visualization using centralized utility
            png_result = self.visualizer.generate_langgraph_png(compiled_workflow, "langgraph_workflow.png")
            self.workflow_logger.log_workflow_visualization("LangGraph PNG", "langgraph_workflow.png", png_result is not None)
            
            print("\nWorkflow Structure:")
            print("START -> research -> draft -> critique -> [conditional]")
            print("  critique -> revise: moderator -> critique (loop)")
            print("  critique -> additional_research: additional_research -> moderator -> critique (loop)")
            print("  critique -> generate: image -> post -> seo -> final_assembly -> END")
            print("=" * 50)
            
        except Exception as e:
            logger.error(f"Failed to visualize compiled graph: {e}")
            print(f"Graph visualization failed: {e}")
    
    def generate_graph_visualization(self, filename: str = "langgraph_workflow.png"):
        """Generate a standalone graph visualization"""
        app = self._build_langgraph_workflow()
        result = self.visualizer.generate_langgraph_png(app, filename)
        self.workflow_logger.log_workflow_visualization("Standalone PNG", filename, result is not None)
        return result
    
    def inspect_runtime_state(self, execution_id: str = None):
        """Inspect the current runtime state of the graph"""
        try:
            # Get current execution state
            if execution_id:
                state = self.runtime_monitor.get_execution_summary(execution_id)
                logger.info(f"Runtime state for execution {execution_id}: {state}")
                return state
            else:
                # Get all executions
                stats = self.runtime_monitor.get_runtime_stats()
                logger.info(f"Runtime stats: {stats}")
                return stats
        except Exception as e:
            logger.error(f"Failed to inspect runtime state: {e}")
            return None
    
    def inspect_node_execution(self, node_name: str, execution_id: str = None):
        """Inspect execution details for a specific node"""
        try:
            if execution_id:
                # Get node executions for specific execution
                node_executions = self.runtime_monitor.get_node_executions(node_name)
                filtered_executions = [exec for exec in node_executions if exec.get("execution_id") == execution_id]
                logger.info(f"Node {node_name} executions for {execution_id}: {len(filtered_executions)}")
                return filtered_executions
            else:
                # Get all executions for this node
                node_executions = self.runtime_monitor.get_node_executions(node_name)
                logger.info(f"Node {node_name} executions: {len(node_executions)}")
                return node_executions
        except Exception as e:
            logger.error(f"Failed to inspect node {node_name}: {e}")
            return None
    
    def get_execution_trace(self, execution_id: str):
        """Get the complete execution trace for a workflow run"""
        try:
            trace = self.runtime_monitor.get_execution_summary(execution_id)
            logger.info(f"Execution trace for {execution_id}: {trace}")
            return trace
        except Exception as e:
            logger.error(f"Failed to get execution trace: {e}")
            return None
    
    def _additional_research_node(self, state: ArticleState) -> ArticleState:
        """Node for additional research based on critique feedback"""
        feedback = state["critique_feedback"]
        logger.info("Conducting additional research based on critique feedback")
        
        state["additional_research_calls"] = state.get("additional_research_calls", 0) + 1
        state = self._log_agent_call(state, "ResearchAgent", f"additional_{state['additional_research_calls']}")
        
        additional_research = self.research_agent._call_research(state['topic'], feedback)
        if additional_research:
            state["research_data"] += "\n\n--- ADDITIONAL RESEARCH ---\n" + additional_research
            logger.info(f"Additional research added - Total research length: {len(state['research_data'])} chars")
        
        return state
    
    def _final_assembly_node(self, state: ArticleState) -> ArticleState:
        """Node for final assembly of all components"""
        logger.info("Assembling final output")
        
        state["final_output"] = {
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
        
        return state
    
    def generate_visual_graph(self, output_file: str = "workflow_graph.html"):
        """Generate a visual graph of the workflow using Pyvis"""
        app = self._build_langgraph_workflow()
        result = self.visualizer.generate_workflow_graph(app, output_file)
        self.workflow_logger.log_workflow_visualization("Workflow HTML", output_file, result is not None)
        return result
    
    def generate_execution_graph(self, execution_data: Dict[str, Any], output_file: str = "execution_graph.html"):
        """Generate a visual graph with actual execution data and call counts"""
        app = self._build_langgraph_workflow()
        result = self.visualizer.generate_execution_graph(app, execution_data, output_file)
        self.workflow_logger.log_visualization_generation("Execution", output_file, result is not None)
        return result
    
    def generate_article_with_langgraph(self, topic: str, export_files: bool = None, output_dir: str = None) -> Dict[str, Any]:
        """Generate article using LangGraph StateGraph for visualization"""
        
        if export_files is None:
            export_config = self.config.get_export_config()
            export_files = export_config["export_word_documents"] or export_config["export_jpeg_images"]
        
        if output_dir is None:
            export_config = self.config.get_export_config()
            output_dir = export_config["default_output_dir"]
        
        workflow_config = self.config.get_workflow_config()
        
        print("Starting LinkedIn Article Generation Workflow with LangGraph...")
        print(f"Topic: {topic}\n")
        
        initial_state = create_initial_state(topic, workflow_config["max_revisions"])
        
        app = self._build_langgraph_workflow()
        
        print("Running LangGraph workflow...")
        print("You can visualize this workflow in real-time!")
        print("Runtime Monitor is tracking execution state...")
        
        execution_id = str(uuid.uuid4())[:8]
        self.runtime_monitor.start_execution(execution_id)
        
        final_state = app.invoke(initial_state)
        
        print("\n" + "="*60)
        print("RUNTIME STATE INSPECTION")
        print("="*60)
        
        execution_summary = self.inspect_runtime_state(execution_id)
        if execution_summary:
            print(f"Execution ID: {execution_id}")
            print(f"Nodes executed: {len(execution_summary.get('nodes_executed', []))}")
            
            for node_exec in execution_summary.get('nodes_executed', []):
                node = node_exec['node']
                state_snapshot = node_exec['state_snapshot']
                print(f"  {node}: revision={state_snapshot['revision_count']}, research_calls={state_snapshot['research_calls']}")
        
        stats = self.runtime_monitor.get_runtime_stats()
        print(f"Runtime stats: {stats}")
        
        print("="*60)
        
        print("LangGraph workflow completed!")
        
        # Ensure we have a proper final output
        if "final_output" not in final_state or not isinstance(final_state["final_output"], dict):
            logger.warning("final_output not found in final_state, creating from state")
            final_output = create_final_output(final_state)
        else:
            final_output = final_state["final_output"]
        
        if export_files:
            print("Exporting files...")
            try:
                export_paths = create_article_package(final_output, output_dir)
                final_output['export_paths'] = export_paths
                print(f"Files exported to: {output_dir}")
            except Exception as e:
                logger.error(f"Export failed: {e}")
                final_output['export_paths'] = None
        
        return final_output
    
    def _should_continue_revision(self, state: ArticleState) -> str:
        """Decide whether to revise, do additional research, or proceed to generation"""
        decision = should_continue_revision(state)
        
        self.runtime_monitor.log_conditional_edge("critique", decision, state)
        self.graph_logger.log_conditional_edge("critique", decision, state)
        self.workflow_logger.log_conditional_edge("critique", decision, state)
        
        return decision
    
    def generate_article(self, topic: str, export_files: bool = None, output_dir: str = None) -> Dict[str, Any]:
        """Generate a complete LinkedIn article with all components"""
        
        if export_files is None:
            export_config = self.config.get_export_config()
            export_files = export_config["export_word_documents"] or export_config["export_jpeg_images"]
        
        if output_dir is None:
            export_config = self.config.get_export_config()
            output_dir = export_config["default_output_dir"]
        
        workflow_config = self.config.get_workflow_config()
        
        print("Starting LinkedIn Article Generation Workflow...")
        print(f"Topic: {topic}\n")
        
        self.workflow_logger.log_workflow_start(topic)
        state = create_initial_state(topic, workflow_config["max_revisions"])
        
        print("Step 1: Researching topic...")
        logger.info("Starting research phase")
        state = self._log_agent_call(state, "ResearchAgent", "initial")
        state = self.research_agent(state)
        research_length = len(state.get('research_data', ''))
        logger.info(f"Research completed - Data length: {research_length} chars")
        self.workflow_logger.log_research_call("initial", research_length)
        print("Research completed")
        
        print("Step 2: Creating initial draft...")
        logger.info("Starting draft phase")
        state = self._log_agent_call(state, "DraftAgent", "initial")
        state = self.draft_agent(state)
        article_length = len(state.get('article', ''))
        logger.info(f"Draft completed - Article length: {article_length} chars")
        self.workflow_logger.log_agent_completion("DraftAgent", article_length)
        print("Draft completed")
        
        print("Step 3: Evaluating and revising article...")
        logger.info("Starting critique and revision phase")
        max_revisions = state["max_revisions"]
        
        for revision in range(max_revisions + 1):
            print(f"   Revision {revision + 1}/{max_revisions + 1}")
            logger.info(f"Critique revision {revision + 1}/{max_revisions + 1}")
            state = self._log_agent_call(state, "CritiqueAgent", f"revision_{revision + 1}")
            state = self.critique_agent(state)
            
            if state["critique_passed"]:
                logger.info("Article passed critique")
                self.workflow_logger.log_critique_result(True)
                print("Article passed critique")
                break
            elif revision < max_revisions:
                feedback = state.get('critique_feedback', [])
                logger.info(f"Revising based on feedback: {feedback}")
                self.workflow_logger.log_critique_result(False, len(feedback))
                print("   Revising based on feedback...")
                print(f"   Critique feedback: {feedback}")
                
                needs_more_research = any(keyword in str(feedback).lower() for keyword in [
                    'insufficient research', 'lack of data', 'missing sources', 'outdated information',
                    'need more research', 'incomplete research', 'limited sources', 'more data needed',
                    'insufficient data', 'lack of sources', 'missing research', 'incomplete data',
                    'limited research', 'need more data', 'insufficient sources', 'more research needed',
                    'recent developments', 'current trends', 'latest information', 'up-to-date sources'
                ])
                
                if needs_more_research:
                    logger.info("Critique indicates need for additional research - conducting supplementary research")
                    print("   Conducting additional research based on feedback...")
                    state["additional_research_calls"] = state.get("additional_research_calls", 0) + 1
                    logger.info(f"Additional research call #{state['additional_research_calls']}")
                    
                    state = self._log_agent_call(state, "ResearchAgent", f"additional_{state['additional_research_calls']}")
                    additional_research = self.research_agent._call_research(state['topic'], feedback)
                    if additional_research:
                        state["research_data"] += "\n\n--- ADDITIONAL RESEARCH ---\n" + additional_research
                        total_research_length = len(state['research_data'])
                        logger.info(f"Additional research added - Total research length: {total_research_length} chars")
                        logger.info(f"Total additional research calls: {state['additional_research_calls']}")
                        self.workflow_logger.log_research_call("additional", total_research_length)
                
                state = self._log_agent_call(state, "ModeratorAgent", f"revision_{revision + 1}")
                state = self.moderator_agent(state)
            else:
                logger.warning("Max revisions reached, proceeding with current version")
                print("Max revisions reached, proceeding with current version")
                break
        
        print("Step 4: Generating supporting content...")
        
        print("   Creating image prompt...")
        state = self._log_agent_call(state, "ImageAgent", "final")
        state = self.image_agent(state)
        print("Image prompt generated")
        
        print("   Creating LinkedIn post...")
        state = self._log_agent_call(state, "PostAgent", "final")
        state = self.post_agent(state)
        print("LinkedIn post created")
        
        print("   Generating SEO keywords and hashtags...")
        state = self._log_agent_call(state, "SEOAgent", "final")
        state = self.seo_agent(state)
        print("SEO content generated")
        
        print("Step 5: Assembling final output...")
        final_output = create_final_output(state)
        
        if export_files:
            print("Step 6: Exporting files...")
            logger.info(f"Starting export to directory: {output_dir}")
            
            file_types = ["word_document", "jpeg_image"]
            self.workflow_logger.log_export_attempt(output_dir, file_types)
            
            logger.info(f"Final output keys: {list(final_output.keys())}")
            logger.info(f"Article length: {len(final_output.get('article', ''))}")
            logger.info(f"LinkedIn post: {final_output.get('linkedin_post', 'MISSING')}")
            logger.info(f"Hashtags: {final_output.get('hashtags', 'MISSING')}")
            logger.info(f"SEO keywords: {final_output.get('seo_keywords', 'MISSING')}")
            
            try:
                export_paths = create_article_package(final_output, output_dir)
                final_output['export_paths'] = export_paths
                logger.info(f"Export successful: {export_paths}")
                self.workflow_logger.log_export_success(export_paths)
                print(f"Files exported to: {output_dir}")
                print(f"   Word document: {export_paths['word_document']}")
                print(f"   JPEG image: {export_paths['image_file']}")
            except Exception as e:
                logger.error(f"Export failed: {e}")
                self.workflow_logger.log_export_failure(e)
                print(f"Export failed: {e}")
                import traceback
                logger.error(f"Export error traceback: {traceback.format_exc()}")
                final_output['export_paths'] = None
        else:
            logger.info("Export files disabled")
        
        print("\nArticle generation completed!")
        self.workflow_logger.log_workflow_complete()
        return final_output
    
    def display_results(self, output: Dict[str, Any]):
        """Display the generated results in a formatted way"""
        print("\n" + "="*80)
        print("WORKFLOW COMPLETE!")
        print("="*80)
        
        print(f"\nRevisions Made: {output['revisions_made']}")
        print(f"\nArticle ({len(output['article'])} chars):")
        print(output['article'][:300] + "...\n")
        
        print(f"Image Prompt:")
        print(output['image_prompt'][:200] + "...\n")
        
        print(f"LinkedIn Post:")
        print(output['linkedin_post'])
        
        print(f"\nHashtags: {' '.join(output['hashtags'])}")
        print(f"SEO Keywords: {', '.join(output['seo_keywords'][:5])}...")
