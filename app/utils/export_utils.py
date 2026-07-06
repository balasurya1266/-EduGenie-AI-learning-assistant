"""Export utilities for PDF generation."""
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def export_text_pdf(title: str, content: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=18, spaceAfter=20)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=11, leading=14, spaceAfter=8)

    story = [Paragraph(_escape(title), title_style), Spacer(1, 12)]
    for line in content.split("\n"):
        if line.strip():
            story.append(Paragraph(_escape(line), body_style))
        else:
            story.append(Spacer(1, 6))
    doc.build(story)
    return buffer.getvalue()


def export_quiz_pdf(topic: str, questions: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"Quiz: {_escape(topic)}", styles["Heading1"]),
        Spacer(1, 20),
    ]
    for i, q in enumerate(questions, 1):
        story.append(Paragraph(f"Q{i}. {_escape(q.get('question', ''))}", styles["Heading3"]))
        for opt in ("A", "B", "C", "D"):
            key = f"option_{opt.lower()}"
            if key in q:
                story.append(Paragraph(f"  {opt}) {_escape(q[key])}", styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    return buffer.getvalue()
