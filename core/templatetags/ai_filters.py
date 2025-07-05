from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def extract_ai_analysis(text):
    """Extract AI analysis section from diagnosis text."""
    if not text:
        return ""
    
    if "AI Analysis:" in text:
        parts = text.split("AI Analysis:")
        if len(parts) > 1:
            return parts[1].strip()
    
    return text

@register.filter
def has_ai_analysis(text):
    """Check if text contains AI analysis."""
    return text and "AI Analysis:" in text 