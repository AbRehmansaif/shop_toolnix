from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def seo_description(text):
    """
    Parses a plain-text product description and formats it into SEO-friendly HTML
    with proper h3 and h4 tags for readability and search engine structure.
    """
    if not text:
        return ""
    
    lines = text.replace('\r', '').split('\n')
    html = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. Short lines with no colon are treated as section headers (h3)
        # e.g., "About this item"
        if len(line) < 40 and ':' not in line and not line.endswith('.'):
            html.append(f'<h3 style="font-family:var(--font-display); font-size:20px; font-weight:800; margin-top:24px; margin-bottom:12px; color:var(--ink);">{line}</h3>')
            continue
            
        # 2. Lines with a colon are split into a bold h4 title and paragraph body
        # e.g., "Fast Charging for MacBook: This charger delivers..."
        if ':' in line:
            parts = line.split(':', 1)
            title = parts[0].strip()
            content = parts[1].strip()
            
            # If the title part is reasonably short, format it as an h4 feature bullet
            if len(title) < 80:
                html.append(f'<div style="margin-bottom:16px;">')
                html.append(f'  <h4 style="font-size:16px; font-weight:700; display:inline; color:var(--ink);">{title}:</h4> ')
                if content:
                    html.append(f'  <span style="color:var(--muted); line-height:1.7;">{content}</span>')
                html.append(f'</div>')
                continue
                
        # 3. Default fallback for standard paragraph text
        html.append(f'<p style="margin-bottom:16px; color:var(--muted); line-height:1.7;">{line}</p>')
        
    return mark_safe('\n'.join(html))
