# D&D 5e Dungeon Master Agent Integration

## Overview

This directory contains a complete Dungeons & Dragons 5th Edition agent system that can be used as a standalone tool or integrated with the whisplay-ai-chatbot system.

## Usage

### Standalone Mode
```bash
# Start interactive session
python dnd_agent.py

# Or use CLI commands
python dnd_agent.py check "CharacterName" DEX stealth --interactive
python dnd_agent.py save "CharacterName" CON --dc 15
python dnd_agent.py roll "2d6+3"
python dnd_agent.py create-character "Lyra" "Elf" "Wizard" --level 5 --background "Sage"
```

### Interactive Dice Modes
All dice rolling supports two modes:
1. **Virtual** - Agent rolls randomly (default)
2. **Physical** - User inputs actual dice results (`-i` flag or interactive prompts)

Example:
```bash
# Interactive mode - prompts for virtual/physical choice
python dnd_agent.py check "Lyra" INT Arcana -i

# Advantage with physical dice
python dnd_agent.py check "Lyra" DEX stealth --advantage --interactive
```

## Files

| File | Purpose |
|------|---------|
| `agent.md` | Dungeon Master persona and behavior guidelines |
| `SKILL.md` | D&D 5e rulebook reference and skill documentation |
| `dnd_agent.py` | Core Python engine with interactive dice system |
| `session.py` | Interactive session runner with full TUI |
| `README.md` | Complete usage documentation |
| `sessions/` | Session log directory |
| `dnd_session.json` | Persistent session state |

## Key Features

- 🎲 **Interactive Dice Rolling** - Physical or virtual dice with automatic modifier calculation
- 🧙 **Character Management** - Auto-calculated ability scores, HP, AC, and derived stats
- ⚔️ **Combat System** - Initiative tracking, attack resolution, and condition management
- 📚 **Rulebook Reference** - Complete D&D 5e SRD content (classes, spells, monsters, items)
- 🎭 **DM Persona** - "Draelin the Wise" with immersive narration and fair rulings

## Integration Notes

This agent can be exposed as an `llm-tools` plugin for whisplay-ai-chatbot by wrapping the core functions:

- `roll_dice(notation, interactive)` → `rollDice`
- `DnDAgent.make_ability_check()` → `abilityCheck`
- `DnDAgent.make_saving_throw()` → `savingThrow`
- `DnDAgent.create_character()` → `createCharacter`

See the `agent.md` file for detailed persona guidelines and the `SKILL.md` file for the complete rulebook reference.

## Support

For issues or feature requests, see the main project repository.