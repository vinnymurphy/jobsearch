import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="render_markdown")
def render_markdown(text):
    if not text:
        return ""
    # Convert markdown to HTML and mark it safe so Django doesn't
    # escape the tags
    html_content = markdown.markdown(text, extensions=["extra", "nl2br"])
    return mark_safe(html_content)
