"""
LinkedIn Article Generation Workflow using LangGraph
Orchestrates the sequential and parallel agent execution
"""

import logging
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from agents import (
    ResearchAgent, DraftWriterAgent, CritiqueAgent, ModeratorAgent,
    ImageGeneratorAgent, PostCreatorAgent, SEOHashtagAgent
)
from utils import create_article_package, get_config, validate_config
import time

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
    
    def _log_agent_call(self, state: dict, agent_name: str, call_type: str = "main") -> dict:
        """Log agent call and update state"""
        import time
        call_id = len(state.get("agent_call_log", [])) + 1
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
        
        if "agent_call_log" not in state:
            state["agent_call_log"] = []
        state["agent_call_log"].append(call_log)
        
        logger.info(f"Agent Call #{call_id}: {agent_name} ({call_type}) - Revision: {state.get('revision_count', 0)}")
        return state
    
    def _build_langgraph_workflow(self):
        """Build the LangGraph StateGraph workflow for visualization"""
        
        # Create the StateGraph
        workflow = StateGraph(ArticleState)
        
        # Add nodes (agents)
        workflow.add_node("research", self.research_agent)
        workflow.add_node("draft", self.draft_agent)
        workflow.add_node("critique", self.critique_agent)
        workflow.add_node("moderator", self.moderator_agent)
        workflow.add_node("additional_research", self._additional_research_node)
        workflow.add_node("image", self.image_agent)
        workflow.add_node("post", self.post_agent)
        workflow.add_node("seo", self.seo_agent)
        workflow.add_node("final_assembly", self._final_assembly_node)
        
        # Set entry point
        workflow.set_entry_point("research")
        
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
        
        return workflow.compile()
    
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
        try:
            from pyvis.network import Network
            
            # Build the LangGraph workflow
            app = self._build_langgraph_workflow()
            
            # Get the graph from LangGraph
            G = app.get_graph()
            
            # Convert LangGraph graph to NetworkX
            import networkx as nx
            nx_graph = nx.DiGraph()
            
            # Add nodes
            if hasattr(G, 'nodes') and callable(G.nodes):
                for node in G.nodes():
                    nx_graph.add_node(node)
            elif hasattr(G, 'nodes') and isinstance(G.nodes, dict):
                for node in G.nodes.keys():
                    nx_graph.add_node(node)
            
            # Add edges
            if hasattr(G, 'edges') and callable(G.edges):
                for edge in G.edges():
                    nx_graph.add_edge(edge[0], edge[1])
            elif hasattr(G, 'edges') and isinstance(G.edges, (list, tuple)):
                for edge in G.edges:
                    nx_graph.add_edge(edge[0], edge[1])
            
            G = nx_graph
            
            # Create Pyvis network
            nt = Network(height="800px", width="100%", directed=True, bgcolor="#222222", font_color="white")
            
            for node in G.nodes():
                call_count = 0
                node_type = "agent"
                
                if node == "research":
                    node_type = "initial"
                elif node == "additional_research":
                    node_type = "conditional"
                elif node in ["critique", "moderator"]:
                    node_type = "revision"
                elif node in ["image", "post", "seo", "final_assembly"]:
                    node_type = "final"
                nt.add_node(
                    node,
                    label=f"{node}\n({node_type})",
                    title=f"Node: {node}\nType: {node_type}\nExpected calls: Variable",
                    color="#4CAF50" if node_type == "initial" else 
                          "#FF9800" if node_type == "conditional" else
                          "#2196F3" if node_type == "revision" else
                          "#9C27B0" if node_type == "final" else "#607D8B",
                    size=30 if node_type == "initial" else 25
                )
            
            for edge in G.edges():
                source, target = edge
                edge_label = ""
                
                if source == "critique":
                    if target == "moderator":
                        edge_label = "revise"
                    elif target == "additional_research":
                        edge_label = "needs research"
                    elif target == "image":
                        edge_label = "pass"
                
                nt.add_edge(source, target, label=edge_label, color="#4CAF50", width=2)
            
            # Customize the appearance
            nt.set_options("""
            {
                "nodes": {
                    "font": {"size": 12, "color": "white"},
                    "borderWidth": 2,
                    "borderColor": "#4CAF50",
                    "shape": "box"
                },
                "edges": {
                    "color": {"color": "#4CAF50", "highlight": "#FF6B6B"},
                    "width": 2,
                    "arrows": {"to": {"enabled": true, "scaleFactor": 1.2}},
                    "font": {"size": 10, "color": "white"}
                },
                "physics": {
                    "enabled": true,
                    "stabilization": {"iterations": 100},
                    "hierarchicalRepulsion": {
                        "centralGravity": 0.0,
                        "springLength": 200,
                        "springConstant": 0.01,
                        "nodeDistance": 120,
                        "damping": 0.09
                    }
                },
                "layout": {
                    "improvedLayout": true,
                    "hierarchical": {
                        "enabled": true,
                        "direction": "UD",
                        "sortMethod": "directed"
                    }
                }
            }
            """)
            
            nt.save_graph(output_file)
            logger.info(f"Visual graph saved to: {output_file}")
            return output_file
            
        except ImportError:
            logger.error("Pyvis not installed. Install with: pip install pyvis")
            return None
        except Exception as e:
            logger.error(f"Failed to generate visual graph: {e}")
            print(f"Error generating visual graph: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_execution_graph(self, execution_data: Dict[str, Any], output_file: str = "execution_graph.html"):
        """Generate a visual graph with actual execution data and call counts"""
        try:
            from pyvis.network import Network
            
            # Build the LangGraph workflow
            app = self._build_langgraph_workflow()
            G = app.get_graph()
            
            # Convert to NetworkX
            import networkx as nx
            nx_graph = nx.DiGraph()
            
            if hasattr(G, 'nodes') and callable(G.nodes):
                for node in G.nodes():
                    nx_graph.add_node(node)
            elif hasattr(G, 'nodes') and isinstance(G.nodes, dict):
                for node in G.nodes.keys():
                    nx_graph.add_node(node)
            
            if hasattr(G, 'edges') and callable(G.edges):
                for edge in G.edges():
                    nx_graph.add_edge(edge[0], edge[1])
            elif hasattr(G, 'edges') and isinstance(G.edges, (list, tuple)):
                for edge in G.edges:
                    nx_graph.add_edge(edge[0], edge[1])
            
            G = nx_graph
            
            # Create Pyvis network with execution data
            nt = Network(height="900px", width="100%", directed=True, bgcolor="#1a1a1a", font_color="white")
            
            agent_call_log = execution_data.get('agent_call_log', [])
            research_calls = execution_data.get('research_calls', 0)
            additional_research_calls = execution_data.get('additional_research_calls', 0)
            revisions_made = execution_data.get('revisions_made', 0)
            node_call_counts = {}
            for call in agent_call_log:
                agent_name = call['agent_name'].replace('Agent', '').lower()
                if agent_name == 'research':
                    if 'additional' in call['call_type']:
                        node_call_counts['additional_research'] = node_call_counts.get('additional_research', 0) + 1
                    else:
                        node_call_counts['research'] = node_call_counts.get('research', 0) + 1
                elif agent_name == 'draft':
                    node_call_counts['draft'] = node_call_counts.get('draft', 0) + 1
                elif agent_name == 'critique':
                    node_call_counts['critique'] = node_call_counts.get('critique', 0) + 1
                elif agent_name == 'moderator':
                    node_call_counts['moderator'] = node_call_counts.get('moderator', 0) + 1
                elif agent_name == 'image':
                    node_call_counts['image'] = node_call_counts.get('image', 0) + 1
                elif agent_name == 'post':
                    node_call_counts['post'] = node_call_counts.get('post', 0) + 1
                elif agent_name == 'seo':
                    node_call_counts['seo'] = node_call_counts.get('seo', 0) + 1
            
            for node in G.nodes():
                call_count = node_call_counts.get(node, 0)
                node_type = "agent"
                
                if node == "research":
                    node_type = "initial"
                    color = "#4CAF50"
                elif node == "additional_research":
                    node_type = "conditional"
                    color = "#FF9800"
                elif node in ["critique", "moderator"]:
                    node_type = "revision"
                    color = "#2196F3"
                elif node in ["image", "post", "seo", "final_assembly"]:
                    node_type = "final"
                    color = "#9C27B0"
                else:
                    color = "#607D8B"
                
                label = f"{node}\n({node_type})\nCalls: {call_count}"
                tooltip = f"""Node: {node}
Type: {node_type}
Actual Calls: {call_count}
Total Agent Calls: {len(agent_call_log)}
Research Calls: {research_calls}
Additional Research: {additional_research_calls}
Revisions Made: {revisions_made}"""
                
                nt.add_node(
                    node,
                    label=label,
                    title=tooltip,
                    color=color,
                    size=30 + (call_count * 5),
                    font={"size": 12, "color": "white"}
                )
            
            for edge in G.edges():
                source, target = edge
                edge_label = ""
                edge_color = "#4CAF50"
                if source == "critique":
                    if target == "moderator":
                        edge_label = f"revise ({revisions_made} times)"
                        edge_color = "#FF9800"
                    elif target == "additional_research":
                        edge_label = f"needs research ({additional_research_calls} times)"
                        edge_color = "#FF5722"
                    elif target == "image":
                        edge_label = "pass"
                        edge_color = "#4CAF50"
                
                nt.add_edge(
                    source, 
                    target, 
                    label=edge_label, 
                    color=edge_color, 
                    width=2 + (call_count * 0.5),
                    font={"size": 10, "color": "white"}
                )
            
            stats_html = f"""
            <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; font-family: monospace;">
                <h4>Execution Statistics</h4>
                <p>Total Agent Calls: {len(agent_call_log)}</p>
                <p>Research Calls: {research_calls}</p>
                <p>Additional Research: {additional_research_calls}</p>
                <p>Revisions Made: {revisions_made}</p>
                <p>Article Length: {len(execution_data.get('article', ''))} chars</p>
            </div>
            """
            nt.set_options("""
            {
                "nodes": {
                    "font": {"size": 12, "color": "white"},
                    "borderWidth": 2,
                    "borderColor": "#4CAF50",
                    "shape": "box"
                },
                "edges": {
                    "color": {"color": "#4CAF50", "highlight": "#FF6B6B"},
                    "width": 2,
                    "arrows": {"to": {"enabled": true, "scaleFactor": 1.2}},
                    "font": {"size": 10, "color": "white"}
                },
                "physics": {
                    "enabled": true,
                    "stabilization": {"iterations": 100},
                    "hierarchicalRepulsion": {
                        "centralGravity": 0.0,
                        "springLength": 200,
                        "springConstant": 0.01,
                        "nodeDistance": 120,
                        "damping": 0.09
                    }
                },
                "layout": {
                    "improvedLayout": true,
                    "hierarchical": {
                        "enabled": true,
                        "direction": "UD",
                        "sortMethod": "directed"
                    }
                }
            }
            """)
            
            nt.save_graph(output_file)
            logger.info(f"Execution graph with call counts saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate execution graph: {e}")
            print(f"Error generating execution graph: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
        
        # Initialize state
        initial_state = {
            "topic": topic,
            "research_data": "",
            "article": "",
            "critique_feedback": [],
            "critique_passed": False,
            "revision_count": 0,
            "max_revisions": workflow_config["max_revisions"],
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
        
        # Build and run the LangGraph workflow
        app = self._build_langgraph_workflow()
        
        print("Running LangGraph workflow...")
        print("You can visualize this workflow in real-time!")
        
        # Run the workflow
        final_state = app.invoke(initial_state)
        
        print("LangGraph workflow completed!")
        
        # Export files if requested
        if export_files:
            print("Exporting files...")
            try:
                export_paths = create_article_package(final_state["final_output"], output_dir)
                final_state["final_output"]['export_paths'] = export_paths
                print(f"Files exported to: {output_dir}")
            except Exception as e:
                logger.error(f"Export failed: {e}")
                final_state["final_output"]['export_paths'] = None
        
        return final_state["final_output"]
    
    def _should_continue_revision(self, state: ArticleState) -> str:
        """Decide whether to revise, do additional research, or proceed to generation"""
        
        # Log decision context
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
            # Enhanced research need detection using new state information
            feedback = state.get('critique_feedback', [])
            research_calls = state.get('research_calls', 0)
            additional_research_calls = state.get('additional_research_calls', 0)
            research_data_length = len(state.get('research_data', ''))
            
            logger.info(f"Evaluating research needs - Feedback: {len(feedback)} issues, Research data: {research_data_length} chars")
            
            # Check for research-related keywords in feedback
            needs_more_research = any(keyword in str(feedback).lower() for keyword in [
                'insufficient research', 'lack of data', 'missing sources', 'outdated information',
                'need more research', 'incomplete research', 'limited sources', 'more data needed',
                'insufficient data', 'lack of sources', 'missing research', 'incomplete data',
                'limited research', 'need more data', 'insufficient sources', 'more research needed',
                'recent developments', 'current trends', 'latest information', 'up-to-date sources',
                'research integration', 'utilize research', 'use research data', 'incorporate research'
            ])
            
            # Additional heuristics for research needs
            research_data_insufficient = research_data_length < 2000  # Less than 2000 chars of research
            no_additional_research_yet = additional_research_calls == 0
            multiple_research_attempts = research_calls + additional_research_calls >= 2
            
            # Decision logic with enhanced context
            if needs_more_research and (no_additional_research_yet or research_data_insufficient):
                logger.info("Additional research needed based on critique feedback")
                return "additional_research"
            elif needs_more_research and multiple_research_attempts:
                logger.info("Research already attempted multiple times - proceeding with revision")
                return "revise"
            else:
                logger.info("Proceeding with revision based on feedback")
                return "revise"
    
    def _final_assembly(self, state: ArticleState) -> ArticleState:
        """Assemble all components into final output"""
        
        state["final_output"] = {
            "article": state["article"],
            "image_prompt": state["image_prompt"],
            "image_url": state["image_url"],
            "linkedin_post": state["linkedin_post"],
            "hashtags": state["hashtags"],
            "seo_keywords": state["seo_keywords"],
            "revisions_made": state["revision_count"],
            "topic": state["topic"]
        }
        
        return state
    
    def _build_workflow(self):
        """Build the LangGraph workflow with parallel execution"""
        
        workflow = StateGraph(ArticleState)
        
        # Add sequential nodes
        workflow.add_node("research", self.research_agent)
        workflow.add_node("draft", self.draft_agent)
        workflow.add_node("critique", self.critique_agent)
        workflow.add_node("moderate", self.moderator_agent)
        
        # Add parallel nodes (these will run simultaneously)
        workflow.add_node("image_gen", self.image_agent)
        workflow.add_node("post_gen", self.post_agent)
        workflow.add_node("seo_gen", self.seo_agent)
        
        # Add final assembly
        workflow.add_node("assemble", self._final_assembly)
        
        # Sequential edges
        workflow.add_edge("research", "draft")
        workflow.add_edge("draft", "critique")
        
        # Conditional edge after critique
        workflow.add_conditional_edges(
            "critique",
            self._should_continue_revision,
            {
                "revise": "moderate",
                "generate": "image_gen"  # Entry point to parallel section
            }
        )
        
        # Loop back from moderate to critique
        workflow.add_edge("moderate", "critique")
        
        # Parallel edges - all three run simultaneously after critique passes
        # Use a different approach to avoid concurrent update issues
        workflow.add_edge("image_gen", "assemble")
        workflow.add_edge("post_gen", "assemble") 
        workflow.add_edge("seo_gen", "assemble")
        
        # End
        workflow.add_edge("assemble", END)
        
        # Set entry point
        workflow.set_entry_point("research")
        
        return workflow.compile()
    
    def generate_article(self, topic: str, export_files: bool = None, output_dir: str = None) -> Dict[str, Any]:
        """Generate a complete LinkedIn article with all components"""
        
        # Use configuration defaults if not specified
        if export_files is None:
            export_config = self.config.get_export_config()
            export_files = export_config["export_word_documents"] or export_config["export_jpeg_images"]
        
        if output_dir is None:
            export_config = self.config.get_export_config()
            output_dir = export_config["default_output_dir"]
        
        # Get workflow configuration
        workflow_config = self.config.get_workflow_config()
        
        print("Starting LinkedIn Article Generation Workflow...")
        print(f"Topic: {topic}\n")
        
        # Initialize state
        state = {
            "topic": topic,
            "research_data": "",
            "article": "",
            "critique_feedback": [],
            "critique_passed": False,
            "revision_count": 0,
            "max_revisions": workflow_config["max_revisions"],
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
        
        print("Step 1: Researching topic...")
        logger.info("Starting research phase")
        state = self._log_agent_call(state, "ResearchAgent", "initial")
        state = self.research_agent(state)
        logger.info(f"Research completed - Data length: {len(state.get('research_data', ''))} chars")
        print("Research completed")
        
        print("Step 2: Creating initial draft...")
        logger.info("Starting draft phase")
        state = self._log_agent_call(state, "DraftAgent", "initial")
        state = self.draft_agent(state)
        logger.info(f"Draft completed - Article length: {len(state.get('article', ''))} chars")
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
                print("Article passed critique")
                break
            elif revision < max_revisions:
                feedback = state.get('critique_feedback', [])
                logger.info(f"Revising based on feedback: {feedback}")
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
                        logger.info(f"Additional research added - Total research length: {len(state['research_data'])} chars")
                        logger.info(f"Total additional research calls: {state['additional_research_calls']}")
                
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
        final_output = {
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
        
        if export_files:
            print("Step 6: Exporting files...")
            logger.info(f"Starting export to directory: {output_dir}")
            
            logger.info(f"Final output keys: {list(final_output.keys())}")
            logger.info(f"Article length: {len(final_output.get('article', ''))}")
            logger.info(f"LinkedIn post: {final_output.get('linkedin_post', 'MISSING')}")
            logger.info(f"Hashtags: {final_output.get('hashtags', 'MISSING')}")
            logger.info(f"SEO keywords: {final_output.get('seo_keywords', 'MISSING')}")
            
            try:
                export_paths = create_article_package(final_output, output_dir)
                final_output['export_paths'] = export_paths
                logger.info(f"Export successful: {export_paths}")
                print(f"Files exported to: {output_dir}")
                print(f"   Word document: {export_paths['word_document']}")
                print(f"   JPEG image: {export_paths['image_file']}")
            except Exception as e:
                logger.error(f"Export failed: {e}")
                print(f"Export failed: {e}")
                import traceback
                logger.error(f"Export error traceback: {traceback.format_exc()}")
                final_output['export_paths'] = None
        else:
            logger.info("Export files disabled")
        
        print("\nArticle generation completed!")
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


if __name__ == "__main__":
    # Example usage
    workflow = LinkedInArticleWorkflow()
    
    # Generate article
    result = workflow.generate_article(
        "The Rise of AI Agents in Software Development: Beyond Copilot"
    )
    
    # Display results
    workflow.display_results(result)
