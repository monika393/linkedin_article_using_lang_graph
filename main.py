"""
Main entry point for LinkedIn Article Generation System
Single, clean entry point for all functionality
"""

import logging
import sys
from workflow import LinkedInArticleWorkflow
from utils import print_config_status, validate_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('linkedin_article_generator.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the LinkedIn Article Generation System"""
    
    logger.info("Starting LinkedIn Article Generation System")
    print("LinkedIn Article Generation System")
    print("=" * 50)
    
    print_config_status()
    logger.info("Configuration status displayed")
    
    if not validate_config():
        logger.error("Configuration is invalid - missing OPENAI_API_KEY")
        print("\nERROR: Configuration is invalid!")
        print("Please check your .env file and set OPENAI_API_KEY")
        print("You can edit the .env file with your actual API key")
        return
    
    logger.info("Configuration validated successfully")
    
    try:
        logger.info("Initializing LinkedInArticleWorkflow...")
        workflow = LinkedInArticleWorkflow()
        logger.info("Workflow initialized successfully")
        print("Workflow initialized successfully!")
    except Exception as e:
        logger.error(f"Workflow initialization failed: {e}")
        print(f"Error initializing workflow: {e}")
        return
    
    topic = "Optimizations in LLM for Saving Carbon Consumption: Green AI Strategies for Sustainable Development"
    
    logger.info(f"Starting article generation for topic: {topic}")
    print(f"\nGenerating article for: {topic}")
    print("Features:")
    print("- Storytelling format with technical accuracy")
    print("- Recent research (2023-2025) with academic sources")
    print("- Academic citations and references")
    print("- Word document and JPEG image export")
    
    try:
        logger.info("Calling workflow.generate_article with export_files=True")
        from utils import get_config
        config = get_config()
        output_dir = config.default_output_dir
        
        logger.info(f"Using output directory: {output_dir}")
        
        print("Generating workflow visualization...")
        graph_file = workflow.generate_visual_graph("workflow_graph.html")
        if graph_file:
            print(f"Workflow graph saved to: {graph_file}")
            print("Open this file in your browser to see the interactive workflow visualization!")
        
        print("Generating PNG workflow visualization...")
        png_file = workflow.generate_graph_visualization("workflow_graph.png")
        if png_file:
            print(f"PNG workflow graph saved to: {png_file}")
            print("This is a static PNG image of the workflow structure!")
        
        use_langgraph = True
        
        if use_langgraph:
            print("\nUsing LangGraph StateGraph workflow for real-time visualization...")
            result = workflow.generate_article_with_langgraph(
                topic=topic,
                export_files=True,
                output_dir=output_dir
            )
        else:
            print("\nUsing sequential workflow...")
            result = workflow.generate_article(
                topic=topic,
                export_files=True,
                output_dir=output_dir
            )
        
        logger.info("Article generation completed successfully")
        
        # Debug: Check result type and structure
        logger.info(f"Result type: {type(result)}")
        if isinstance(result, dict):
            logger.info(f"Result keys: {list(result.keys())}")
        else:
            logger.error(f"Result is not a dictionary: {result}")
            print(f"ERROR: Expected dictionary but got {type(result)}")
            return
        
        print("\nGenerating execution graph with call counts...")
        execution_graph_file = workflow.generate_execution_graph(result, "execution_graph.html")
        if execution_graph_file:
            print(f"Execution graph saved to: {execution_graph_file}")
            print("This graph shows actual node call counts and execution statistics!")
        
        workflow.display_results(result)
        
        print("\n" + "="*80)
        print("DEBUG INFORMATION")
        print("="*80)
        
        if isinstance(result, dict) and 'research_data' in result:
            print(f"\nResearch Data Length: {len(result.get('research_data', ''))} characters")
            print("Research Preview (first 500 chars):")
            print("-" * 50)
            print(result.get('research_data', '')[:500] + "...")
            print("-" * 50)
        
        if isinstance(result, dict) and 'critique_feedback' in result:
            feedback = result.get('critique_feedback', [])
            if feedback:
                print(f"\nCritique Feedback ({len(feedback)} issues):")
                for i, issue in enumerate(feedback, 1):
                    print(f"   {i}. {issue}")
            else:
                print("\nNo critique issues found")
        
        revisions = result.get('revisions_made', 0) if isinstance(result, dict) else 0
        print(f"\nRevisions Made: {revisions}")
        
        # Show agent call hierarchy
        if isinstance(result, dict) and 'agent_call_log' in result:
            agent_calls = result.get('agent_call_log', [])
            print(f"\nAgent Call Hierarchy ({len(agent_calls)} total calls):")
            print("-" * 60)
            for i, call in enumerate(agent_calls, 1):
                print(f"{i:2d}. {call['agent_name']} ({call['call_type']}) - Revision: {call['revision_count']}")
            print("-" * 60)
            
            # Show research call summary
            research_calls = result.get('research_calls', 0)
            additional_research_calls = result.get('additional_research_calls', 0)
            print(f"\nResearch Call Summary:")
            print(f"   Initial research calls: {research_calls}")
            print(f"   Additional research calls: {additional_research_calls}")
            print(f"   Total research calls: {research_calls + additional_research_calls}")
            
            if additional_research_calls > 0:
                print(f"   Additional research was conducted based on critique feedback")
                print(f"   Moderator agent used both original and additional research for revisions")
            else:
                print(f"   No additional research was needed - critique passed on first attempt")
        
        article = result.get('article', '') if isinstance(result, dict) else ''
        word_count = len(article.split()) if article else 0
        char_count = len(article) if article else 0
        
        print(f"\nArticle Quality Metrics:")
        print(f"   Word count: {word_count}")
        print(f"   Character count: {char_count}")
        print(f"   Target: 2000-3000 words")
        
        if word_count >= 2000:
            print("   Length: Excellent (2000+ words)")
        elif word_count >= 1500:
            print("   Length: Good (1500+ words)")
        elif word_count >= 1000:
            print("   Length: Acceptable (1000+ words)")
        else:
            print("   Length: Too short (less than 1000 words)")
        
        storytelling_indicators = [
            "I", "we", "our team", "Sarah", "John", "the company", 
            "struggled", "discovered", "realized", "implemented",
            "But then", "However", "Suddenly", "The breakthrough"
        ]
        
        found_indicators = [indicator for indicator in storytelling_indicators 
                          if indicator.lower() in article.lower()]
        
        print(f"   Storytelling elements: {len(found_indicators)} found")
        if found_indicators:
            print(f"   Indicators: {', '.join(found_indicators[:5])}")
        
        technical_indicators = [
            "algorithm", "model", "training", "inference", "optimization",
            "carbon", "energy", "efficiency", "metrics", "benchmark",
            "implementation", "architecture", "performance"
        ]
        
        found_technical = [indicator for indicator in technical_indicators 
                          if indicator.lower() in article.lower()]
        
        print(f"   Technical elements: {len(found_technical)} found")
        if found_technical:
            print(f"   Technical terms: {', '.join(found_technical[:5])}")
        
        citation_count = article.count('(') + article.count('[')
        print(f"   Citations found: {citation_count}")
        
        if article and "References" in article:
            ref_section = article.split("References")[1]
            print(f"\nReferences Section Length: {len(ref_section)} characters")
            print("References Preview:")
            print("-" * 40)
            print(ref_section[:300] + "...")
            print("-" * 40)
        else:
            print("\nNo References section found")
        
        if isinstance(result, dict) and 'image_prompt' in result:
            print(f"\nImage Prompt Length: {len(result.get('image_prompt', ''))} characters")
            print("Image Prompt Preview:")
            print("-" * 40)
            print(result.get('image_prompt', '')[:200] + "...")
            print("-" * 40)
        
        if isinstance(result, dict) and 'linkedin_post' in result:
            print(f"\nLinkedIn Post:")
            print(f"   Length: {len(result.get('linkedin_post', ''))} characters")
            print(f"   Content: {result.get('linkedin_post', '')}")
        
        if isinstance(result, dict) and 'hashtags' in result:
            hashtags = result.get('hashtags', [])
            print(f"\nHashtags ({len(hashtags)}): {', '.join(hashtags)}")
        
        if isinstance(result, dict) and 'seo_keywords' in result:
            keywords = result.get('seo_keywords', [])
            print(f"SEO Keywords ({len(keywords)}): {', '.join(keywords[:5])}...")
        
        print("\n" + "="*80)
        
        if isinstance(result, dict) and result.get('export_paths'):
            logger.info(f"Export completed successfully: {result['export_paths']}")
            print(f"\nExport completed successfully!")
            print(f"Word document: {result['export_paths']['word_document']}")
            print(f"JPEG image: {result['export_paths']['image_file']}")
        else:
            logger.warning("No export paths found in result")
            print("\nNo export paths found in result")
        
        if article:
            print(f"\nArticle Preview (first 500 characters):")
            print("-" * 50)
            print(article[:500] + "...")
            print("-" * 50)
        
        logger.info(f"Generation completed - Article length: {len(article)} chars, Revisions: {revisions}")
        print(f"\nGeneration completed successfully!")
        print(f"Article length: {len(article)} characters")
        print(f"Revisions made: {revisions}")
        
        # Show comprehensive agent call hierarchy
        if isinstance(result, dict) and 'agent_call_log' in result:
            print("\n" + "="*80)
            print("COMPLETE AGENT CALL HIERARCHY - END TO END")
            print("="*80)
            
            agent_calls = result.get('agent_call_log', [])
            print(f"Total Agent Calls: {len(agent_calls)}")
            print("-" * 80)
            
            # Group calls by phase
            initial_calls = [call for call in agent_calls if call['call_type'] == 'initial']
            revision_calls = [call for call in agent_calls if call['call_type'].startswith('revision_')]
            additional_research_calls = [call for call in agent_calls if call['call_type'].startswith('additional_')]
            final_calls = [call for call in agent_calls if call['call_type'] == 'final']
            
            print(f"\nPHASE 1: INITIAL GENERATION ({len(initial_calls)} calls)")
            print("-" * 40)
            for call in initial_calls:
                print(f"  {call['call_id']:2d}. {call['agent_name']} - {call['call_type']}")
            
            if additional_research_calls:
                print(f"\nPHASE 2: ADDITIONAL RESEARCH ({len(additional_research_calls)} calls)")
                print("-" * 40)
                for call in additional_research_calls:
                    print(f"  {call['call_id']:2d}. {call['agent_name']} - {call['call_type']}")
            
            if revision_calls:
                print(f"\nPHASE 3: REVISION CYCLE ({len(revision_calls)} calls)")
                print("-" * 40)
                for call in revision_calls:
                    print(f"  {call['call_id']:2d}. {call['agent_name']} - {call['call_type']}")
            
            if final_calls:
                print(f"\nPHASE 4: FINAL CONTENT GENERATION ({len(final_calls)} calls)")
                print("-" * 40)
                for call in final_calls:
                    print(f"  {call['call_id']:2d}. {call['agent_name']} - {call['call_type']}")
            
            print("\n" + "="*80)
            print("DETAILED CALL SEQUENCE")
            print("="*80)
            for i, call in enumerate(agent_calls, 1):
                print(f"{i:2d}. {call['agent_name']:15s} | {call['call_type']:15s} | Revision: {call['revision_count']:2d} | Research: {call['research_calls']:2d} | Additional: {call['additional_research_calls']:2d}")
            
            print("="*80)
        
    except Exception as e:
        logger.error(f"Article generation failed: {e}")
        print(f"Error: {e}")
        print("This might be due to:")
        print("1. Missing OpenAI API key")
        print("2. Network connectivity issues")
        print("3. API rate limits")
        print("4. Missing dependencies")


if __name__ == "__main__":
    main()
