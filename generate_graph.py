#!/usr/bin/env python3
"""
Generate visual workflow graph using LangGraph and Pyvis
"""

from workflow import LinkedInArticleWorkflow
from utils import validate_config

def main():
    print("LinkedIn Article Generator - Workflow Visualization")
    print("=" * 60)
    
    if not validate_config():
        print("ERROR: Configuration is invalid!")
        print("Please check your .env file and set OPENAI_API_KEY")
        return
    
    try:
        # Initialize workflow
        workflow = LinkedInArticleWorkflow()
        
        # Generate visual graph
        print("Generating workflow visualization...")
        graph_file = workflow.generate_visual_graph("workflow_graph.html")
        
        if graph_file:
            print(f"Workflow graph saved to: {graph_file}")
            print("\nOpen this file in your browser to see the interactive workflow visualization!")
            print("\nThe graph shows:")
            print("   - All workflow nodes (agents)")
            print("   - Edges (connections between agents)")
            print("   - Conditional paths (critique decisions)")
            print("   - Parallel execution paths")
            print("   - Interactive navigation")
        else:
            print("Failed to generate visual graph")
        
        # Generate sample execution graph with mock data
        print("\nGenerating sample execution graph with call counts...")
        sample_execution_data = {
            'agent_call_log': [
                {'agent_name': 'ResearchAgent', 'call_type': 'initial', 'revision_count': 0},
                {'agent_name': 'DraftAgent', 'call_type': 'initial', 'revision_count': 0},
                {'agent_name': 'CritiqueAgent', 'call_type': 'revision_1', 'revision_count': 1},
                {'agent_name': 'ModeratorAgent', 'call_type': 'revision_1', 'revision_count': 1},
                {'agent_name': 'ResearchAgent', 'call_type': 'additional_1', 'revision_count': 1},
                {'agent_name': 'CritiqueAgent', 'call_type': 'revision_2', 'revision_count': 2},
                {'agent_name': 'ImageAgent', 'call_type': 'final', 'revision_count': 2},
                {'agent_name': 'PostAgent', 'call_type': 'final', 'revision_count': 2},
                {'agent_name': 'SEOAgent', 'call_type': 'final', 'revision_count': 2},
            ],
            'research_calls': 1,
            'additional_research_calls': 1,
            'revisions_made': 2,
            'article': 'Sample article content for demonstration purposes...'
        }
        
        execution_graph_file = workflow.generate_execution_graph(sample_execution_data, "sample_execution_graph.html")
        if execution_graph_file:
            print(f"Sample execution graph saved to: {execution_graph_file}")
            print("\nThis graph shows:")
            print("   - Actual node call counts")
            print("   - Execution statistics")
            print("   - Node sizes based on call frequency")
            print("   - Edge labels with execution counts")
            print("   - Real-time execution data")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
