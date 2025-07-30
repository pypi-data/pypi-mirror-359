"""
Advanced theming system for SlideSmith.
Provides customizable design tokens and theme variants.
"""

from typing import Dict, Any
from pathlib import Path


class ThemeRegistry:
    """Registry for managing SlideSmith themes."""
    
    def __init__(self):
        self.themes = {
            'markov-pro': self._get_markov_pro_theme(),
            'minimal': self._get_minimal_theme(),
            'tech': self._get_tech_theme(),
            'corporate': self._get_corporate_theme(),
            'creative': self._get_creative_theme(),
            'dark': self._get_dark_theme()
        }
    
    def get_theme(self, theme_name: str) -> Dict[str, Any]:
        """Get theme tokens by name."""
        return self.themes.get(theme_name, self.themes['markov-pro'])
    
    def list_themes(self) -> list:
        """List all available theme names."""
        return list(self.themes.keys())
    
    def _get_markov_pro_theme(self) -> Dict[str, Any]:
        """Professional business theme with blue accents."""
        return {
            "name": "Markov Pro",
            "description": "Professional business theme with clean typography",
            "colors": {
                "primary": "#111827",      # Dark gray
                "secondary": "#374151",    # Medium gray  
                "accent": "#3B82F6",       # Blue
                "success": "#10B981",      # Green
                "warning": "#F59E0B",      # Orange
                "error": "#EF4444",        # Red
                "background": "#FFFFFF",   # White
                "surface": "#F9FAFB",      # Light gray
                "text": "#111827",         # Dark gray
                "text_secondary": "#6B7280", # Medium gray
                "border": "#E5E7EB"        # Light border
            },
            "fonts": {
                "heading": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
                "body": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", 
                "mono": "'Fira Code', 'SF Mono', 'Monaco', 'Consolas', monospace"
            },
            "typography": {
                "h1_size": "4.5rem",      # 72px
                "h1_weight": "800",
                "h2_size": "3rem",        # 48px
                "h2_weight": "700",
                "h3_size": "2.25rem",     # 36px
                "h3_weight": "600",
                "body_size": "1.25rem",   # 20px
                "body_line_height": "1.8"
            },
            "spacing": {
                "xs": "0.5rem",   # 8px
                "sm": "1rem",     # 16px
                "md": "1.5rem",   # 24px
                "lg": "2rem",     # 32px
                "xl": "3rem",     # 48px
                "2xl": "4rem",    # 64px
                "3xl": "6rem"     # 96px
            },
            "shadows": {
                "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                "md": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1)",
                "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1)"
            },
            "animations": {
                "duration_fast": "150ms",
                "duration_normal": "300ms", 
                "duration_slow": "500ms",
                "easing": "cubic-bezier(0.4, 0, 0.2, 1)"
            }
        }
    
    def _get_minimal_theme(self) -> Dict[str, Any]:
        """Clean minimal theme with subtle styling."""
        return {
            "name": "Minimal",
            "description": "Clean and minimal design with subtle accents",
            "colors": {
                "primary": "#1F2937",
                "secondary": "#4B5563", 
                "accent": "#6366F1",
                "success": "#059669",
                "warning": "#D97706",
                "error": "#DC2626",
                "background": "#FFFFFF",
                "surface": "#FAFAFA",
                "text": "#1F2937",
                "text_secondary": "#6B7280",
                "border": "#F3F4F6"
            },
            "fonts": {
                "heading": "'Helvetica Neue', Helvetica, Arial, sans-serif",
                "body": "'Helvetica Neue', Helvetica, Arial, sans-serif",
                "mono": "'SF Mono', Monaco, 'Cascadia Code', monospace"
            },
            "typography": {
                "h1_size": "4rem",
                "h1_weight": "300",
                "h2_size": "2.5rem", 
                "h2_weight": "400",
                "h3_size": "2rem",
                "h3_weight": "500",
                "body_size": "1.125rem",
                "body_line_height": "1.75"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.75rem",
                "md": "1.25rem", 
                "lg": "2rem",
                "xl": "3rem",
                "2xl": "4.5rem",
                "3xl": "6rem"
            },
            "shadows": {
                "sm": "0 1px 2px 0 rgb(0 0 0 / 0.03)",
                "md": "0 2px 4px 0 rgb(0 0 0 / 0.06)",
                "lg": "0 4px 8px 0 rgb(0 0 0 / 0.08)",
                "xl": "0 8px 16px 0 rgb(0 0 0 / 0.1)"
            },
            "animations": {
                "duration_fast": "100ms",
                "duration_normal": "200ms",
                "duration_slow": "400ms", 
                "easing": "ease-out"
            }
        }
    
    def _get_tech_theme(self) -> Dict[str, Any]:
        """Tech-focused theme with cyan accents."""
        return {
            "name": "Tech",
            "description": "Modern tech theme with vibrant cyan accents",
            "colors": {
                "primary": "#0F172A",
                "secondary": "#334155",
                "accent": "#06B6D4",
                "success": "#00D9FF",
                "warning": "#FCD34D",
                "error": "#F87171",
                "background": "#FFFFFF",
                "surface": "#F8FAFC",
                "text": "#0F172A",
                "text_secondary": "#64748B",
                "border": "#E2E8F0"
            },
            "fonts": {
                "heading": "'JetBrains Mono', 'SF Mono', monospace",
                "body": "'Inter', sans-serif",
                "mono": "'JetBrains Mono', 'Fira Code', monospace"
            },
            "typography": {
                "h1_size": "4rem",
                "h1_weight": "700",
                "h2_size": "2.75rem",
                "h2_weight": "600", 
                "h3_size": "2rem",
                "h3_weight": "500",
                "body_size": "1.125rem",
                "body_line_height": "1.7"
            },
            "spacing": {
                "xs": "0.5rem",
                "sm": "1rem",
                "md": "1.5rem",
                "lg": "2.5rem",
                "xl": "4rem",
                "2xl": "5rem",
                "3xl": "7rem"
            },
            "shadows": {
                "sm": "0 0 0 1px rgb(6 182 212 / 0.1)",
                "md": "0 4px 6px -1px rgb(6 182 212 / 0.2)",
                "lg": "0 8px 16px -4px rgb(6 182 212 / 0.3)",
                "xl": "0 16px 32px -8px rgb(6 182 212 / 0.4)"
            },
            "animations": {
                "duration_fast": "200ms",
                "duration_normal": "350ms",
                "duration_slow": "600ms",
                "easing": "cubic-bezier(0.34, 1.56, 0.64, 1)"
            }
        }
    
    def _get_corporate_theme(self) -> Dict[str, Any]:
        """Conservative corporate theme with navy and gold."""
        return {
            "name": "Corporate",
            "description": "Professional corporate theme with navy and gold accents",
            "colors": {
                "primary": "#1E3A8A",      # Navy blue
                "secondary": "#1E40AF",    # Blue
                "accent": "#D97706",       # Gold/orange
                "success": "#065F46",      # Dark green
                "warning": "#92400E",      # Dark orange
                "error": "#991B1B",        # Dark red
                "background": "#FFFFFF",
                "surface": "#F8FAFC",
                "text": "#1E3A8A",
                "text_secondary": "#64748B",
                "border": "#CBD5E1"
            },
            "fonts": {
                "heading": "'Playfair Display', Georgia, serif",
                "body": "'Source Sans Pro', sans-serif",
                "mono": "'Source Code Pro', monospace"
            },
            "typography": {
                "h1_size": "5rem",
                "h1_weight": "700",
                "h2_size": "3.5rem",
                "h2_weight": "600",
                "h3_size": "2.5rem", 
                "h3_weight": "600",
                "body_size": "1.25rem",
                "body_line_height": "1.8"
            },
            "spacing": {
                "xs": "0.75rem",
                "sm": "1.25rem",
                "md": "2rem",
                "lg": "3rem",
                "xl": "4rem",
                "2xl": "5rem",
                "3xl": "7rem"
            },
            "shadows": {
                "sm": "0 2px 4px 0 rgb(30 58 138 / 0.1)",
                "md": "0 4px 8px 0 rgb(30 58 138 / 0.15)",
                "lg": "0 8px 16px 0 rgb(30 58 138 / 0.2)",
                "xl": "0 16px 32px 0 rgb(30 58 138 / 0.25)"
            },
            "animations": {
                "duration_fast": "200ms",
                "duration_normal": "400ms",
                "duration_slow": "600ms",
                "easing": "ease-in-out"
            }
        }
    
    def _get_creative_theme(self) -> Dict[str, Any]:
        """Creative theme with vibrant colors and playful typography."""
        return {
            "name": "Creative",
            "description": "Vibrant creative theme with playful gradients",
            "colors": {
                "primary": "#7C3AED",      # Purple
                "secondary": "#C084FC",    # Light purple
                "accent": "#F59E0B",       # Orange
                "success": "#10B981",      # Green
                "warning": "#F59E0B",      # Orange
                "error": "#EF4444",        # Red
                "background": "#FFFFFF",
                "surface": "#FAF5FF",      # Purple tint
                "text": "#581C87",         # Dark purple
                "text_secondary": "#7C2D12", # Brown
                "border": "#DDD6FE"        # Light purple
            },
            "fonts": {
                "heading": "'Poppins', sans-serif",
                "body": "'Nunito', sans-serif", 
                "mono": "'JetBrains Mono', monospace"
            },
            "typography": {
                "h1_size": "4.5rem",
                "h1_weight": "800",
                "h2_size": "3.25rem",
                "h2_weight": "700",
                "h3_size": "2.5rem",
                "h3_weight": "600",
                "body_size": "1.25rem",
                "body_line_height": "1.75"
            },
            "spacing": {
                "xs": "0.5rem",
                "sm": "1rem",
                "md": "1.75rem",
                "lg": "2.5rem",
                "xl": "3.5rem",
                "2xl": "5rem",
                "3xl": "7rem"
            },
            "shadows": {
                "sm": "0 4px 6px -1px rgb(124 58 237 / 0.1)",
                "md": "0 8px 12px -2px rgb(124 58 237 / 0.15)",
                "lg": "0 16px 24px -4px rgb(124 58 237 / 0.2)",
                "xl": "0 24px 48px -8px rgb(124 58 237 / 0.25)"
            },
            "animations": {
                "duration_fast": "150ms",
                "duration_normal": "300ms",
                "duration_slow": "500ms",
                "easing": "cubic-bezier(0.68, -0.55, 0.265, 1.55)"
            }
        }
    
    def _get_dark_theme(self) -> Dict[str, Any]:
        """Dark theme with high contrast and blue accents."""
        return {
            "name": "Dark",
            "description": "Professional dark theme with high contrast",
            "colors": {
                "primary": "#F9FAFB",      # Light gray
                "secondary": "#D1D5DB",    # Medium gray
                "accent": "#60A5FA",       # Light blue
                "success": "#34D399",      # Light green
                "warning": "#FBBF24",      # Light yellow
                "error": "#F87171",        # Light red
                "background": "#111827",   # Dark gray
                "surface": "#1F2937",      # Slightly lighter
                "text": "#F9FAFB",         # Light gray
                "text_secondary": "#9CA3AF", # Medium gray
                "border": "#374151"        # Dark border
            },
            "fonts": {
                "heading": "'Inter', sans-serif",
                "body": "'Inter', sans-serif",
                "mono": "'Fira Code', monospace"
            },
            "typography": {
                "h1_size": "4.5rem",
                "h1_weight": "800",
                "h2_size": "3rem",
                "h2_weight": "700",
                "h3_size": "2.25rem",
                "h3_weight": "600",
                "body_size": "1.25rem",
                "body_line_height": "1.8"
            },
            "spacing": {
                "xs": "0.5rem",
                "sm": "1rem",
                "md": "1.5rem",
                "lg": "2rem",
                "xl": "3rem",
                "2xl": "4rem",
                "3xl": "6rem"
            },
            "shadows": {
                "sm": "0 1px 2px 0 rgb(0 0 0 / 0.3)",
                "md": "0 4px 6px -1px rgb(0 0 0 / 0.4)",
                "lg": "0 10px 15px -3px rgb(0 0 0 / 0.5)",
                "xl": "0 20px 25px -5px rgb(0 0 0 / 0.6)"
            },
            "animations": {
                "duration_fast": "150ms",
                "duration_normal": "300ms",
                "duration_slow": "500ms",
                "easing": "cubic-bezier(0.4, 0, 0.2, 1)"
            }
        }


# Global theme registry instance
theme_registry = ThemeRegistry()