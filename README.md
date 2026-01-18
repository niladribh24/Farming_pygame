# PyDew Valley - Educational Farming Sim 🌾

A gamified farming simulation built with Python and Pygame, designed to teach **Data Structures** through interactive gameplay mechanics. Manage a sustainable farm, learn about soil health, and unlock skills by observing real-time consequences of your farming practices.

## 🎓 Educational Features: Data Structures in Action

This project integrates core computer science data structures directly into game logic:

| Data Structure | In-Game Feature | Description |
| :--- | :--- | :--- |
| **List** | Daily Action Log | Sequentially tracks your actions (watering, planting) to generate day summaries. |
| **Queue (FIFO)** | Weather System | A First-In-First-Out queue forecasts weather for the upcoming week. |
| **Stack (LIFO)** | Undo System | A Last-In-First-Out stack allows you to undo your last farming mistake (Press 'U'). |
| **Set** | Achievements | Uses hash-based sets for O(1) checking of unique unlocked achievements. |
| **Dictionary** | Knowledge Base | Stores O(1) access data for crop info, soil impacts, and item properties. |
| **Tree** | Skill System | Hierarchical skill tree where unlocking parent skills (e.g., Crop Rotation) enables child skills. |
| **Graph** | Farm Navigation | Models the farm as a connected graph for pathfinding (used by traders). |
| **2D Array** | Soil Grid | Represents the farm layouts, tracking water retention and crop status per tile. |

## 🎮 Gameplay Features

### Sustainable Farming
*   **Soil Health**: Over-farming the same crop deletes nutrients. Rotate crops to keep soil healthy!
*   **Fertilizers**: Apply generic or organic fertilizers (Press 'F' to switch, 'R' to apply).
*   **Consequences**: Monocropping damages soil; Rotation restores it. Poor soil yields fewer crops.

### Advanced Mechanics
*   **Water Management**:
    *   **Irrigation Modes**: Switch between Manual, Efficient, and Drip irrigation (Press 'I').
    *   **Rain Harvesting**: Rainwater is automatically collected into your reserve.
    *   **Crop Death**: Crops die if unwatered for 2 consecutive days.
*   **Orchards**: Trees take **5 days** to regrow after chopping. Apples auto-collect on harvest.
*   **Save System**: Your progress, unrestricted soil, and tree states are saved automatically on sleep.

### UI & UX
*   **Knowledge Book**: In-game wiki explaining crops and mechanics (Press 'B').
*   **Settings Menu**: Adjust volume and controls.
*   **Shop**: Buy seeds and sell crops to the trader.
*   **Overlays**: Real-time soil health bars and notifications.

## ⌨️ Controls

| Key | Action |
| :--- | :--- |
| **WASD** / Arrows | Move Player |
| **Space** | Use Tool (Axe, Hoe, Water) |
| **Enter** | Interact / Sleep / Buy |
| **Q** | Switch Tool |
| **E** | Switch Seed |
| **F** | Switch Fertilizer Type |
| **R** | Apply Fertilizer |
| **I** | Switch Irrigation Mode |
| **U** | Undo Last Action |
| **B** | Open Knowledge Book |
| **Esc** | Settings / Pause |

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/niladribh24/Farming_pygame.git
    cd Farming_pygame
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install pygame-ce
    ```

4.  **Run the game**:
    ```bash
    python main.py
    ```

## 📜 License

This project is for educational purposes, demonstrating how abstract data structures can be applied to create engaging software systems.
