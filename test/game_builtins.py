import random as py_random
import builtins as python_builtins
from number_wrapper import Number

# Save original Python builtins before we override them
_original_len = python_builtins.len
_original_print = python_builtins.print
_original_abs = python_builtins.abs
_original_max = python_builtins.max
_original_min = python_builtins.min
_original_range = python_builtins.range

_original_range = python_builtins.range



# GameEnum - unique enum type where each instance only equals itself
class GameEnum:
    _next_id = 0
    
    def __init__(self, name, category=None):
        self._name = name
        self._category = category
        self._id = GameEnum._next_id
        GameEnum._next_id += 1
    
    def __repr__(self):
        if self._category:
            return f"{self._category}.{self._name}"
        return self._name
    
    def __str__(self):
        return self._name
    
    def __eq__(self, other):
        return self is other
    
    def __ne__(self, other):
        return self is not other
    
    def __hash__(self):
        return hash(self._id)

# Direction constants
North = GameEnum('North', 'Direction')
South = GameEnum('South', 'Direction')
East = GameEnum('East', 'Direction')
West = GameEnum('West', 'Direction')

# Entities enum for testing
class Entities:
    Grass = GameEnum('Grass', 'Entities')
    Bush = GameEnum('Bush', 'Entities')
    Tree = GameEnum('Tree', 'Entities')
    Carrot = GameEnum('Carrot', 'Entities')
    Pumpkin = GameEnum('Pumpkin', 'Entities')
    Sunflower = GameEnum('Sunflower', 'Entities')
    Cactus = GameEnum('Cactus', 'Entities')
    Maze = GameEnum('Maze', 'Entities')
    Treasure = GameEnum('Treasure', 'Entities')

class Grounds:
    Grassland = GameEnum('Grassland', 'Grounds')
    Soil = GameEnum('Soil', 'Grounds')
    
class Unlocks:
    Sunflower = GameEnum('Sunflower', 'Unlocks')
    Cactus = GameEnum('Cactus', 'Unlocks')
    Companion = GameEnum('Companion', 'Unlocks')
    Mazes = GameEnum('Mazes', 'Unlocks')

def get_world_size():
    """Mock get_world_size function - returns a reasonable test world size"""
    return 100

def random():
    """Mock random function - returns a random float between 0 and 1"""
    return py_random.random()

def num_unlocked(unlock_item):
    """Mock num_unlocked function - returns 0 for testing"""
    return 0

# Position tracking and map system
_world_state = {
    'pos_x': 0,
    'pos_y': 0,
    'world_size': 100,
    'map': {},  # (x, y) -> {'entity': Entities.*, 'ground': Grounds.*}
}

def _init_map():
    """Initialize the map with default values"""
    world_size = _world_state['world_size']
    _world_state['map'] = {}
    for x in range(world_size):
        for y in range(world_size):
            _world_state['map'][(x, y)] = {
                'entity': None,
                'ground': Grounds.Grassland
            }

def _get_current_tile():
    """Get the tile at current position"""
    pos = (_world_state['pos_x'], _world_state['pos_y'])
    if pos not in _world_state['map']:
        _world_state['map'][pos] = {
            'entity': None,
            'ground': Grounds.Grassland
        }
    return _world_state['map'][pos]

def move(direction):
    """Move in the specified direction, returns True on success, False on failure"""
    world_size = _world_state['world_size']
    
    if direction == North:
        _world_state['pos_y'] = (_world_state['pos_y'] + 1) % world_size
    elif direction == South:
        _world_state['pos_y'] = (_world_state['pos_y'] - 1) % world_size
    elif direction == East:
        _world_state['pos_x'] = (_world_state['pos_x'] + 1) % world_size
    elif direction == West:
        _world_state['pos_x'] = (_world_state['pos_x'] - 1) % world_size
    else:
        return False
    
    return True

def can_move(direction):
    """Check if can move in the specified direction, always returns True for toroidal world"""
    if direction in (North, South, East, West):
        return True
    return False

def get_pos_x():
    """Get current X position"""
    return _world_state['pos_x']

def get_pos_y():
    """Get current Y position"""
    return _world_state['pos_y']

def clear():
    """Move to (0, 0) and reset the entire map"""
    _world_state['pos_x'] = 0
    _world_state['pos_y'] = 0
    _init_map()

def till():
    """Toggle ground type between Grassland and Soil at current position"""
    tile = _get_current_tile()
    if tile['ground'] == Grounds.Grassland:
        tile['ground'] = Grounds.Soil
    elif tile['ground'] == Grounds.Soil:
        tile['ground'] = Grounds.Grassland
    return True

# Game-style builtin functions that override Python defaults
def len(c):
    """Game version of len() - returns length of collection"""
    return _original_len(c)

def add(c, item):
    """Game version of add() - adds item to set"""
    c.add(item)

def remove(c, item):
    """Game version of remove() - removes item from collection"""
    if hasattr(c, 'remove'):
        c.remove(item)
    else:
        raise TypeError(f"'{type(c).__name__}' object has no method 'remove'")

def print(*args, **kwargs):
    """Game version of print() - prints to console"""
    _original_print(*args, **kwargs)

def quick_print(*args, **kwargs):
    """Game version of quick_print() - alias for print"""
    _original_print(*args, **kwargs)

def abs(x):
    """Game version of abs() - returns absolute value"""
    return _original_abs(x)

def max(*args, **kwargs):
    """Game version of max() - returns maximum value"""
    return _original_max(*args, **kwargs)

def min(*args, **kwargs):
    """Game version of min() - returns minimum value"""
    return _original_min(*args, **kwargs)

def setup_game_builtins():
    """Setup all game built-in constants and functions into Python builtins"""
    # Initialize map on first setup
    if not _world_state['map']:
        _init_map()
    
    python_builtins.North = North
    python_builtins.South = South
    python_builtins.East = East
    python_builtins.West = West
    python_builtins.Entities = Entities
    python_builtins.Grounds = Grounds
    python_builtins.get_world_size = get_world_size
    python_builtins.random = random
    python_builtins.Unlocks = Unlocks
    python_builtins.num_unlocked = num_unlocked
    
    # Movement and position functions
    python_builtins.move = move
    python_builtins.can_move = can_move
    python_builtins.get_pos_x = get_pos_x
    python_builtins.get_pos_y = get_pos_y
    python_builtins.clear = clear
    python_builtins.till = till
    
    # Number wrapper for AST transformation
    python_builtins.Number = Number
    
    # Override Python builtins with game versions (only functions, not types)
    python_builtins.len = len
    python_builtins.add = add
    python_builtins.remove = remove
    python_builtins.print = print
    python_builtins.quick_print = quick_print
    python_builtins.abs = abs
    python_builtins.max = max
    python_builtins.min = min
    
    # Note: list, set are NOT overridden because they are types used by Python internals
    # The original Python versions work fine for game code