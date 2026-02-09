# Data Structures Implementation Guide

This document tracks where each major data structure is implemented and used in the **Sustainable Farming Game** codebase.

## 1. List (Dynamic Array)
**File**: `c:\Ritika\Farming_pygame\learning_system.py`
**Usage**: Daily Action Log
- **Implementation**: `self.daily_actions = []` (Line 126)
- **Purpose**: Stores a sequential log of all player actions (planting, watering, harvesting) for the current day to generate the end-of-day summary.
- **Key Operations**: 
  - `append()`: Adding actions.
  - `clear()`: Resetting at end of day.

**File**: `c:\Ritika\Farming_pygame\inventory.py`
**Usage**: Inventory Categories & Items
- **Implementation**: `self.categories = [...]` (Line 41)
- **Purpose**: Stores the list of inventory tabs and the list of items to display in the current tab.

---

## 2. Stack (LIFO - Last In, First Out)
**File**: `c:\Ritika\Farming_pygame\learning_system.py`
**Usage**: Undo System
- **Implementation**: `self.action_stack = []` (Line 135)
- **Purpose**: Allows players to undo their last farming action (e.g., accidental planting).
- **Key Operations**:
  - `push_action()`: Adds action to top of stack.
  - `pop_action()`: Removes and returns most recent action for undoing.

---

## 3. Queue (FIFO - First In, First Out)
**File**: `c:\Ritika\Farming_pygame\learning_system.py`
**Usage**: Weather Event System
- **Implementation**: `self.event_queue = deque()` (Line 130)  *(Using Python's `collections.deque`)*
- **Purpose**: Manages a queue of upcoming weather events (Rain/Sun) to ensure a balanced weather cycle.
- **Key Operations**:
  - `append()`: Adding new weather days to the end.
  - `popleft()`: Retrieving the next day's weather from the front.

---

## 4. Set (Hash Set)
**File**: `c:\Ritika\Farming_pygame\learning_system.py` & `skill_tree.py`
**Usage**: Achievement Tracking
- **Implementation**: `self.achievements = set()` (Line 139)
- **Purpose**: Stores IDs of unlocked achievements. Uses a Set for O(1) constant-time lookup to instantly check if an achievement is already unlocked.
- **Key Operations**:
  - `add()`: Unlocking a new achievement.
  - `in`: Checking if an achievement exists (e.g., `if 'first_harvest' in self.achievements`).

---

## 5. Tree (Hierarchical)
**File**: `c:\Ritika\Farming_pygame\skill_tree.py`
**Implementation**: `class SkillNode` & `class SkillTree`
**Usage**: Skill Progression System
- **Structure**: Root Node (Farmer) -> Branches (Water, Soil) -> Leaves (Specific Skills).
- **Purpose**: Models the dependency hierarchy of skills (e.g., must unlock "Sustainable Farming" before "Crop Rotation").
- **Key Features**:
  - Parent-Child relationships (`self.children = []`).
  - Recursive traversal for unlocking.

---

## 6. Graph (Network)
**File**: `c:\Ritika\Farming_pygame\soil.py` (Gameplay Implementation)
**Usage**: Irrigation Network Connectivity
- **Implementation**: BFS Traversal using Adjacency (Touching Rectangles).
- **Purpose**: Ensures Drip Emitters only function if physically connected to a **Water Tank** or **River**.
- **Key Features**:
  - `_get_connected_drip_emitters()` builds graph of connected pipes on-the-fly.
  - Uses `collections.deque` (Queue) for Breadth-First Search traversal.
  - Uses `Set` to track visited nodes.
  - Treats **Water Tanks** and **River Tiles** as graph source nodes.

**File**: `c:\Ritika\Farming_pygame\farm_graph.py` (Backend Model)
**Usage**: Farm Connectivity & Pathfinding
- **Implementation**: Adjacency List (Dictionary of Lists)
- **Purpose**: Represents key locations on the farm (House, Field, Market, River) as nodes and the paths between them as edges.
- **Key Features**:
  - `self.graph = {}` stores connections.
  - Used to calculate visiting "efficiency" or verify if all farm areas are accessible.

---

## 7. 2D Array (Grid)
**File**: `c:\Ritika\Farming_pygame\soil.py`
**Usage**: Soil/Terrain Map
- **Implementation**: `self.grid = [[...], [...]]`
- **Purpose**: Represents the farm layout as a grid of tiles. Each cell `[x][y]` contains data about that specific tile (is it hoed? watered? planted?).
- **Key Operations**:
  - Double indexing `grid[y][x]` to access specific tiles.
  - Nested loops for rendering and updating state.

---

## 8. Hash Map (Dictionary)
**File**: `c:\Ritika\Farming_pygame\inventory.py`
**Usage**: Fast Item Search
- **Implementation**: `self.item_hash_map = {}` (Line 176)
- **Purpose**: Maps item names (keys) directly to item data objects (values) for O(1) instant search results in the inventory.
- **Key Operations**:
  - Key-Value mapping.
  - `get()` for instant retrieval.
