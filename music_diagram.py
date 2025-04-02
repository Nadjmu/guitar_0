import matplotlib.pyplot as plt
from matplotlib import use
#use('WebAgg')
import numpy as np
import matplotlib.image as mpimg

# Mapping of musical notes to y-axis positions (approximate for a staff)
note_positions = {
    "C0": -3.5, "Db": -0.5, "D0": -0.5, "Eb": 0, "E0": 0, "F0": 6.5,
    "Gb": 0.5, "G0": 1.0, "Ab": 2, "A0": 2.5, "Bb": 3, "B0": 3.5, "C1": 4
}

def draw_music_diagram(notes, clef_image_path):
    fig, ax = plt.subplots(figsize=(6, 3))
    diagram_length = 10
    # Draw staff lines
    for i in range(5):
        ax.hlines(y=i, xmin=0.5, xmax=1+diagram_length, color='black', linewidth=1.8)
    
    # Load and display treble clef image
    clef_img = mpimg.imread(clef_image_path)
    ax.imshow(clef_img, aspect='auto', extent=[-0.8, 0.6, -1.74, 5.44])  # Adjust position and size
    
    # Plot quarter notes at discrete x positions
    x_positions = np.linspace(1, len(notes), len(notes))
    print(x_positions)
    note_size = 150  # Adjusted for proper size relative to staff
    for x_o, note in zip(x_positions, notes):
        if note in note_positions:
            y = note_positions[note]
            x = 1+ (x_o-1)*diagram_length/(len(notes)-1)*0.35
            print(x)
            ax.scatter(x, y, color='black', s=note_size, marker='o')  # Larger note head
            ax.plot([x + 0.13, x + 0.13], [y, y + 3], color='black', linewidth=1.5)  # Adjusted Stem
            if y < -0.5:
                for i in range(3):
                    helper_line_y = -i-1
                    if helper_line_y >= y:
                        ax.plot([x - 0.25, x + 0.25], [helper_line_y, helper_line_y], color='black', linewidth=1.8)  # Adjusted Stem
            if y > 4.5:
                for i in range(2):
                    helper_line_y = 5+i
                    if helper_line_y <= y:
                        ax.plot([x - 0.25, x + 0.25], [helper_line_y, helper_line_y], color='black', linewidth=1.8)  # Adjusted Stem

    # Formatting
    #ax.set_xticks(range(1, len(notes) + 1))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1, 5.5)  # Adjusted to make space for clef
    ax.set_ylim(-6, 8)
    ax.set_frame_on(False)
    ax.set_xticklabels([])
    
    return fig

# Define notes
notes = ["C0", "E0", "F0"]
clef_image_path = "clef.png"  # Path to uploaded clef image

# Plot the music diagram
fig = draw_music_diagram(notes, clef_image_path)
plt.show()
