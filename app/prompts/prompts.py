"""Optimized prompts for all AI modules."""

QA_SYSTEM = """You are EduGenie, an expert educational AI tutor. Provide accurate, well-structured answers for students.

Format your response in Markdown with these sections:
## Answer
(Clear, accurate explanation)

## Examples
(2-3 practical examples)

## Important Notes
(Key points to remember)

## Key Takeaways
(Bullet points)

## Related Topics
(Topics to explore next)

## Reference Links
(Suggest reputable educational resources if applicable, as markdown links)
"""

QA_RAG_CONTEXT = """Use the following document context to answer the question. If the context doesn't contain enough information, say so and provide general knowledge.

Context:
{context}

Question: {question}
"""

EXPLAIN_PROMPT = """Explain the topic "{topic}" at a {level} level for students.

Structure your response EXACTLY with these sections:

## Definition
(What is it?)

## Why It Is Important
(Real-world relevance)

## Simple Explanation
(Easy to understand explanation)

## Example
(A concrete example)

## Real Life Analogy
(An everyday comparison)

## Summary
(Brief recap in 2-3 sentences)
"""

QUIZ_PROMPT = """Generate {num_questions} multiple-choice questions about "{topic}" at {difficulty} difficulty.

Return ONLY valid JSON array with this structure:
[
  {{
    "question": "Question text?",
    "option_a": "Option A",
    "option_b": "Option B",
    "option_c": "Option C",
    "option_d": "Option D",
    "correct_option": "A",
    "explanation": "Why this answer is correct"
  }}
]

Rules:
- Questions must be educational and accurate
- Exactly 4 options per question
- correct_option must be A, B, C, or D
- Include clear explanations
"""

SUMMARY_PROMPTS = {
    "short": "Create a concise 2-3 paragraph summary of the following educational content.",
    "medium": "Create a medium-length summary with main points and supporting details.",
    "detailed": "Create a comprehensive detailed summary covering all important aspects.",
    "bullet": "Create bullet-point summary with organized sections.",
    "exam": "Create exam-focused notes with key facts, formulas, and definitions.",
    "concepts": "Extract and explain key concepts with important definitions.",
}

SUMMARY_FORMAT = """{instruction}

Also include:
## Key Concepts
## Important Definitions

Content:
{text}
"""

LEARNING_PATH_PROMPT = """Create a personalized learning roadmap for:

Topic: {topic}
Current Level: {current_level}
Weekly Study Hours: {weekly_hours}
Goal: {goal}

Structure your response in Markdown:

## Personalized Roadmap
(Overview of the learning journey)

## Weekly Timeline
(Week-by-week breakdown)

## Resources
(Books, courses, websites)

## Projects
(Hands-on projects to build skills)

## Milestones
(Key achievements to track)

## Career Suggestions
(How this skill applies to careers)
"""

FLASHCARD_PROMPT = """Generate {num_cards} educational flashcards about "{topic}".

Return ONLY valid JSON array:
[
  {{"front": "Question or term", "back": "Answer or definition"}}
]
"""
