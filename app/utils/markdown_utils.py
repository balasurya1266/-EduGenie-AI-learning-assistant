"""Markdown rendering utilities."""
import markdown
from pygments.formatters import HtmlFormatter


def render_markdown(text: str) -> str:
    extensions = ["fenced_code", "tables", "nl2br", "sane_lists"]
    html_content = markdown.markdown(text, extensions=extensions)
    return html_content


def get_code_css() -> str:
    return HtmlFormatter(style="monokai").get_style_defs(".highlight")
