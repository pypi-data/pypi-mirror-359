# Slidesmith Markdown Specification

## Overview
This document defines the Markdown syntax for Slidesmith slides, replacing the MDX format with a simpler, pure-Python approach.

## Basic Structure

### Slide Separation
Slides are separated by `---` on its own line:

```markdown
---
slide: 1
template: title
---

# First Slide

---
slide: 2
template: standard
---

# Second Slide
```

### Frontmatter
Each slide can have YAML frontmatter defining metadata:

```yaml
---
slide: 1                # Slide number (auto-incremented if omitted)
template: standard      # Template type (default: standard)
theme: markov-pro      # Theme name (default: markov-pro)
transition: fade       # Transition type (optional)
notes: Speaker notes   # Short speaker notes (optional)
---
```

## Component Syntax

### Block Components
Components are defined using `:::component-name` blocks:

```markdown
:::columns ratio=7:5
### Left Column
Content for left column

### Right Column  
Content for right column
:::
```

### Nested Components
Components can be nested:

```markdown
:::columns ratio=6:6
### Analysis
:::chart type=bar
title: Performance Metrics
data: [95, 87, 92, 88]
labels: [Speed, Quality, Ease, Value]
:::

### Summary
Key insights from the data
:::
```

### Component Parameters
Parameters use key=value syntax:
- Strings: `title="My Title"` or `title='My Title'`
- Numbers: `size=24`
- Arrays: `data=[1, 2, 3]`
- Objects: `config={theme: 'dark', animated: true}`

## Supported Components

### Layout Components

#### columns
```markdown
:::columns ratio=7:5
### Left
Content

### Right
Content
:::
```

#### grid
```markdown
:::grid cols=3 gap=4
### Card 1
Content

### Card 2
Content

### Card 3
Content
:::
```

### Data Components

#### chart
```markdown
:::chart type=bar
title: Sales Data
data: [100, 150, 125, 200]
labels: [Q1, Q2, Q3, Q4]
colors: ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
:::
```

Supported types: bar, line, pie, doughnut, radar

#### metrics
```markdown
:::metrics
- value: 125%
  label: Growth Rate
  trend: +15% from last quarter
- value: $2.4M
  label: Revenue
  trend: Exceeded target
- value: 98.5%
  label: Satisfaction
  trend: Industry leading
:::
```

#### table
```markdown
:::table
| Feature | Basic | Pro | Enterprise |
|---------|-------|-----|------------|
| Users   | 10    | 100 | Unlimited  |
| Storage | 5GB   | 50GB| 500GB      |
| Support | Email | 24/7 | Dedicated  |
:::
```

### Content Components

#### card
```markdown
:::card title="Key Feature" icon=rocket color=blue
Powerful functionality that drives results
:::
```

#### callout
```markdown
:::callout type=info
Important information highlighted for emphasis
:::
```

Types: info, warning, success, error

#### timeline
```markdown
:::timeline
- date: 2024 Q1
  title: Project Kickoff
  description: Initial planning and team formation
- date: 2024 Q2
  title: Development Phase
  description: Core features implemented
- date: 2024 Q3
  title: Beta Launch
  description: Limited release to test users
:::
```

### Special Components

#### speaker-notes
```markdown
:::speaker-notes
These notes are only visible in presenter mode.
Key points to remember:
- Emphasize the growth metrics
- Mention the team's hard work
:::
```

#### code
```markdown
:::code language=python
def hello_world():
    print("Hello, Slidesmith!")
:::
```

#### image
```markdown
:::image src="assets/diagram.png" alt="Architecture Diagram" width=800
caption: System architecture overview
:::
```

## Standard Markdown Support

All standard Markdown features are supported:
- Headers: `# H1`, `## H2`, etc.
- Lists: `- item` or `1. item`
- Bold: `**text**`
- Italic: `*text*`
- Links: `[text](url)`
- Images: `![alt](url)`
- Code: `` `inline` `` or ``` ```block``` ```
- Quotes: `> quote`
- Tables: Standard GFM tables

## Examples

### Title Slide
```markdown
---
slide: 1
template: title
---

# Quarterly Business Review
## Q4 2024 Performance Report

**Presented by:** Sarah Johnson  
**Date:** January 15, 2025

:::speaker-notes
Welcome everyone to our Q4 review.
We've had an exceptional quarter.
:::
```

### Metrics Dashboard
```markdown
---
slide: 2
template: metrics
---

# Key Performance Indicators

:::metrics
- value: $8.2M
  label: Total Revenue
  trend: +32% YoY
- value: 1,248
  label: New Customers
  trend: +18% vs target
- value: 4.8/5
  label: Customer Rating
  trend: All-time high
:::

:::callout type=success
Best quarter in company history!
:::
```

### Comparison Slide
```markdown
---
slide: 3
template: standard
---

# Product Comparison

:::columns ratio=5:7
### Our Solution
- ✅ Cloud-native architecture
- ✅ Real-time collaboration
- ✅ AI-powered insights
- ✅ Enterprise security
- ✅ 24/7 support

### Competition
:::table
| Feature | Us | Competitor A | Competitor B |
|---------|-----|--------------|--------------|
| Speed   | 5ms | 50ms        | 100ms        |
| Uptime  | 99.99% | 99.5%    | 99%          |
| Price   | $$  | $$$         | $$$$         |
:::
:::
```

## Validation Rules

1. **Component Names**: Must be lowercase with hyphens (e.g., `speaker-notes`, not `SpeakerNotes`)
2. **Parameter Names**: Must be valid identifiers (alphanumeric + underscore)
3. **Component Closure**: All components must be properly closed with `:::`
4. **Nesting**: Maximum nesting depth of 3 levels
5. **Frontmatter**: Must be valid YAML
6. **Slide Numbers**: Must be positive integers (auto-assigned if missing)

## Error Handling

The parser will provide clear error messages:
- `Line 15: Unclosed component 'columns' (opened at line 10)`
- `Line 8: Invalid parameter syntax in 'chart' component`
- `Line 3: Invalid frontmatter: expected key-value pairs`

## Future Extensions

Reserved syntax for future features:
- `:::animate type=fade delay=500` - Animation directives
- `:::layout template=custom-name` - Custom layout templates
- `:::style css="..."` - Inline CSS overrides
- `@import "shared/header.md"` - Include external content