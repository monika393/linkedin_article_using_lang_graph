"""
Basic usage example for LinkedIn Article Generation System
"""

import os
from workflow import LinkedInArticleWorkflow


def main():
    """Example of generating a LinkedIn article"""
    
    # Set up OpenAI API key (you'll need to set this in your environment)
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    # Initialize the workflow
    workflow = LinkedInArticleWorkflow()
    
    # Example topics
    topics = [
        "The Rise of AI Agents in Software Development: Beyond Copilot",
        "Microservices Architecture: Best Practices for 2024",
        "The Future of Remote Work: Tools and Strategies",
        "Data Engineering Trends: What's Next in 2024",
        "Cybersecurity in the Age of AI: New Challenges and Solutions"
    ]
    
    # Generate article for the first topic
    topic = topics[0]
    print(f"Generating article for: {topic}")
    
    try:
        # Generate article with export functionality
        result = workflow.generate_article(topic, export_files=True, output_dir="generated_articles")
        workflow.display_results(result)
        
        # Also save results to markdown file
        with open("generated_article.md", "w") as f:
            f.write(f"# {result['topic']}\n\n")
            f.write(f"## Article\n\n{result['article']}\n\n")
            f.write(f"## LinkedIn Post\n\n{result['linkedin_post']}\n\n")
            f.write(f"## Image Prompt\n\n{result['image_prompt']}\n\n")
            f.write(f"## Hashtags\n\n{', '.join(result['hashtags'])}\n\n")
            f.write(f"## SEO Keywords\n\n{', '.join(result['seo_keywords'])}\n")
        
        print(f"\nMarkdown file saved to 'generated_article.md'")
        
        # Display export information
        if result.get('export_paths'):
            print(f"\nExport files created:")
            print(f"Word document: {result['export_paths']['word_document']}")
            print(f"JPEG image: {result['export_paths']['image_file']}")
        
    except Exception as e:
        print(f"Error generating article: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    main()
