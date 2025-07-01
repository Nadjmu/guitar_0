import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse
from music_theory import string_notes
notes_color = [
    # Original reds (slightly adjusted for better contrast on gold)
    (0.65, 0.10, 0.18),    # Deep burgundy
    (0.72, 0.18, 0.26),    # Rich red
    (0.78, 0.25, 0.32),    # Medium red
    
    # Darker variations that contrast well with gold
    (0.58, 0.08, 0.15),    # Very deep burgundy
    (0.68, 0.12, 0.20),    # Dark wine
    (0.75, 0.15, 0.25),    # Dark red
    
    # Warmer, slightly desaturated variations
    (0.70, 0.20, 0.22),    # Reddish brown
    (0.72, 0.22, 0.24),    # Warm burgundy
    (0.74, 0.24, 0.26),    # Soft red
    
    # Lighter variations that maintain contrast
    (0.76, 0.26, 0.30),    # Medium-light red
    (0.80, 0.30, 0.34),    # Light red
    (0.82, 0.32, 0.36)     # Very light red
]

def draw_fretboard(show_notes=True, highlighted_notes=[[0,0]]):
    chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'bB', 'B']
    
    # Define color mapping based on the last entry
    color_mapping = {
        0: (0.65, 0.10, 0.18, 1.0),    # Deep burgundy (original color for index 0)
        1: (0.72, 0.18, 0.26, 1.0),     # Rich red (original color for index 1)
        2: (0.78, 0.25, 0.32, 1.0),     # Medium red (original color for index 2)
        3: (0.2, 0.4, 1.0, 0.7),        # Light transparent blue
        4: (0.4, 0.8, 0.2, 0.7),        # Light transparent green
        5: (0.6, 0.2, 0.8, 0.7)         # Light transparent purple
    }
    
    fig, ax = plt.subplots(figsize=(10, 1.5), facecolor='black')
    num_frets = 12
    num_strings = 6

    # Draw the strings
    for string in range(num_strings):
        ax.plot([0, num_frets], [string, string], color=(0.8, 0.643, 0.0), lw=4)

    # Draw the frets
    ax.plot([0, 0], [-0.5, 5.5], color='white', lw=2)
    for fret in range(1, num_frets + 1):
        ax.plot([fret, fret], [-0.5, 5.5], color=(0.6, 0.482, 0.0), lw=2)

    # Draw fret markers
    for i in range(5):
        circle = Ellipse((2.5+2*i, 2.5), width=0.05, height=0.1, color='white', edgecolor='black')
        ax.add_patch(circle)

    # Add note labels
    if show_notes:
        for string in range(6):
            start_note = string_notes[string]
            start_index = chromatic_scale.index(start_note)
            for fret in range(num_frets + 1):
                note_index = (start_index + fret) % 12 
                note = chromatic_scale[note_index]    
                ax.text(fret-0.2, string, note, color='white', ha='center', va='center', 
                        fontweight='bold', alpha=0.5, zorder=4)
    
    # Add highlighted notes with color based on last entry
    for highlighted_note in highlighted_notes:
        highlight_fret = highlighted_note[0]
        highlight_string = highlighted_note[1]
        highlight_width = 0.38
        highlight_height = 0.3
        
        # Get color index (default to 0 if not specified)
        color_idx = highlighted_note[2] if len(highlighted_note) > 2 else 0
        
        # Get color from mapping (default to first color if not found)
        note_color = color_mapping.get(color_idx, color_mapping[0])
        
        ax.add_patch(Rectangle(
            (highlight_fret-highlight_width, highlight_string - highlight_height/2),
            highlight_width-0.025, 
            highlight_height,
            color=note_color,
            alpha=note_color[3],  # Use alpha from the color tuple
            zorder=3
        ))

    ax.set_ylim(-0.5, 5.5)
    ax.axis('off')
    
    return fig

#chord1=[[0,0],[1,1],[3,4]]
#a_minor = [[0,1],[2,2],[2,3],[1,4],[0,5]]
#draw_fretboard(show_notes=True,chord = a_minor)
#plt.show()