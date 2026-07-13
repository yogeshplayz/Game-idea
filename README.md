# Game Idea - Elemental Dungeon Crawler

A challenging 2D role-playing dungeon crawler where players navigate procedurally generated levels with strategic combat and permadeath mechanics.

## 📋 Overview

This repository contains the design documentation and implementation code for an element-based dungeon crawler RPG. The game emphasizes replayability, strategic gameplay, and permadeath consequences.

**Tech Stack:** Python | GDScript | HTML/Web Visualization

---

## 🎮 Core Game Mechanics

### Seven Elemental Classes
Choose from seven unique fighting classes/elements, each with distinct abilities and playstyles.

### Key Features
- **Procedurally Generated Dungeons** - Unique level layouts and enemy combinations for every run
- **Permadeath Mechanic** - Permanent character death ends the run; no saves or retries
- **Dynamic Loot System** - Random drops from enemies and destructible objects
- **Skill Progression** - Unlock abilities through gameplay, not fixed leveling
- **Resource Scarcity** - Limited healing potions and consumables per run
- **Boss Variants** - Multiple permutations of boss encounters across different runs
- **Multiple Endings** - Story paths diverge based on player choices and achievements

### Design Principles
1. No fixed routes - Dynamic, non-linear progression
2. Strategic combat prioritizing tactical decision-making
3. High replayability through procedural generation and randomization
4. Consequence-driven gameplay with permanent choices

---

## 📁 Repository Structure

### `/Game Story`
Narrative and world-building documentation
- **Game story.md** - Main narrative, plot progression, and story arcs
- **Characters.md** - NPC profiles, character backgrounds, and relationships
- **areas.md** - World locations, regions, and environmental descriptions
- **conversation.md** - Dialogue trees and NPC interactions

### `/Game System`
Core gameplay systems and mechanics implementation
- **fighting_system.py** - Combat mechanics, damage calculation, abilities
- **movement_system.py** - Player movement and collision detection
- **movement_system.gd** - GDScript implementation for Godot engine
- **weapons_and_armor.md** - Equipment stats, modifiers, and balancing
- **route.md** - Level progression, dungeon layouts, and progression design
- **elemental_regions_world.html** - Interactive world map visualization

### Root Files
- **ideas.md** - Quick design notes and brainstorming
- **README.md** - This file

---

## 🛠️ Development

### Setup Requirements
- Python 3.x (for gameplay systems)
- Godot Engine (for GDScript)
- Basic HTML/CSS knowledge (for visualization tools)

### Running the Systems
Refer to individual system files for implementation details:
```bash
python Game\ system/fighting_system.py
python Game\ system/movement_system.py
```

---

## 🎯 Design Goals

- Create a challenging, roguelike experience with strategic depth
- Balance difficulty with accessibility through varied elemental mechanics
- Build a cohesive elemental world with meaningful environmental storytelling
- Implement procedural generation for infinite replayability

---

## 📅 Last Updated
09/07/26

---

## 🤝 Contributing

This is a design document and prototype repository. Contributions and feedback are welcome!

For suggestions or discussions about game mechanics, please open an issue.

---

## 📝 License

[Add your license here]
