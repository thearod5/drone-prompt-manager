import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET

woods_color = '#8A9A5B' # Color for woods
water_color = '#A0BCC2' ##6D8390'    # Color for water
launch_pad_color = '#404040' # Black for launch pad
battery_charging_color = '#909090' # Gray for battery charging

num_rows = 16
num_cols = 28
cell_size = 40

# Dictionary to hold button references
buttons = {}


# Global variable to keep track of the current terrain type
current_terrain_type = None

# Updated terrain_blocks dictionary
terrain_blocks = {
    'Woodland': set(), 
    'Waterway': set(), 
    'LaunchPad': set(), 
    'BatteryCharging': set()
}


def get_adjacent_cells(row, col):
    """ Returns a list of adjacent cells (up, down, left, right) within the grid bounds. """
    adjacent = []
    for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
        new_row, new_col = row + d_row, col + d_col
        if 0 <= new_row < num_rows and 0 <= new_col < num_cols:
            adjacent.append((new_row, new_col))
    return adjacent

def dfs(row, col, terrain_type, visited):
    """ Perform Depth-First Search to find all connected cells of the same type. """
    visited.add((row, col))
    component = {(row, col)}
    for (adj_row, adj_col) in get_adjacent_cells(row, col):
        if (adj_row, adj_col) not in visited and is_terrain_type(adj_row, adj_col, terrain_type):
            component |= dfs(adj_row, adj_col, terrain_type, visited)
    return component

def is_terrain_type(row, col, terrain_type):
    """ Check if the cell at (row, col) is of the given terrain type. """
    cell_label = f'{row_to_letter(row)}{col + 1}'
    return cell_label in terrain_blocks[terrain_type]

def identify_separate_blocks():
    separate_blocks = {
        'Woodland': [], 
        'Waterway': [], 
        'LaunchPad': [], 
        'BatteryCharging': []
    }
    visited = set()

    for terrain_type in separate_blocks.keys():
        for row in range(num_rows):
            for col in range(num_cols):
                if (row, col) not in visited and is_terrain_type(row, col, terrain_type):
                    component = dfs(row, col, terrain_type, visited)
                    separate_blocks[terrain_type].append(component)

    return separate_blocks



def open_terrain_file():
    filename = filedialog.askopenfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
    if filename:
        return filename
    else:
        # Handle case where the user does not select a file
        return None

# Function to handle terrain button clicks
def set_terrain_type(terrain_type):
    global current_terrain_type
    current_terrain_type = terrain_type

    # Update button colors
    for btn_text, btn in buttons.items():
        if btn_text == terrain_type:
            btn.config(highlightbackground='gray', highlightthickness=2)
        else:
            btn.config(highlightbackground='white', highlightthickness=0)

def parse_terrain_file(filename):
    terrain_dict = {}
    tree = ET.parse(filename)
    root = tree.getroot()
    for terrain in root.findall('terrain'):
        type = terrain.find('type').text
        blocks = terrain.find('blocks').text.split(',')
        terrain_dict[type] = terrain_dict.get(type, []) + blocks

        # Also populate the terrain_blocks dictionary for modification
        for block in blocks:
            terrain_blocks[type].add(block)

    return terrain_dict

def color_terrain(terrain_dict):
    terrain_colors = {
        'Woodland': woods_color,
        'Waterway': water_color,
        'LaunchPad': launch_pad_color,
        'BatteryCharging': battery_charging_color
    }
    
    for terrain_type, blocks in terrain_dict.items():
        color = terrain_colors.get(terrain_type, 'white')
        for block in blocks:
            row = ord(block[0]) - 65
            column = int(block[1:]) - 1
            if (row, column) in cells:
                canvas.itemconfig(cells[(row, column)], fill=color)


def on_cell_click(event):
    # Calculate row and column from mouse position
    row = event.y // cell_size
    column = event.x // cell_size
    cell_label = f'{row_to_letter(row)}{column + 1}'

    if current_terrain_type:
        # Define a mapping from terrain types to their colors
        terrain_color_map = {
            'Woodland': woods_color,
            'Waterway': water_color,
            'LaunchPad': launch_pad_color,
            'BatteryCharging': battery_charging_color
        }
        
        # Update the cell color based on the current terrain type
        fill_color = terrain_color_map.get(current_terrain_type, 'white')
        canvas.itemconfig(cells[(row, column)], fill=fill_color)
        
        # Add the cell to the appropriate set in the terrain_blocks dictionary
        terrain_blocks[current_terrain_type].add(cell_label)


def blocks_to_text_format(blocks):
    formatted_blocks = []
    for block in blocks:
        formatted_block = ','.join(sorted([f'{row_to_letter(row)}{col + 1}' for row, col in block]))
        formatted_blocks.append(formatted_block)
    return formatted_blocks
    
def save_terrain_to_file():
    filename = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
    if filename:
        root = ET.Element('terrains')

    # Ensure that separate_blocks include new terrain types
    separate_blocks = identify_separate_blocks()

    for terrain_type, blocks in separate_blocks.items():
        for block in blocks:
            formatted_block = blocks_to_text_format([block])[0]
            if formatted_block:
                terrain = ET.SubElement(root, 'terrain')
                ET.SubElement(terrain, 'type').text = terrain_type
                ET.SubElement(terrain, 'blocks').text = formatted_block


    tree = ET.ElementTree(root)
    tree.write(filename)

# Create the main window
root = tk.Tk()
root.title("Scene Builder for SMP Tests")

# Create a frame for the grid canvas
canvas_frame = tk.Frame(root)
canvas_frame.grid(row=0, column=0, sticky='nsew')

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, sticky='ew')

# Configure the main window to give all space to canvas_frame
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Canvas for the grid
canvas = tk.Canvas(canvas_frame, width=num_cols*cell_size, height=num_rows*cell_size)
canvas.pack(expand=True, fill='both')

# Add terrain type buttons in button_frame
# btn_woodland = tk.Button(button_frame, text="Woodlands", command=lambda: set_terrain_type('Woodland'))
# btn_woodland.pack(side='left', expand=True, fill='x')
buttons['Woodland'] = tk.Button(button_frame, text="Woodland", command=lambda: set_terrain_type('Woodland'))
buttons['Woodland'].pack(side='left', expand=True, fill='x')

buttons['Waterway'] = tk.Button(button_frame, text="Waterway", command=lambda: set_terrain_type('Waterway'))
buttons['Waterway'].pack(side='left', expand=True, fill='x')

# Add new buttons for Launch Pad and Battery Charging in button_frame
buttons['LaunchPad']= tk.Button(button_frame, text="LaunchPad", command=lambda: set_terrain_type('LaunchPad'))
buttons['LaunchPad'].pack(side='left', expand=True, fill='x')

buttons['BatteryCharging'] = tk.Button(button_frame, text="BatteryCharging", command=lambda: set_terrain_type('BatteryCharging'))
buttons['BatteryCharging'].pack(side='left', expand=True, fill='x')

# Add a save button in button_frame
btn_save = tk.Button(button_frame, text="Save Terrain Data", command=save_terrain_to_file)
btn_save.pack(side='left', expand=True, fill='x')

# Canvas for the grid
#cell_size = 40
canvas = tk.Canvas(root, width=num_cols*cell_size, height=num_rows*cell_size)
canvas.grid(row=0, column=0)

# Function to convert row number to letter (e.g., 0 -> A, 1 -> B, etc.)
def row_to_letter(row):
    return chr(row + 65)

   
# Create rectangles and labels for the grid
cells = {}
for r in range(num_rows):  # Rows A-H
    for c in range(num_cols):  # Columns 1-14
        x1, y1 = c * cell_size, r * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size
        rect = canvas.create_rectangle(x1, y1, x2, y2, fill='white')
        cells[(r, c)] = rect
        # Create a label for the cell (e.g., A1, A2, ...)
        label = f'{row_to_letter(r)}{c + 1}'
        canvas.create_text(x1 + 20, y1 + 20, text=label, fill='black')

# At the start of your main code
terrain_file = open_terrain_file()
if terrain_file:
    terrain_dict = parse_terrain_file(terrain_file)
    color_terrain(terrain_dict)

# Bind the cell click event
canvas.bind("<Button-1>", on_cell_click)

root.mainloop()



