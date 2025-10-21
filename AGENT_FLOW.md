# LinkedIn Article Generation Agent Flow

## Sequential Phase (Research → Draft → Critique → Revise Loop)

```
START
  ↓
[Research Agent] → Gathers topic data, trends, statistics
  ↓
[Draft Writer Agent] → Creates initial article (800-1200 words)
  ↓
[Critique Agent] → Evaluates article quality
  ↓
    ┌─ PASS? ──→ [Parallel Generation Phase]
    │
    └─ FAIL? ──→ [Moderator Agent] → Revises article
                    ↓
                [Critique Agent] (loop back)
                    ↓
                Max revisions? → Force proceed to parallel
```

## Parallel Phase (All run simultaneously after critique passes)

```
[Image Generator Agent] ──┐
                         ├─→ [Final Assembly Agent] → END
[Post Creator Agent] ────┤
                         │
[SEO/Hashtag Agent] ─────┘
```

## Agent Responsibilities

### Sequential Agents:
1. **Research Agent**: Topic research, data gathering, trend analysis
2. **Draft Writer Agent**: Initial article creation with professional tone
3. **Critique Agent**: Quality evaluation (authenticity, structure, LinkedIn suitability)
4. **Moderator Agent**: Article revision based on critique feedback

### Parallel Agents (Run simultaneously):
1. **Image Generator Agent**: Creates DALL-E/Midjourney prompts for article images
2. **Post Creator Agent**: Generates LinkedIn promotional post text
3. **SEO/Hashtag Agent**: Creates hashtags and SEO keywords

### Final Assembly:
- Combines all outputs into structured final result
- Tracks revision count and quality metrics

## Key Features:
- **Parallelization**: Image, post, and SEO generation run simultaneously
- **Quality Control**: Multi-pass critique and revision system
- **Professional Focus**: Optimized for LinkedIn technical content
- **Scalable**: Easy to add new parallel agents
