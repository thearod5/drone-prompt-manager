import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET

# Define colors for terrains
woods_color = '#8A9A5B'
water_color = '#A0BCC2'
launch_pad_color = '#404040'
battery_charging_color = '#909090'

# Grid dimensions
num_rows = 16
num_cols = 28
cell_size = 40

def reset_recharge_counters():
    for drone_id in recharge_counters.keys():
        recharge_counters[drone_id] = 0
# Function to convert row number to letter
def row_to_letter(row):
    return chr(row + 65)


def label_cell(cell, drone_id, color):
    x, y = get_cell_center(cell)
    drone_counters[drone_id] += 1
    label_text = f"{drone_id[0].upper()}{drone_counters[drone_id]}"  # E.g., "Y1", "B2"
    canvas.create_text(x, y + 15, text=label_text, fill=color, font=('Helvetica', '9', 'bold'))  # Adjusted to place below the cell ID

def get_cell_center(cell_label):
    row = ord(cell_label[0]) - 65
    column = int(cell_label[1:]) - 1
    x = (column * cell_size) + (cell_size / 2)
    y = (row * cell_size) + (cell_size / 2)
    return x, y
    
def draw_arrow(from_cell, to_cell, color):
    # Calculate the center of the from and to cells
    from_x, from_y = get_cell_center(from_cell)
    to_x, to_y = get_cell_center(to_cell)
    canvas.create_line(from_x, from_y, to_x, to_y, arrow=tk.LAST, fill=color)



    
# Function to color the terrain based on XML data
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
    
def parse_terrain_file(filename):
    terrain_dict = {'Woodland': [], 'Waterway': [], 'LaunchPad': [], 'BatteryCharging': []}

    tree = ET.parse(filename)
    root = tree.getroot()
    for terrain in root.findall('terrain'):
        type = terrain.find('type').text
        blocks = terrain.find('blocks').text.split(',')

        # Append blocks to the list for each terrain type
        if type in terrain_dict:
            terrain_dict[type].extend(blocks)
        else:
            terrain_dict[type] = blocks

    return terrain_dict
    
def parse_drone_flights(filename):
    drone_flights = {}
    drone_colors = {}

    tree = ET.parse(filename)
    root = tree.getroot()
    for drone in root.findall('drone'):
        drone_id = drone.find('id').text
        flights = []
        for flight in drone.findall('flight'):
            actions = [action.text for action in flight if action.text is not None]
            flights.append(actions)
        drone_flights[drone_id] = flights

        # Use drone ID as color (converted to lowercase)
        drone_colors[drone_id] = drone_id.lower()

    print()
    print(drone_flights,drone_colors)
    print()
    return drone_flights, drone_colors
    
# Function to open the file dialog and return the selected filename
def open_terrain_file():
    filename = filedialog.askopenfilename(title="Open TERRAIN File", 
                                          filetypes=[("XML files", "*.xml")])
    return filename
    
# Function to open the file dialog and return the selected filename
def open_droneflight_file():
    filename = filedialog.askopenfilename(title="Open DRONE FLIGHT File", 
                                          filetypes=[("XML files", "*.xml")])
    return filename

current_step_index = 0  # Global variable to keep track of the current step

def preprocess_flight_plans(drone_flights):
    actions_by_time = {}
    current_positions = {drone_id: "I8" for drone_id in drone_flights}  # Starting position

    for drone_id, flights in drone_flights.items():
        time_step = 0

        for flight in flights:
            for action in flight:
                if "FLY TO" in action:
                    target_cell = action.split()[-1]
                    actions_by_time.setdefault(time_step, []).append(('arrow', drone_id, current_positions[drone_id], target_cell))
                    current_positions[drone_id] = target_cell

                elif "SEARCH" in action:
                    search_cells = action.replace("SEARCH", "").split(",")
                    for cell in search_cells:
                        cell = cell.strip()
                        actions_by_time.setdefault(time_step, []).append(('label', drone_id, cell))
                        current_positions[drone_id] = cell  # Update the current position
                        time_step += 1

                elif "RECHARGE" in action:
                    # Add an arrow to the charging station before recharging
                    charging_station = "F1"  # Assuming F1 is the charging station
                    actions_by_time.setdefault(time_step, []).append(('arrow', drone_id, current_positions[drone_id], charging_station))
                    current_positions[drone_id] = charging_station  # Update the current position

                    # Assuming 3 timesteps for recharging
                    for _ in range(3):
                        actions_by_time.setdefault(time_step, []).append(('recharge', drone_id))
                        time_step += 1

            # Increment timestep for next flight's "FLY TO"
            time_step += 1

    return actions_by_time

def animate_actions(actions_by_time):
    for time_step in sorted(actions_by_time.keys()):
        for action in actions_by_time[time_step]:
            action_type, drone_id, *details = action

            if action_type == 'arrow':
                from_cell, to_cell = details
                draw_arrow(from_cell, to_cell, drone_colors[drone_id])
            elif action_type == 'label':
                cell = details[0]
                label_cell(cell, drone_id, drone_colors[drone_id])
            elif action_type == 'recharge':
                # Recharge action might not need a visual representation
                pass

        root.update()
        root.after(1000)  # Delay for each timestep

# Create the main window

root = tk.Tk()
root.title("Scene Builder for SMP Tests")

# Canvas for the grid
canvas = tk.Canvas(root, width=num_cols * cell_size, height=num_rows * cell_size)
canvas.grid(row=0, column=0)

# Create rectangles and labels for the grid
cells = {}
for r in range(num_rows):
    for c in range(num_cols):
        x1, y1 = c * cell_size, r * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size
        rect = canvas.create_rectangle(x1, y1, x2, y2, fill='white')
        cells[(r, c)] = rect
        label = f'{row_to_letter(r)}{c + 1}'
        canvas.create_text(x1 + 20, y1 + 20, text=label, fill='black')

# Load and display the terrain from the XML file
terrain_file = open_terrain_file()
if terrain_file:
    terrain_dict = parse_terrain_file(terrain_file)
    color_terrain(terrain_dict)

# Load drone flights and preprocess them
drone_file = open_droneflight_file()
if drone_file:
    drone_flights, drone_colors = parse_drone_flights(drone_file)
    actions_by_time = preprocess_flight_plans(drone_flights)
    drone_counters = {drone_id: 0 for drone_id in drone_colors.keys()}

# Animate Actions
animate_actions(actions_by_time)

root.mainloop()
