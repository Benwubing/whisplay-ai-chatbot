# D&D 5e Dungeon Master Agent

A complete toolkit for running Dungeons & Dragons 5th Edition sessions, featuring automated dice rolling, character management, combat encounter facilitation, and comprehensive rulebook reference.

## Files

| File | Description |
|------|-------------|
| `agent.md` | Dungeon Master persona and behavior guidelines |
| `SKILL.md` | Comprehensive D&D 5e rulebook reference skill |
| `dnd_agent.py` | Full Python implementation of the DM agent |
| `session.py` | Interactive session runner for gameplay |

## Quick Start

### Install Python 3.x

No special dependencies required - uses only Python standard library!

### Running the CLI Tool (with Interactive Dice Support)

```bash
# Roll dice (virtual - automatic)
python dnd_agent.py roll "2d6+3"
python dnd_agent.py roll "1d20+5"
python dnd_agent.py roll "d100"

# Roll dice interactively (choose physical or virtual)
python dnd_agent.py roll "1d20+5" --interactive

# Roll ability scores
python dnd_agent.py roll-stats

# Create a character
python dnd_agent.py create-character "Thrain" "Dwarf" "Fighter" --level 3 --background "Soldier"

# Make an ability check (virtual)
python dnd_agent.py check "Thrain" STR

# Make an ability check with physical dice
python dnd_agent.py check "Thrain" DEX stealth --advantage --interactive

# Make a saving throw with virtual dice
python dnd_agent.py save "Thrain" CON --dc 15

# Make a saving throw with physical dice
python dnd_agent.py save "Thrain" CON --dc 15 --interactive

# Roll initiative
python dnd_agent.py initiative "Thrain" "Elara" "Gorbag"
```

### Interactive Session Mode (with Physical Dice Support)

```bash
python session.py
```

In the interactive session, you can use:
- `roll <dice>` — Virtual dice roll
- `roll <dice> -i` — Interactive mode: prompt to choose physical or virtual
- `check <char> <ability> [skill] [-a] [-d] [-i]` — Ability check
- `save <char> <ability> [dc] [-a] [-d] [-i]` — Saving throw
5. Roll on random tables

## Key Features

### 🎲 Dice Rolling
- Full dice notation support (`2d6+3`, `1d20`, `d100`, etc.)
- Advantage/disadvantage mechanics
- Critical hit and failure detection

### 🧙 Character Management
- Automatic ability score generation (4d6 drop lowest)
- Full character sheet tracking (HP, AC, initiative, etc.)
- Class-specific features and saving throw proficiencies
- Inventory and equipment tracking

### ⚔️ Combat System
- Full initiative tracking with turn management
- Attack roll resolution with advantage/disadvantage
- Damage calculation with critical hits
- Condition tracking (poisoned, prone, stunned, etc.)

### 📚 Rulebook Integration
- Complete reference for all 5e mechanics
- Spell lists organized by class and level
- Monster statistics with pre-built templates
- Equipment and weapon databases
- Condition and status effect references

### 🎭 DM Tools
- Random encounter generation by environment
- Character action parsing (natural language → skill check)
- Passive perception/insight calculation
- Random treasure and weather tables

## Agent Behavior

The `agent.md` file defines the Dungeon Master persona:

> **`Draelin the Wise`** - An experienced Dungeon Master who balances rules mastery with creative improvisation.

Key behaviors:
- **Descriptive but Concise** narration
- **Player-Focused** interaction (asks "What do you do?" rather than narrating)
- **Fair and Consistent** rule application
- **Adaptive Improvisation** when rules don't cover a situation

## Rulebook Coverage

The `SKILL.md` file provides comprehensive 5e SRD coverage including:

- **Core Rules**: Advantage/disadvantage, conditions, ability scores
- **Character Classes**: All 12 base classes with features
- **Spells**: Full spell lists by class, spell schools, casting mechanics
- **Combat**: Initiative, attacks, damage types, cover system
- **Equipment**: Weapons, armor, tools, currency
- **Backgrounds**: All 8 standard backgrounds with features
- **Monsters**: Templates for common enemies

## Usage Examples

### Creating Characters
```python
from dnd_agent import *

agent = DnDAgent()
scores = agent.roll_ability_scores()
character = agent.create_character(
    name="Lyra Nightwhisper",
    race="Elf",
    class_name="Rogue",
    ability_scores=scores,
    level=5,
    background="Urchin"
)
print(format_character_sheet(character))
```

### Making Checks
```python
# Strength (Athletics) check with advantage
result = agent.make_ability_check(
    character_name="Lyra",
    ability="STR",
    skill="athletics",
    advantage=True
)

# Dexterity saving throw against DC 18
result = agent.make_saving_throw(
    character_name="Lyra",
    ability="DEX",
    dc=18
)
```

### Combat Encounters
```python
# Set up combat
encounter = EncounterManager()
encounter.add_character(character)
encounter.add_monster(agent.monsters["Orc"], count=3)

# Roll initiative
initiative_order = encounter.roll_initiative()

# Process turns
while encounter.is_active:
    current = encounter.get_current_combatant()
    print(f"{current['name']}'s turn!")
    # ... resolve actions ...
    encounter.next_turn()
```

## Customization

### Adding New Weapons
```python
from dnd_agent import Weapon, ContentLibrary

library = ContentLibrary()
library.get_weapons()["My Custom Weapon"] = Weapon(
    name="My Custom Weapon",
    damage_dice="2d6",
    damage_type="fire",
    properties=["heavy", "two-handed"],
    is_simple=False
)
```

### Adding New Monsters
```python
from dnd_agent import Monster

dragon = Monster(
    name="Young Red Dragon",
    size="Large",
    type="dragon",
    alignment="chaotic evil",
    challenge_rating="10",
    xp=5200,
    armor_class=18,
    hit_points=256,
    speed="40 ft., fly 80 ft.",
    # ... add attributes ...
)
```

## Hardware Requirements

- **CPU**: Any modern processor (8+ cores recommended)
- **RAM**: 4 GB+ recommended for large battles
- **Storage**: Minimal (~100 KB for code, session files auto-saved)
- **OS**: Cross-platform (Windows, macOS, Linux)

## Notes

- The agent uses Python's `random` module for dice rolls
- Session data is automatically saved to `dnd_session.json`
- All weapon, armor, and monster data is based on D&D 5e SRD
- For official D&D content, consult Wizards of the Coast materials

---

*Have fun, and may your dice roll high!* 🎲