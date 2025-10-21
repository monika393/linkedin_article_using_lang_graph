"""
Export Example for LinkedIn Article Generation System
Demonstrates Word document and JPEG image export functionality
"""

import os
from workflow import LinkedInArticleWorkflow
from utils import export_to_word, export_image_to_jpeg, create_article_package


def main():
    """Example of generating and exporting articles"""
    
    # Set up OpenAI API key (you'll need to set this in your environment)
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    # Initialize the workflow
    workflow = LinkedInArticleWorkflow()
    
    # Example topic
    topic = "The Future of AI in Software Development: Trends and Predictions for 2024"
    
    print(f"Generating and exporting article for: {topic}")
    
    try:
        # Generate article with automatic export
        result = workflow.generate_article(
            topic=topic,
            export_files=True,
            output_dir="exported_articles"
        )
        
        # Display results
        workflow.display_results(result)
        
        # Show export information
        if result.get('export_paths'):
            print(f"\nExport completed successfully!")
            print(f"Word document: {result['export_paths']['word_document']}")
            print(f"JPEG image: {result['export_paths']['image_file']}")
            print(f"Output directory: {result['export_paths']['output_directory']}")
        
        # Demonstrate individual export functions
        print(f"\nDemonstrating individual export functions...")
        
        # Export just the Word document
        word_path = "individual_article.docx"
        export_to_word(result, word_path)
        print(f"Individual Word document saved to: {word_path}")
        
        # Export just the image
        image_path = "individual_image.jpg"
        export_image_to_jpeg(result, image_path)
        print(f"Individual JPEG image saved to: {image_path}")
        
        # Create a complete package
        package_paths = create_article_package(result, "article_package")
        print(f"\nComplete package created:")
        print(f"Word document: {package_paths['word_document']}")
        print(f"JPEG image: {package_paths['image_file']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable")
        print("Also ensure you have installed the required dependencies:")
        print("pip install python-docx Pillow requests")


def demonstrate_export_options():
    """Demonstrate different export options"""
    
    print("Export Options Demonstration")
    print("=" * 50)
    
    # Sample article data for demonstration
    sample_data = {
        'topic': 'Sample Article Topic',
        'article': '# Sample Article\n\nThis is a sample article content with multiple paragraphs.\n\n## Section 1\n\nContent for section 1.\n\n## Section 2\n\nContent for section 2.',
        'linkedin_post': 'This is a sample LinkedIn post for the article.',
        'hashtags': ['#AI', '#Tech', '#Innovation'],
        'seo_keywords': ['artificial intelligence', 'technology', 'innovation'],
        'image_prompt': 'Abstract technology illustration with blue and white colors',
        'revisions_made': 1
    }
    
    try:
        # Test Word export
        print("Testing Word document export...")
        word_path = "test_article.docx"
        export_to_word(sample_data, word_path)
        print(f"Word document created: {word_path}")
        
        # Test image export
        print("Testing JPEG image export...")
        image_path = "test_image.jpg"
        export_image_to_jpeg(sample_data, image_path)
        print(f"JPEG image created: {image_path}")
        
        # Test package creation
        print("Testing complete package creation...")
        package_paths = create_article_package(sample_data, "test_package")
        print(f"Package created in: {package_paths['output_directory']}")
        
        print("\nAll export functions working correctly!")
        
    except Exception as e:
        print(f"Export test failed: {e}")
        print("Make sure you have installed: pip install python-docx Pillow requests")


if __name__ == "__main__":
    print("LinkedIn Article Generation - Export Example")
    print("=" * 50)
    
    # Run the main example
    main()
    
    print("\n" + "=" * 50)
    print("Testing export functions with sample data...")
    
    # Test export functions
    demonstrate_export_options()
