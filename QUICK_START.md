# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
cd linkedin-article-generator
pip install -r requirements.txt
```

### 2. Set API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run Example
```bash
python examples/basic_usage.py
```

## 📁 What's Included

- **7 Specialized Agents**: Research, Draft, Critique, Moderator, Image, Post, SEO
- **Parallel Execution**: Image, post, and SEO generation run simultaneously
- **Quality Control**: Multi-pass critique and revision system
- **Batch Processing**: Generate multiple articles at once
- **Professional Output**: Optimized for LinkedIn technical content

## 🎯 Key Features

### Sequential Workflow
1. **Research** → Gathers comprehensive topic data
2. **Draft** → Creates 800-1200 word article
3. **Critique** → Evaluates quality and structure
4. **Moderate** → Revises based on feedback (with loop)

### Parallel Generation
- **Image Agent** → DALL-E/Midjourney prompts
- **Post Agent** → LinkedIn promotional posts
- **SEO Agent** → Hashtags and keywords

## 📊 Output Example

```markdown
# The Rise of AI Agents in Software Development

## Article
[Full professional article with sections and examples]

## LinkedIn Post
"AI agents are revolutionizing software development beyond simple code completion..."

## Image Prompt
"Abstract geometric composition representing AI and software development..."

## Hashtags
#AI #SoftwareDevelopment #TechInnovation

## SEO Keywords
AI agents, software development, code automation
```

## 🔧 Customization

### Modify Agents
```python
# Custom research agent
class CustomResearchAgent(ResearchAgent):
    def __call__(self, state):
        # Your custom logic
        return super().__call__(state)
```

### Add New Parallel Agent
```python
# Add to workflow
workflow.add_node("custom_agent", custom_agent)
workflow.add_edge("image_gen", "custom_agent")
```

## 📈 Advanced Usage

### Batch Generation
```python
from examples.batch_generation import generate_multiple_articles

topics = ["Topic 1", "Topic 2", "Topic 3"]
results = generate_multiple_articles(topics)
```

### Custom Workflow
```python
from workflow import LinkedInArticleWorkflow

workflow = LinkedInArticleWorkflow()
result = workflow.generate_article("Your Topic")
workflow.display_results(result)
```

## 🆘 Troubleshooting

### Common Issues
1. **Import Error**: Run `pip install -r requirements.txt`
2. **API Key Error**: Set `OPENAI_API_KEY` environment variable
3. **Memory Issues**: Reduce batch size or article length

### Getting Help
- Check `examples/` directory for usage patterns
- Review `agents/` for implementation details
- See `AGENT_FLOW.md` for workflow documentation

## 🎉 Ready to Generate!

Your LinkedIn Article Generation System is ready to create professional, high-quality content with AI agents working in parallel for maximum efficiency.
