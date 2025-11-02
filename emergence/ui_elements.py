"""
UI elements for EMERGENCE terminal interface.

Provides box-drawing utilities, panel layouts, borders, and UI components
using Unicode box-drawing characters and styled text.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class BoxStyle(Enum):
    """Box drawing styles."""
    LIGHT = "light"
    HEAVY = "heavy"
    DOUBLE = "double"
    MIXED = "mixed"
    ROUNDED = "rounded"


@dataclass
class BoxChars:
    """Box drawing characters for a specific style."""
    tl: str  # top-left
    tr: str  # top-right
    bl: str  # bottom-left
    br: str  # bottom-right
    h: str   # horizontal
    v: str   # vertical
    lt: str  # left tee
    rt: str  # right tee
    t: str   # top tee
    b: str   # bottom tee
    c: str   # cross


class BoxDrawing:
    """Box drawing character sets."""
    
    LIGHT = BoxChars(
        tl='┌', tr='┐', bl='└', br='┘',
        h='─', v='│',
        lt='├', rt='┤', t='┬', b='┴', c='┼'
    )
    
    HEAVY = BoxChars(
        tl='┏', tr='┓', bl='┗', br='┛',
        h='━', v='┃',
        lt='┣', rt='┫', t='┳', b='┻', c='╋'
    )
    
    DOUBLE = BoxChars(
        tl='╔', tr='╗', bl='╚', br='╝',
        h='═', v='║',
        lt='╠', rt='╣', t='╦', b='╩', c='╬'
    )
    
    ROUNDED = BoxChars(
        tl='╭', tr='╮', bl='╰', br='╯',
        h='─', v='│',
        lt='├', rt='┤', t='┬', b='┴', c='┼'
    )
    
    @classmethod
    def get_style(cls, style: BoxStyle) -> BoxChars:
        """Get box characters for a style."""
        if style == BoxStyle.LIGHT:
            return cls.LIGHT
        elif style == BoxStyle.HEAVY:
            return cls.HEAVY
        elif style == BoxStyle.DOUBLE:
            return cls.DOUBLE
        elif style == BoxStyle.ROUNDED:
            return cls.ROUNDED
        else:
            return cls.LIGHT
    
    @classmethod
    def draw_box(cls, width: int, height: int, style: BoxStyle = BoxStyle.LIGHT, 
                 title: Optional[str] = None) -> List[str]:
        """Draw a box with optional title."""
        b = cls.get_style(style)
        lines = []
        
        # Top border
        if title:
            title_text = f" {title} "
            if len(title_text) > width - 4:
                title_text = title_text[:width-7] + "... "
            title_pad_left = (width - len(title_text) - 2) // 2
            title_pad_right = width - len(title_text) - title_pad_left - 2
            top = b.tl + b.h * title_pad_left + title_text + b.h * title_pad_right + b.tr
        else:
            top = b.tl + b.h * (width - 2) + b.tr
        lines.append(top)
        
        # Middle
        for _ in range(height - 2):
            lines.append(b.v + ' ' * (width - 2) + b.v)
        
        # Bottom
        lines.append(b.bl + b.h * (width - 2) + b.br)
        return lines
    
    @classmethod
    def draw_separator(cls, width: int, style: BoxStyle = BoxStyle.LIGHT, 
                      left_connect: bool = True, right_connect: bool = True) -> str:
        """Draw a horizontal separator line."""
        b = cls.get_style(style)
        left = b.lt if left_connect else b.h
        right = b.rt if right_connect else b.h
        return left + b.h * (width - 2) + right
    
    @classmethod
    def draw_vertical_separator(cls, height: int, style: BoxStyle = BoxStyle.LIGHT) -> List[str]:
        """Draw a vertical separator."""
        b = cls.get_style(style)
        return [b.v] * height
    
    @classmethod
    def draw_border_top(cls, width: int, style: BoxStyle = BoxStyle.LIGHT, 
                       title: Optional[str] = None) -> str:
        """Draw top border."""
        b = cls.get_style(style)
        if title:
            title_text = f" {title} "
            if len(title_text) > width - 4:
                title_text = title_text[:width-7] + "... "
            title_pad_left = (width - len(title_text) - 2) // 2
            title_pad_right = width - len(title_text) - title_pad_left - 2
            return b.tl + b.h * title_pad_left + title_text + b.h * title_pad_right + b.tr
        return b.tl + b.h * (width - 2) + b.tr
    
    @classmethod
    def draw_border_bottom(cls, width: int, style: BoxStyle = BoxStyle.LIGHT) -> str:
        """Draw bottom border."""
        b = cls.get_style(style)
        return b.bl + b.h * (width - 2) + b.br
    
    @classmethod
    def draw_border_sides(cls, width: int, content: str = '', 
                          style: BoxStyle = BoxStyle.LIGHT) -> str:
        """Draw left and right borders with content."""
        b = cls.get_style(style)
        content_width = width - 2
        
        # Pad or truncate content
        if len(content) > content_width:
            content = content[:content_width-3] + '...'
        else:
            content = content + ' ' * (content_width - len(content))
        
        return b.v + content + b.v


class PanelLayout:
    """Predefined panel layouts."""
    
    @staticmethod
    def split_horizontal(width: int, height: int, left_width: int, 
                        style: BoxStyle = BoxStyle.DOUBLE) -> List[str]:
        """Create a split-pane layout (left/right)."""
        b = BoxDrawing.get_style(style)
        lines = []
        
        right_width = width - left_width - 1
        
        # Top border
        top = (b.tl + b.h * (left_width - 2) + b.t + 
               b.h * (right_width - 1) + b.tr)
        lines.append(top)
        
        # Content area
        for _ in range(height - 2):
            line = (b.v + ' ' * (left_width - 2) + b.v + 
                   ' ' * (right_width - 1) + b.v)
            lines.append(line)
        
        # Bottom border
        bottom = (b.bl + b.h * (left_width - 2) + b.b + 
                 b.h * (right_width - 1) + b.br)
        lines.append(bottom)
        
        return lines
    
    @staticmethod
    def split_vertical(width: int, top_height: int, bottom_height: int,
                      style: BoxStyle = BoxStyle.DOUBLE) -> List[str]:
        """Create a split-pane layout (top/bottom)."""
        b = BoxDrawing.get_style(style)
        lines = []
        
        # Top section
        lines.append(b.tl + b.h * (width - 2) + b.tr)
        for _ in range(top_height - 1):
            lines.append(b.v + ' ' * (width - 2) + b.v)
        
        # Separator
        lines.append(b.lt + b.h * (width - 2) + b.rt)
        
        # Bottom section
        for _ in range(bottom_height - 1):
            lines.append(b.v + ' ' * (width - 2) + b.v)
        lines.append(b.bl + b.h * (width - 2) + b.br)
        
        return lines
    
    @staticmethod
    def three_column(width: int, height: int, col1_width: int, col2_width: int,
                    style: BoxStyle = BoxStyle.DOUBLE) -> List[str]:
        """Create a three-column layout."""
        b = BoxDrawing.get_style(style)
        lines = []
        
        col3_width = width - col1_width - col2_width - 3
        
        # Top border
        top = (b.tl + b.h * (col1_width - 1) + b.t + 
               b.h * (col2_width - 1) + b.t + 
               b.h * (col3_width - 1) + b.tr)
        lines.append(top)
        
        # Content area
        for _ in range(height - 2):
            line = (b.v + ' ' * (col1_width - 1) + b.v + 
                   ' ' * (col2_width - 1) + b.v + 
                   ' ' * (col3_width - 1) + b.v)
            lines.append(line)
        
        # Bottom border
        bottom = (b.bl + b.h * (col1_width - 1) + b.b + 
                 b.h * (col2_width - 1) + b.b + 
                 b.h * (col3_width - 1) + b.br)
        lines.append(bottom)
        
        return lines
    
    @staticmethod
    def dashboard_layout(width: int, height: int) -> str:
        """Create the main dashboard layout with header, world view, status panel, log, and command."""
        b = BoxDrawing.get_style(BoxStyle.DOUBLE)
        lines = []
        
        # Calculate dimensions
        header_height = 2
        log_height = 4
        command_height = 3
        world_height = height - header_height - log_height - command_height - 4
        status_width = int(width * 0.3)
        world_width = width - status_width - 1
        
        # Top border with title
        lines.append(b.tl + b.h * (width - 2) + b.tr)
        lines.append(b.v + " EMERGENCE - Gen: 47 | Pop: 87 | Fit: 847 | EP: 234".ljust(width - 2) + b.v)
        lines.append(b.lt + b.h * (world_width - 2) + b.t + b.h * (status_width - 1) + b.rt)
        
        # World view and status panel header
        lines.append(b.v + " 🌍 WORLD VIEW (70%)".ljust(world_width - 2) + b.v + 
                    " 📊 STATUS PANEL (30%)".ljust(status_width - 1) + b.v)
        lines.append(b.v + ' ' * (world_width - 2) + b.v + ' ' * (status_width - 1) + b.v)
        
        # World and status content area
        for _ in range(world_height - 4):
            lines.append(b.v + ' ' * (world_width - 2) + b.v + ' ' * (status_width - 1) + b.v)
        
        # Separator before log
        lines.append(b.lt + b.h * (width - 2) + b.rt)
        lines.append(b.v + " 📜 MESSAGE LOG".ljust(width - 2) + b.v)
        lines.append(b.lt + b.h * (width - 2) + b.rt)
        
        # Log area
        for _ in range(log_height - 1):
            lines.append(b.v + ' ' * (width - 2) + b.v)
        
        # Command input separator
        lines.append(b.lt + b.h * (width - 2) + b.rt)
        lines.append(b.v + " 💬 Command: _".ljust(width - 2) + b.v)
        lines.append(b.bl + b.h * (width - 2) + b.br)
        
        return '\n'.join(lines)


class UIComponents:
    """Common UI components."""
    
    @staticmethod
    def create_menu(items: List[str], selected: int = 0, width: int = 25) -> List[str]:
        """Create a menu with selectable items."""
        lines = []
        lines.append(BoxDrawing.draw_border_top(width, BoxStyle.LIGHT, "MAIN MENU"))
        
        for i, item in enumerate(items):
            prefix = '▸ ' if i == selected else '  '
            content = f" {prefix}{item}".ljust(width - 2)
            lines.append(BoxDrawing.draw_border_sides(width, content))
        
        lines.append(BoxDrawing.draw_border_bottom(width))
        return lines
    
    @staticmethod
    def create_progress_bar(label: str, value: float, max_value: float = 100.0, 
                           width: int = 20, bar_width: int = 10) -> str:
        """Create a labeled progress bar."""
        ratio = min(1.0, max(0.0, value / max_value))
        filled = int(ratio * bar_width)
        empty = bar_width - filled
        bar = '█' * filled + '░' * empty
        percentage = f"{value:.0f}/{max_value:.0f}"
        return f"{label}: {bar} {percentage}"
    
    @staticmethod
    def create_stat_panel(title: str, stats: Dict[str, str], width: int = 30) -> List[str]:
        """Create a panel with statistics."""
        lines = []
        lines.append(BoxDrawing.draw_border_top(width, BoxStyle.HEAVY, title))
        
        for key, value in stats.items():
            content = f" {key}: {value}".ljust(width - 2)
            lines.append(BoxDrawing.draw_border_sides(width, content, BoxStyle.HEAVY))
        
        lines.append(BoxDrawing.draw_border_bottom(width, BoxStyle.HEAVY))
        return lines
    
    @staticmethod
    def create_tabs(tabs: List[str], active: int = 0, width: int = 80) -> str:
        """Create a tab bar."""
        b = BoxDrawing.get_style(BoxStyle.DOUBLE)
        tab_line = b.tl + b.h
        
        for i, tab in enumerate(tabs):
            if i == active:
                tab_line += f"[{tab}]"
            else:
                tab_line += f" {tab} "
            
            if i < len(tabs) - 1:
                tab_line += b.h
        
        # Fill remaining width
        current_len = len(tab_line)
        if current_len < width - 1:
            tab_line += b.h * (width - current_len - 1)
        
        tab_line += b.tr
        return tab_line
    
    @staticmethod
    def create_command_palette(width: int = 80, prompt: str = "> ", 
                              suggestions: Optional[List[str]] = None) -> List[str]:
        """Create a command palette with autocomplete suggestions."""
        b = BoxDrawing.get_style(BoxStyle.DOUBLE)
        lines = []
        
        # Top border
        header_text = " 💬 Command Palette"
        help_text = "[Ctrl+P to close]"
        padding = width - len(header_text) - len(help_text) - 4
        top = b.tl + b.h * (width - 2) + b.tr
        lines.append(top)
        
        header = b.v + header_text + ' ' * padding + help_text + ' ' + b.v
        lines.append(header)
        
        lines.append(b.lt + b.h * (width - 2) + b.rt)
        
        # Command input
        input_line = b.v + f" {prompt}".ljust(width - 2) + b.v
        lines.append(input_line)
        
        # Suggestions
        if suggestions:
            for suggestion in suggestions[:5]:  # Limit to 5 suggestions
                sug_text = f"   ▸ {suggestion}"
                if len(sug_text) < width - 2:
                    sug_text += " " * (width - len(sug_text) - 2)
                lines.append(b.v + sug_text + b.v)
        
        # Bottom border
        lines.append(b.bl + b.h * (width - 2) + b.br)
        return lines
    
    @staticmethod
    def create_hud_panel(title: str, content: List[Tuple[str, str]], 
                        width: int = 25) -> List[str]:
        """Create a HUD-style panel with key-value pairs."""
        lines = []
        lines.append(BoxDrawing.draw_border_top(width, BoxStyle.HEAVY, title))
        
        for key, value in content:
            line = f" {key}: {value}".ljust(width - 2)
            lines.append(BoxDrawing.draw_border_sides(width, line, BoxStyle.HEAVY))
        
        lines.append(BoxDrawing.draw_border_bottom(width, BoxStyle.HEAVY))
        return lines
    
    @staticmethod
    def create_tooltip(text: str, width: int = 40) -> List[str]:
        """Create a tooltip box."""
        lines = []
        b = BoxDrawing.get_style(BoxStyle.LIGHT)
        
        # Wrap text to fit width
        words = text.split()
        current_line = ""
        wrapped_lines = []
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width - 4:
                current_line += word + " "
            else:
                wrapped_lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            wrapped_lines.append(current_line.strip())
        
        # Create box
        lines.append(b.tl + b.h * (width - 2) + b.tr)
        
        for line in wrapped_lines:
            content = f" {line}".ljust(width - 2)
            lines.append(b.v + content + b.v)
        
        lines.append(b.bl + b.h * (width - 2) + b.br)
        return lines


class AsciiArt:
    """Pre-made ASCII art scenes."""
    
    LOGO = [
        "███████╗███╗   ███╗███████╗██████╗  ██████╗ ███████╗███╗   ██╗ ██████╗███████╗",
        "██╔════╝████╗ ████║██╔════╝██╔══██╗██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔════╝",
        "█████╗  ██╔████╔██║█████╗  ██████╔╝██║  ███╗█████╗  ██╔██╗ ██║██║     █████╗  ",
        "██╔══╝  ██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██║╚██╗██║██║     ██╔══╝  ",
        "███████╗██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝███████╗██║ ╚████║╚██████╗███████╗",
        "╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝"
    ]
    
    MINI_LOGO = [
        "╔═══════════════════════════╗",
        "║   E M E R G E N C E      ║",
        "║   AI Ecosystem Simulator  ║",
        "╚═══════════════════════════╝"
    ]
    
    @staticmethod
    def center_text(text: str, width: int) -> str:
        """Center text within a given width."""
        padding = (width - len(text)) // 2
        return ' ' * padding + text
    
    @staticmethod
    def center_art(art: List[str], width: int) -> List[str]:
        """Center multi-line ASCII art."""
        max_line_len = max(len(line) for line in art)
        padding = (width - max_line_len) // 2
        return [' ' * padding + line for line in art]


def create_full_interface(width: int = 120, height: int = 40) -> str:
    """Create the full EMERGENCE interface layout."""
    return PanelLayout.dashboard_layout(width, height)
