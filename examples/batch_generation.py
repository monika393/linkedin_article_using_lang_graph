"""
Batch generation example for multiple LinkedIn articles
"""

import os
import json
from datetime import datetime
from workflow import LinkedInArticleWorkflow


def generate_multiple_articles(topics: list, output_dir: str = "generated_articles"):
    """Generate multiple articles in batch"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize workflow
    workflow = LinkedInArticleWorkflow()
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*60}")
        print(f"Generating Article {i}/{len(topics)}: {topic}")
        print(f"{'='*60}")
        
        try:
            # Generate article with export functionality
            result = workflow.generate_article(topic, export_files=True, output_dir=output_dir)
            results.append(result)
            
            # Save individual article markdown
            filename = f"article_{i:02d}_{topic.replace(' ', '_').replace(':', '')[:30]}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(f"# {result['topic']}\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Revisions:** {result['revisions_made']}\n\n")
                f.write(f"## Article\n\n{result['article']}\n\n")
                f.write(f"## LinkedIn Post\n\n{result['linkedin_post']}\n\n")
                f.write(f"## Image Prompt\n\n{result['image_prompt']}\n\n")
                f.write(f"## Hashtags\n\n{', '.join(result['hashtags'])}\n\n")
                f.write(f"## SEO Keywords\n\n{', '.join(result['seo_keywords'])}\n")
            
            print(f"Article saved to: {filepath}")
            
            # Display export information
            if result.get('export_paths'):
                print(f"Word document: {result['export_paths']['word_document']}")
                print(f"JPEG image: {result['export_paths']['image_file']}")
            
        except Exception as e:
            print(f"Error generating article for '{topic}': {e}")
            continue
    
    # Save summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_articles": len(results),
        "topics": topics,
        "results": results
    }
    
    summary_path = os.path.join(output_dir, "generation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nBatch generation complete!")
    print(f"Articles saved in: {output_dir}")
    print(f"Summary saved to: {summary_path}")
    
    return results


def main():
    """Example batch generation"""
    
    # Example topics for batch generation
    topics = [
        "The Rise of AI Agents in Software Development: Beyond Copilot",
        "Microservices Architecture: Best Practices for 2024",
        "The Future of Remote Work: Tools and Strategies",
        "Data Engineering Trends: What's Next in 2024",
        "Cybersecurity in the Age of AI: New Challenges and Solutions",
        "Cloud-Native Development: Container Orchestration Best Practices",
        "Machine Learning Operations (MLOps): Scaling AI in Production",
        "API Design Patterns: Building Developer-Friendly Interfaces"
    ]
    
    print("Starting batch article generation...")
    print(f"Topics: {len(topics)}")
    
    try:
        results = generate_multiple_articles(topics)
        print(f"\nSuccessfully generated {len(results)} articles!")
        
    except Exception as e:
        print(f"Batch generation failed: {e}")


if __name__ == "__main__":
    main()
