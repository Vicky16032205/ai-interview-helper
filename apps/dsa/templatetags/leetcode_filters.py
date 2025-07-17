from django import template
import re

register = template.Library()

@register.filter
def leetcode_slug(value):
    """
    Convert question title to LeetCode URL format
    Example: "Merge Two Sorted Lists" -> "merge-two-sorted-lists"
    """
    if not value:
        return ""
    
    # Convert to lowercase
    slug = value.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars except spaces and hyphens
    slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple hyphens with single hyphen
    slug = slug.strip('-')                # Remove leading/trailing hyphens
    
    return slug
