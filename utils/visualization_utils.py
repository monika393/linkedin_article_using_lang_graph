"""
Visualization utilities for workflow graphs using Pyvis and NetworkX
"""

import logging
from typing import Dict, Any, Optional
import networkx as nx

logger = logging.getLogger(__name__)


class WorkflowVisualizer:
    """Handles visualization of workflow graphs using Pyvis"""
    
    def __init__(self):
        self.pyvis_available = self._check_pyvis_availability()
    
    def _check_pyvis_availability(self) -> bool:
        """Check if Pyvis is available"""
        try:
            from pyvis.network import Network
            return True
        except ImportError:
            logger.warning("Pyvis not installed. Install with: pip install pyvis")
            return False
    
    def _convert_langgraph_to_networkx(self, langgraph_app):
        """Convert LangGraph graph to NetworkX DiGraph"""
        G = langgraph_app.get_graph()
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
        
        return nx_graph
    
    def _get_node_style(self, node: str, node_type: str = "agent") -> Dict[str, Any]:
        """Get styling information for a node"""
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
        
        return {
            "node_type": node_type,
            "color": color,
            "size": 30 if node_type == "initial" else 25
        }
    
    def _get_edge_style(self, source: str, target: str, execution_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get styling information for an edge"""
        edge_label = ""
        edge_color = "#4CAF50"
        
        if source == "critique":
            if target == "moderator":
                edge_label = "revise"
                edge_color = "#FF9800"
                if execution_data:
                    revisions_made = execution_data.get('revisions_made', 0)
                    edge_label = f"revise ({revisions_made} times)"
            elif target == "additional_research":
                edge_label = "needs research"
                edge_color = "#FF5722"
                if execution_data:
                    additional_research_calls = execution_data.get('additional_research_calls', 0)
                    edge_label = f"needs research ({additional_research_calls} times)"
            elif target == "image":
                edge_label = "pass"
                edge_color = "#4CAF50"
        
        return {
            "label": edge_label,
            "color": edge_color,
            "width": 2
        }
    
    def _get_pyvis_options(self) -> str:
        """Get Pyvis network options as JSON string"""
        return """
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
        """
    
    def generate_workflow_graph(self, langgraph_app, output_file: str = "workflow_graph.html") -> Optional[str]:
        """Generate a visual graph of the workflow using Pyvis"""
        if not self.pyvis_available:
            return None
        
        try:
            from pyvis.network import Network
            
            nx_graph = self._convert_langgraph_to_networkx(langgraph_app)
            
            nt = Network(height="800px", width="100%", directed=True, bgcolor="#222222", font_color="white")
            
            for node in nx_graph.nodes():
                style = self._get_node_style(node)
                nt.add_node(
                    node,
                    label=f"{node}\n({style['node_type']})",
                    title=f"Node: {node}\nType: {style['node_type']}\nExpected calls: Variable",
                    color=style['color'],
                    size=style['size']
                )
            
            for edge in nx_graph.edges():
                source, target = edge
                edge_style = self._get_edge_style(source, target)
                nt.add_edge(source, target, label=edge_style['label'], color=edge_style['color'], width=edge_style['width'])
            
            nt.set_options(self._get_pyvis_options())
            nt.save_graph(output_file)
            logger.info(f"Visual graph saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate visual graph: {e}")
            return None
    
    def generate_execution_graph(self, langgraph_app, execution_data: Dict[str, Any], output_file: str = "execution_graph.html") -> Optional[str]:
        """Generate a visual graph with actual execution data and call counts"""
        if not self.pyvis_available:
            return None
        
        try:
            from pyvis.network import Network
            
            nx_graph = self._convert_langgraph_to_networkx(langgraph_app)
            
            nt = Network(height="900px", width="100%", directed=True, bgcolor="#1a1a1a", font_color="white")
            
            agent_call_log = execution_data.get('agent_call_log', [])
            research_calls = execution_data.get('research_calls', 0)
            additional_research_calls = execution_data.get('additional_research_calls', 0)
            revisions_made = execution_data.get('revisions_made', 0)
            node_call_counts = self._calculate_node_call_counts(agent_call_log)
            
            for node in nx_graph.nodes():
                call_count = node_call_counts.get(node, 0)
                style = self._get_node_style(node)
                
                label = f"{node}\n({style['node_type']})\nCalls: {call_count}"
                tooltip = f"""Node: {node}
Type: {style['node_type']}
Actual Calls: {call_count}
Total Agent Calls: {len(agent_call_log)}
Research Calls: {research_calls}
Additional Research: {additional_research_calls}
Revisions Made: {revisions_made}"""
                
                nt.add_node(
                    node,
                    label=label,
                    title=tooltip,
                    color=style['color'],
                    size=30 + (call_count * 5),
                    font={"size": 12, "color": "white"}
                )
            
            for edge in nx_graph.edges():
                source, target = edge
                edge_style = self._get_edge_style(source, target, execution_data)
                
                nt.add_edge(
                    source, 
                    target, 
                    label=edge_style['label'], 
                    color=edge_style['color'], 
                    width=2 + (call_count * 0.5),
                    font={"size": 10, "color": "white"}
                )
            
            nt.set_options(self._get_pyvis_options())
            nt.save_graph(output_file)
            logger.info(f"Execution graph with call counts saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate execution graph: {e}")
            return None
    
    def _calculate_node_call_counts(self, agent_call_log: list) -> Dict[str, int]:
        """Calculate call counts for each node based on agent call log"""
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
        
        return node_call_counts
    
    def generate_langgraph_png(self, langgraph_app, filename: str = "langgraph_workflow.png") -> Optional[str]:
        """Generate PNG visualization using LangGraph's built-in methods"""
        try:
            graph = langgraph_app.get_graph()
            
            print("\nGenerating graph visualization...")
            
            # Try mermaid PNG first (doesn't require system dependencies)
            if hasattr(graph, 'draw_mermaid_png'):
                try:
                    mermaid_result = graph.draw_mermaid_png()
                    with open(filename, "wb") as f:
                        f.write(mermaid_result)
                    print("Graph visualization saved as: langgraph_workflow.png")
                    return filename
                except Exception as mermaid_error:
                    print(f"Mermaid PNG generation failed: {mermaid_error}")
                    print("Trying standard PNG...")
                    if hasattr(graph, 'draw_png'):
                        try:
                            graph.draw_png(filename)
                            print("Graph visualization saved as: langgraph_workflow.png")
                            return filename
                        except Exception as png_error:
                            print(f"PNG generation failed: {png_error}")
                            print("Trying ASCII representation...")
                            if hasattr(graph, 'draw_ascii'):
                                print(graph.draw_ascii())
                            return None
                    else:
                        print("No PNG generation methods available")
                        return None
            elif hasattr(graph, 'draw_png'):
                try:
                    graph.draw_png(filename)
                    print("Graph visualization saved as: langgraph_workflow.png")
                    return filename
                except Exception as png_error:
                    print(f"PNG generation failed: {png_error}")
                    print("Trying ASCII representation...")
                    if hasattr(graph, 'draw_ascii'):
                        print(graph.draw_ascii())
                    return None
            else:
                print("Graph visualization not available")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate LangGraph PNG visualization: {e}")
            print(f"Visualization generation failed: {e}")
            return None
