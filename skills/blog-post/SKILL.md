---
name: blog-post
description: This skill should be used when the user asks to "write a blog post", "draft a blog post", "create a blog post", "write an article about", or wants to produce a markdown blog post on any topic. Outputs to ~/claude-posts/.
user-invocable: true
---

# Blog Post Drafter

Draft a well-structured blog post in markdown and save it to `~/claude-posts/`.

## Workflow

### 1. Clarify the Topic

If the user provided a clear topic, proceed. Otherwise, ask:
- What is the topic or title?
- Who is the target audience? (developers, general public, beginners, etc.)
- What tone? (casual, professional, tutorial, opinion)
- Approximate length? (short ~500 words, medium ~1000, long ~2000+)

Default to: developer audience, professional-but-approachable tone, medium length (~1000 words).

### 2. Create Output Directory

Run `mkdir -p ~/claude-posts` to ensure the output directory exists.

### 3. Generate the Slug

Derive a URL-friendly slug from the topic:
- Lowercase, hyphens instead of spaces
- Remove special characters
- Keep it concise (3-6 words max)

The filename format is: `YYYY-MM-DD-slug.md` using today's date.

### 4. Draft the Blog Post

Write the post with this structure:

```markdown
---
title: "Post Title"
date: YYYY-MM-DD
slug: the-slug
tags: [relevant, tags]
draft: true
---

# Post Title

Introduction paragraph — hook the reader with a clear statement of what the post covers and why it matters.

## Section Headings

Body content organized into logical sections. Each section should:
- Make one clear point
- Use concrete examples or code snippets where relevant
- Flow naturally to the next section

## Conclusion

Summarize key takeaways. End with a call to action or thought-provoking question.
```

#### Writing guidelines

- **Lead with value**: Open with the problem or insight, not background filler.
- **Be concrete**: Use examples, code snippets, or data instead of vague claims.
- **Short paragraphs**: 2-4 sentences max. Break up walls of text.
- **Use subheadings**: Every 200-300 words, add a heading to guide scanning.
- **Active voice**: "React renders components" not "Components are rendered by React".
- **Cut filler words**: Remove "basically", "actually", "in order to", "it should be noted that".
- **Code blocks**: Use fenced code blocks with language hints when including code.

### 5. Save the File

Write the completed post to `~/claude-posts/YYYY-MM-DD-slug.md`.

### 6. Present Summary

After saving, confirm:
- File path where the post was saved
- Word count
- A brief summary of what was written
- Suggest 2-3 possible improvements or follow-up edits the user might want
