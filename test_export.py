"""
Test script to check export functionality
"""

from utils.export_utils import create_article_package, export_to_word, export_image_to_jpeg
import os

def test_export():
    """Test the export functionality"""
    
    print("Testing Export Functionality")
    print("=" * 40)
    
    # Create test article data
    test_article_data = {
        'topic': 'Test Article Topic',
        'article': '# Test Article\n\nThis is a test article content.',
        'image_prompt': 'Create a professional abstract image about technology and innovation',
        'linkedin_post': 'Test LinkedIn post content',
        'hashtags': ['#Test', '#Technology'],
        'seo_keywords': ['test', 'technology'],
        'revisions_made': 1
    }
    
    # Test 1: Word document export
    print("1. Testing Word document export...")
    try:
        word_path = "test_output/test_article.docx"
        word_file = export_to_word(test_article_data, word_path)
        print(f"✅ Word document created: {word_file}")
        print(f"   File exists: {os.path.exists(word_file)}")
        print(f"   File size: {os.path.getsize(word_file)} bytes")
    except Exception as e:
        print(f"❌ Word export failed: {e}")
    
    # Test 2: Image export (with placeholder)
    print("\n2. Testing image export (placeholder)...")
    try:
        image_path = "test_output/test_article.jpg"
        image_file = export_image_to_jpeg(test_article_data, image_path, use_dalle=False)
        print(f"✅ Image created: {image_file}")
        print(f"   File exists: {os.path.exists(image_file)}")
        print(f"   File size: {os.path.getsize(image_file)} bytes")
    except Exception as e:
        print(f"❌ Image export failed: {e}")
    
    # Test 3: Complete package
    print("\n3. Testing complete package...")
    try:
        package = create_article_package(test_article_data, "test_output")
        print(f"✅ Package created:")
        print(f"   Word: {package['word_document']}")
        print(f"   Image: {package['image_file']}")
        print(f"   Directory: {package['output_directory']}")
        
        # Check if files exist
        word_exists = os.path.exists(package['word_document'])
        image_exists = os.path.exists(package['image_file'])
        
        print(f"   Word exists: {word_exists}")
        print(f"   Image exists: {image_exists}")
        
        if word_exists:
            print(f"   Word size: {os.path.getsize(package['word_document'])} bytes")
        if image_exists:
            print(f"   Image size: {os.path.getsize(package['image_file'])} bytes")
            
    except Exception as e:
        print(f"❌ Package creation failed: {e}")
    
    print("\n" + "=" * 40)
    print("Export test completed!")

if __name__ == "__main__":
    test_export()
