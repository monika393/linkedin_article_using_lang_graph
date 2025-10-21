# LinkedIn Article Generation System with LangGraph

A sophisticated AI-powered system for generating high-quality LinkedIn articles using LangGraph's state-based workflow orchestration. This system combines multiple specialized AI agents to create comprehensive, research-backed articles with real-time visualization and execution tracking.

## LangGraph — Building Stateful, Reliable AI Workflows

LangGraph is a framework for building **stateful, graph-based workflows** that orchestrate Large Language Models (LLMs), tools, and logic using a directed graph abstraction.

It extends the **LangChain** ecosystem by adding **explicit state management, control flow, and runtime tracing** — making it ideal for **multi-step reasoning**, **agent workflows**, and **production-grade pipelines**.

### What Is LangGraph?

LangGraph lets you represent an AI workflow as a **graph of nodes** where each node performs a computation — such as calling an LLM, fetching data, or applying business logic — and passes results to the next node(s) via a **shared state**.

Instead of chaining steps linearly like in LangChain's `Chain` abstraction, LangGraph lets you define **arbitrary control flow**:
- Branching (if/else logic)
- Loops (retry until success)
- Parallel nodes
- Conditional routing

This gives you fine-grained control over **how data flows** and **how decisions are made** during execution.

### Key Concepts

#### 1. State
A **state** is a structured object (e.g. `TypedDict` or `Pydantic` model) that holds data flowing between nodes.

```python
from typing import TypedDict

class MyState(TypedDict):
    question: str
    answer: str
    sources: list[str]
```

#### 2. Nodes
**Nodes** are functions that take the current state and return an updated state. They can call LLMs, APIs, or apply any business logic.

```python
def research_node(state: MyState) -> MyState:
    # Perform research
    sources = search_database(state["question"])
    state["sources"] = sources
    return state
```

#### 3. Edges
**Edges** define how control flows between nodes. They can be:
- **Simple edges**: Always follow the same path
- **Conditional edges**: Route based on state values

```python
# Simple edge
workflow.add_edge("research", "draft")

# Conditional edge
workflow.add_conditional_edges(
    "critique",
    should_continue,
    {"revise": "moderator", "done": "final"}
)
```

#### 4. Graphs
A **graph** is the complete workflow definition that combines nodes and edges into an executable pipeline.

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(MyState)
workflow.add_node("research", research_node)
workflow.add_node("draft", draft_node)
workflow.add_edge("research", "draft")
workflow.set_entry_point("research")
workflow.add_edge("draft", END)

app = workflow.compile()
```

## Table of Contents

1. [What is LangGraph?](#what-is-langgraph)
2. [LangGraph Concepts](#langgraph-concepts)
3. [Our Use Case: LinkedIn Article Generation](#our-use-case-linkedin-article-generation)
4. [Agent Architecture](#agent-architecture)
5. [Workflow Visualization](#workflow-visualization)
6. [State Management & Execution Tracking](#state-management--execution-tracking)
7. [Code Usage](#code-usage)
8. [Prompt Engineering](#prompt-engineering)
9. [Installation & Setup](#installation--setup)
10. [Examples](#examples)

## What is LangGraph?

LangGraph is a framework for building stateful, multi-actor applications with cycles. It's designed to handle complex workflows where multiple AI agents need to collaborate, make decisions, and iterate based on feedback.

### Key Features:
- **Stateful Workflows**: Maintains state across agent interactions
- **Conditional Routing**: Dynamic path selection based on state
- **Cyclic Execution**: Support for loops and iterative processes
- **Parallel Execution**: Run multiple agents simultaneously
- **Built-in Visualization**: Generate workflow graphs automatically

## LangGraph Concepts

### 1. StateGraph
The core component that defines your workflow structure:

```python
from langgraph.graph import StateGraph, END

# Define your state schema
class ArticleState(TypedDict):
    topic: str
    research_data: str
    article: str
    critique_feedback: list[str]
    # ... other fields

# Create the graph
workflow = StateGraph(ArticleState)
```

### 2. Nodes (Agents)
Individual functions that process the state:

```python
def research_agent(state: ArticleState) -> ArticleState:
    # Process research logic
    state["research_data"] = conduct_research(state["topic"])
    return state

# Add nodes to the graph
workflow.add_node("research", research_agent)
```

### 3. Edges (Connections)
Define the flow between nodes:

```python
# Simple edge
workflow.add_edge("research", "draft")

# Conditional edge
workflow.add_conditional_edges(
    "critique",
    should_continue_revision,
    {
        "revise": "moderator",
        "generate": "image"
    }
)
```

### 4. Compilation & Execution
```python
# Compile the graph
app = workflow.compile()

# Execute with initial state
final_state = app.invoke(initial_state)
```

## Our Use Case: LinkedIn Article Generation

We use LangGraph to orchestrate a complex content generation pipeline that:

1. **Researches** topics using academic and industry sources
2. **Drafts** comprehensive articles with storytelling elements
3. **Critiques** content for quality and completeness
4. **Revises** based on feedback (with potential additional research)
5. **Generates** supporting content (images, posts, SEO)

### Why LangGraph for This Use Case?

- **Iterative Refinement**: Articles go through multiple revision cycles
- **Conditional Logic**: Different paths based on critique feedback
- **State Persistence**: Maintains research data, revisions, and context
- **Parallel Generation**: Create multiple outputs simultaneously
- **Visualization**: Track the entire process in real-time

## Agent Architecture

Our system consists of 7 specialized agents working in a coordinated workflow:

### 1. Research Agent
**Purpose**: Gather comprehensive research data
- **Input**: Topic
- **Output**: Research data with academic sources
- **Features**: Focuses on recent sources (2023-2025), case studies, real-world implementations

### 2. Draft Agent  
**Purpose**: Create initial article draft
- **Input**: Research data + topic
- **Output**: 9000-10000 word article
- **Features**: Storytelling format, technical accuracy, academic citations

### 3. Critique Agent
**Purpose**: Evaluate article quality
- **Input**: Article + research data
- **Output**: Pass/fail decision + feedback list
- **Features**: Comprehensive quality assessment, identifies research gaps

### 4. Moderator Agent
**Purpose**: Revise articles based on feedback
- **Input**: Article + critique feedback + research data
- **Output**: Improved article
- **Features**: Incorporates both original and additional research

### 5. Image Agent
**Purpose**: Generate image prompts
- **Input**: Article content
- **Output**: DALL-E compatible image prompt
- **Features**: Professional, abstract visual concepts

### 6. Post Agent
**Purpose**: Create LinkedIn post
- **Input**: Article summary
- **Output**: 900-1200 character LinkedIn post
- **Features**: Engaging, professional tone

### 7. SEO Agent
**Purpose**: Generate SEO content
- **Input**: Article content
- **Output**: Hashtags + SEO keywords
- **Features**: Optimized for LinkedIn algorithm

## Workflow Visualization

### Text-Based Flow
```
START → RESEARCH → DRAFT → CRITIQUE → [DECISION POINT]
                                    ↓
                              [REVISE] ← [ADDITIONAL RESEARCH]
                                    ↓
                              [CRITIQUE] (loop until pass)
                                    ↓
                              [IMAGE] → [POST] → [SEO] → [FINAL] → END
```

### Agent Relationship Diagram
```
                    ┌─────────────────┐
                    │   RESEARCH      │
                    │   AGENT         │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   DRAFT          │
                    │   AGENT          │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   CRITIQUE      │
                    │   AGENT         │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   DECISION      │
                    │   POINT         │
                    └─────┬─────┬─────┘
                          │     │
                    ┌─────▼─┐   │   ┌─────────────────┐
                    │ REVISE│   │   │ ADDITIONAL      │
                    │ AGENT │◄──┘   │ RESEARCH        │
                    └───────┘       │ AGENT           │
                          │         └─────────────────┘
                          │                   │
                          │                   │
                    ┌─────▼───────┐           │
                    │   CRITIQUE  │◄──────────┘
                    │   (LOOP)    │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐
                    │   PASS      │
                    └─────┬───────┘
                          │
                    ┌─────▼───────┐    ┌─────────────┐    ┌─────────────┐
                    │   IMAGE      │───▶│    POST     │───▶│     SEO     │
                    │   AGENT      │    │   AGENT     │    │   AGENT     │
                    └──────────────┘    └─────────────┘    └─────────────┘
                          │                   │                   │
                          │                   │                   │
                    ┌─────▼───────────────────▼───────────────────▼───────┐
                    │                FINAL ASSEMBLY                        │
                    │              (Word + JPEG Export)                   │
                    └─────────────────────────────────────────────────────┘
```

### State Flow Visualization
```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ARTICLE STATE                                │
├─────────────────────────────────────────────────────────────────────────┤
│ topic: str                    │ Input topic for research              │
│ research_data: str            │ Comprehensive research content        │
│ article: str                  │ Generated article (9000-10000 words)   │
│ critique_feedback: list[str]  │ Quality feedback from critique         │
│ critique_passed: bool         │ Quality gate status                    │
│ revision_count: int          │ Number of revision cycles               │
│ research_calls: int          │ Initial research calls made             │
│ additional_research_calls: int│ Additional research triggered          │
│ agent_call_log: list[dict]   │ Complete execution tracking            │
│ image_prompt: str            │ DALL-E compatible image prompt         │
│ linkedin_post: str           │ LinkedIn post (900-1200 chars)          │
│ hashtags: list[str]          │ Generated hashtags                     │
│ seo_keywords: list[str]       │ SEO optimization keywords              │
│ final_output: dict           │ Complete output package                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Visual Graph Representation

Our system generates interactive HTML visualizations showing:

- **Node Types**: Initial (green), Conditional (orange), Revision (blue), Final (purple)
- **Call Counts**: Actual execution statistics for each node
- **Edge Labels**: Decision paths and execution counts
- **Statistics Panel**: Total calls, research cycles, revisions made

## State Management & Execution Tracking

### How LangGraph Manages State

LangGraph's `StateGraph` provides powerful state management capabilities:

1. **Persistent State**: State persists across all agent calls
2. **Type Safety**: TypedDict ensures consistent state structure
3. **Automatic Updates**: Agents can modify state and changes are preserved
4. **Execution Tracking**: Built-in logging of state transitions
5. **Conditional Routing**: State values determine execution paths

### State Schema
```python
class ArticleState(TypedDict):
    topic: str                          # Input topic
    research_data: str                 # Research content
    article: str                       # Generated article
    critique_feedback: list[str]      # Feedback from critique
    critique_passed: bool             # Quality gate status
    revision_count: int              # Number of revisions
    research_calls: int               # Initial research calls
    additional_research_calls: int    # Additional research calls
    agent_call_log: list[dict]        # Complete execution log
    image_prompt: str                 # Image generation prompt
    linkedin_post: str               # LinkedIn post content
    hashtags: list[str]              # Generated hashtags
    seo_keywords: list[str]          # SEO keywords
    final_output: dict               # Complete output package
```

### Execution Tracking Features

1. **Agent Call Logging**: Every agent call is logged with:
   - Call ID and timestamp
   - Agent name and type
   - Revision count at time of call
   - Research call statistics

2. **State Persistence**: LangGraph maintains state across:
   - Multiple revision cycles
   - Additional research calls
   - Parallel content generation

3. **Visualization Export**: Generate execution graphs showing:
   - Actual node call counts
   - Execution statistics
   - Node sizes based on frequency
   - Edge labels with counts

### How We Use LangGraph State Management

Our implementation leverages LangGraph's state management in several key ways:

#### 1. State Definition
```python
class ArticleState(TypedDict):
    # Core content
    topic: str
    research_data: str
    article: str
    
    # Quality control
    critique_feedback: list[str]
    critique_passed: bool
    revision_count: int
    
    # Execution tracking
    research_calls: int
    additional_research_calls: int
    agent_call_log: list[dict]
```

#### 2. State Updates in Agents
```python
def research_agent(state: ArticleState) -> ArticleState:
    # Update research data
    state["research_data"] = conduct_research(state["topic"])
    
    # Track execution
    state["research_calls"] = state.get("research_calls", 0) + 1
    state["agent_call_log"].append({
        "agent": "ResearchAgent",
        "timestamp": time.time(),
        "revision_count": state["revision_count"]
    })
    
    return state
```

#### 3. Conditional Routing Based on State
```python
def should_continue_revision(state: ArticleState) -> str:
    if state["critique_passed"]:
        return "generate"  # Move to final generation
    elif needs_additional_research(state["critique_feedback"]):
        return "additional_research"  # Get more research
    else:
        return "revise"  # Continue revision cycle
```

#### 4. State Persistence Across Cycles
- **Research Data**: Accumulates across multiple research calls
- **Revision History**: Tracks all revision attempts
- **Execution Log**: Maintains complete call hierarchy
- **Quality Gates**: Remembers critique decisions

## Code Usage

### Basic Usage
```python
from workflow import LinkedInArticleWorkflow

# Initialize workflow
workflow = LinkedInArticleWorkflow()

# Generate article
result = workflow.generate_article_with_langgraph(
    topic="AI Optimization Techniques",
    export_files=True,
    output_dir="output"
)

# Access results
print(f"Article: {result['article']}")
print(f"LinkedIn Post: {result['linkedin_post']}")
print(f"Revisions Made: {result['revisions_made']}")
```

### Advanced Usage with Visualization
```python
# Generate workflow visualization
graph_file = workflow.generate_visual_graph("workflow.html")

# Generate execution graph with call counts
execution_graph = workflow.generate_execution_graph(result, "execution.html")

# Access detailed execution data
agent_calls = result['agent_call_log']
research_calls = result['research_calls']
additional_research = result['additional_research_calls']
```

### Command Line Usage
```bash
# Generate article with full workflow
python main.py

# Generate visualizations only
python generate_graph.py
```

## Prompt Engineering

Our system uses carefully crafted prompts stored in the `text/` directory:

### Research Prompt (`text/research_prompt.txt`)
- Focuses on recent academic sources (2023-2025)
- Emphasizes case studies and real-world implementations
- Requires comprehensive coverage with technical depth

### Draft Prompt (`text/draft_prompt.txt`)
- Targets 9000-10000 word articles
- Combines storytelling with technical accuracy
- Includes specific formatting and citation requirements

### Critique Prompt (`text/critique_prompt.txt`)
- Evaluates multiple quality dimensions
- Identifies research gaps and triggers additional research
- Provides specific, actionable feedback

### Additional Research Prompt (`text/additional_research_prompt.txt`)
- Focuses on addressing specific critique feedback
- Emphasizes case studies and implementation details
- Builds upon existing research data

## Installation & Setup

### Prerequisites
```bash
pip install -U langgraph langgraph-cli
pip install pyvis
pip install python-docx pillow requests python-dotenv
```

### Environment Setup
```bash
# Create .env file
cp .env.example .env

# Edit .env with your OpenAI API key
OPENAI_API_KEY=your-api-key-here
DEFAULT_OUTPUT_DIR=output
```

### Project Structure
```
linkedin-article-generator/
├── agents/                 # Agent implementations
│   ├── research_agent.py
│   ├── draft_agent.py
│   ├── critique_agent.py
│   ├── moderator_agent.py
│   ├── image_agent.py
│   ├── post_agent.py
│   └── seo_agent.py
├── text/                  # Prompt templates
│   ├── research_prompt.txt
│   ├── draft_prompt.txt
│   ├── critique_prompt.txt
│   └── additional_research_prompt.txt
├── utils/                 # Utility functions
│   ├── config.py
│   └── export_utils.py
├── workflow.py           # LangGraph workflow
├── main.py               # Entry point
└── generate_graph.py     # Visualization generator
```

## Examples

### Example 1: Basic Article Generation
```python
from workflow import LinkedInArticleWorkflow

workflow = LinkedInArticleWorkflow()
result = workflow.generate_article_with_langgraph(
    topic="Machine Learning Optimization Techniques"
)

print(f"Generated {len(result['article'])} character article")
print(f"Made {result['revisions_made']} revisions")
print(f"Research calls: {result['research_calls']}")
```

### Example 2: Custom Configuration
```python
# Modify .env file
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
MAX_REVISIONS=5
DEFAULT_OUTPUT_DIR=custom_output
```

### Example 3: Execution Analysis
```python
# Analyze execution patterns
agent_calls = result['agent_call_log']
for call in agent_calls:
    print(f"Call {call['call_id']}: {call['agent_name']} - {call['call_type']}")

# Generate execution visualization
workflow.generate_execution_graph(result, "analysis.html")
```

## Key Benefits

1. **Transparency**: Complete visibility into agent execution
2. **Quality Control**: Multi-stage critique and revision process
3. **Flexibility**: Easy to modify prompts and add new agents
4. **Visualization**: Interactive graphs for debugging and analysis
5. **Scalability**: LangGraph handles complex state management
6. **Professional Output**: High-quality articles with proper citations

## Troubleshooting

### Common Issues
1. **API Key**: Ensure OPENAI_API_KEY is set in .env
2. **Dependencies**: Install all required packages
3. **Output Directory**: Check write permissions for output folder
4. **Memory**: Large articles may require more memory

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Generate with debug information
result = workflow.generate_article_with_langgraph(
    topic="Your Topic",
    export_files=True
)
```

## Contributing

To extend the system:

1. **Add New Agents**: Create new agent classes in `agents/`
2. **Modify Workflow**: Update `workflow.py` to include new nodes
3. **Custom Prompts**: Add new prompt templates in `text/`
4. **Export Formats**: Extend `utils/export_utils.py` for new formats

## License

This project is open source and available under the MIT License.