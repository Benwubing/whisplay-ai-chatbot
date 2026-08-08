#!/usr/bin/env python3
"""
D&D 5e Dungeon Master Agent Implementation
A complete toolkit for running D&D 5e sessions with automated mechanics.
Supports interactive dice rolling: use physical dice or let the agent roll!
"""

import random
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import os


# =============================================================================
# Dice Rolling Engine (Interactive)
# =============================================================================

def roll_dice(dice_string: str, interactive: bool = False) -> Tuple[int, List[int]]:
    """
    Roll dice from a dice string like '2d6+3' or '1d20+5'
    Returns (total, list_of_rolls)

    If interactive=True, asks user whether to use physical dice or virtual roll.
    """
    # Parse the dice notation
    pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
    match = re.match(pattern, dice_string.replace(' ', ''))
    
    if not match:
        raise ValueError(f"Invalid dice string: {dice_string}")
    
    num_dice = int(match.group(1)) if match.group(1) else 1
    die_type = int(match.group(2))
    modifier_str = match.group(3)
    
    modifier = int(modifier_str) if modifier_str else 0
    
    # Interactive mode: let user choose physical or virtual
    if interactive:
        choice = None
        while choice not in ['virtual', 'physical']:
            print(f"\n🎲 Roll: {dice_string}")
            print(f"  Option 1: [virtual] Let the agent roll (automatic)")
            print(f"  Option 2: [physical] I rolled physical dice (enter results manually)")
            choice = input("Enter your choice: ").strip().lower()
            
            if choice in ['1', 'v']:
                choice = 'virtual'
            elif choice in ['2', 'p', 'manual']:
                choice = 'physical'
            elif choice == '':
                choice = 'virtual'  # Default to virtual
        
        if choice == 'physical':
            return _get_physical_dice_input(dice_string, num_dice, die_type, modifier)
    
    # Default: virtual roll
    rolls = [random.randint(1, die_type) for _ in range(num_dice)]
    total = sum(rolls) + modifier
    return total, rolls + ([modifier] if modifier != 0 else [])


def _get_physical_dice_input(dice_string: str, num_dice: int, die_type: int, modifier: int) -> Tuple[int, List[int]]:
    """
    Prompt user for physical dice results
    """
    print(f"\n🎲 Enter your physical dice results for: {dice_string}")
    print(f"  Roll {num_dice}d{die_type}", end="")
    if modifier != 0:
        print(f" and add {modifier}", end="")
    print()
    
    rolls = []
    for i in range(num_dice):
        while True:
            try:
                val = input(f"  Dice {i+1} (1-{die_type}): ").strip()
                roll_val = int(val)
                if 1 <= roll_val <= die_type:
                    rolls.append(roll_val)
                    break
                else:
                    print(f"  Invalid! Must be between 1 and {die_type}")
            except ValueError:
                print(f"  Please enter a valid number between 1 and {die_type}")
    
    detail = ' + '.join(str(r) for r in rolls) + (f" + {modifier}" if modifier != 0 else "")
    total = sum(rolls) + modifier
    
    # Also calculate the virtual roll for verification
    virtual_rolls = [random.randint(1, die_type) for _ in range(num_dice)]
    virtual_total = sum(virtual_rolls) + modifier
    
    print(f"\n  Your result: {detail} = **{total}**")
    print(f"  (Agent would have rolled: {' '.join(str(r) for r in virtual_rolls)} = {virtual_total})")
    
    return total, rolls + ([modifier] if modifier != 0 else [])


def roll_d20(advantage: bool = False, disadvantage: bool = False, interactive: bool = False) -> Tuple[int, List[int]]:
    """
    Roll a d20, optionally with advantage or disadvantage
    Returns (result, [rolls])

    If interactive=True, asks user whether to use physical dice or virtual roll.
    """
    if advantage and disadvantage:
        # Cancel each other out
        return roll_d20(interactive=interactive)
    
    # Interactive mode
    if interactive:
        mode = ""
        if advantage:
            mode = "advantage"
        elif disadvantage:
            mode = "disadvantage"
        
        choice = None
        while choice not in ['virtual', 'physical']:
            print(f"\n🎲 d20 Roll {mode}:" if mode else "\n🎲 d20 Roll:")
            print(f"  Option 1: [virtual] Let the agent roll")
            print(f"  Option 2: [physical] I rolled a physical d20")
            choice = input("Enter your choice: ").strip().lower()
            if choice in ['1', 'v']:
                choice = 'virtual'
            elif choice in ['2', 'p', 'manual']:
                choice = 'physical'
            elif choice == '':
                choice = 'virtual'
        
        if choice == 'physical':
            if advantage or disadvantage:
                print(f"\n  Enter your physical dice results for d20 {mode}:")
                rolls = []
                for i in range(2):
                    while True:
                        try:
                            val = input(f"  d20 {i+1} (1-20): ").strip()
                            roll_val = int(val)
                            if 1 <= roll_val <= 20:
                                rolls.append(roll_val)
                                break
                            else:
                                print("  Invalid! Must be between 1 and 20")
                        except ValueError:
                            print("  Please enter a valid number between 1 and 20")
                result = max(rolls) if advantage else min(rolls)
                detail = f"{rolls[0]} and {rolls[1]}, take {result} ({mode})"
                return result, rolls + [0]  # 0 as sentinel for modifier position
            else:
                while True:
                    try:
                        val = input("\n  Enter your physical d20 roll (1-20): ").strip()
                        roll_val = int(val)
                        if 1 <= roll_val <= 20:
                            virtual_roll = random.randint(1, 20)
                            print(f"  Your roll: {roll_val}")
                            print(f"  (Agent would have rolled: {virtual_roll})")
                            return roll_val, [roll_val]
                        else:
                            print("  Invalid! Must be between 1 and 20")
                    except ValueError:
                        print("  Please enter a valid number between 1 and 20")
    
    # Default: virtual roll
    if advantage:
        rolls = [random.randint(1, 20) for _ in range(2)]
        return max(rolls), rolls
    
    if disadvantage:
        rolls = [random.randint(1, 20) for _ in range(2)]
        return min(rolls), rolls
    
    result = random.randint(1, 20)
    return result, [result]


def parse_dice_notation(notation: str, interactive: bool = False) -> str:
    """
    Parse dice notation and return formatted result
    Examples: '2d6', '1d20+5', '3d8-2', etc.
    """
    try:
        total, rolls = roll_dice(notation, interactive=interactive)
        detail = ' + '.join(str(r) for r in rolls) if len(rolls) > 1 else str(rolls[0])
        return f"🎲 {notation}: {detail} = **{total}**"
    except ValueError as e:
        return f"❌ Error: {str(e)}"


# =============================================================================
# Character System
# =============================================================================

class Ability(Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class Skill(Enum):
    ATHLETICS = "athletics"              # STR
    ACROBATICS = "acrobatics"            # DEX
    SLEIGHT_OF_HAND = "sleight_of_hand"  # DEX
    STEALTH = "stealth"                 # DEX
    ARCANA = "arcana"                  # INT
    HISTORY = "history"                # INT
    INVESTIGATION = "investigation"    # INT
    NATURE = "nature"                  # INT
    RELIGION = "religion"              # INT
    ANIMAL_HANDLING = "animal_handling" # WIS
    INSIGHT = "insight"                # WIS
    MEDICINE = "medicine"              # WIS
    PERCEPTION = "perception"          # WIS
    SURVIVAL = "survival"              # WIS
    DECEPTION = "deception"            # CHA
    INTIMIDATION = "intimidation"      # CHA
    PERFORMANCE = "performance"        # CHA
    PERSUASION = "persuasion"          # CHA


@dataclass
class Character:
    """Represents a D&D 5e character"""
    name: str
    race: str
    class_name: str
    level: int = 1
    background: str = ""
    player_name: str = ""
    
    # Ability Scores
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    # Proficiency
    proficiency_bonus: int = 2
    is_proficient: Dict[str, bool] = field(default_factory=dict)
    expertise: List[str] = field(default_factory=list)
    
    # Combat Stats
    max_hp: int = 10
    current_hp: int = 10
    armor_class: int = 10
    initiative: float = 0.0
    speed: int = 30
    
    # Resources
    hit_dice: str = "d10"
    spell_slots: Dict[int, int] = field(default_factory=dict)
    sorcery_points: int = 0
    ki_points: int = 0
    rages: int = 0
    rages_per_long_rest: int = 0
    
    # Conditions & Status
    conditions: List[str] = field(default_factory=list)
    temporary_hp: int = 0
    is_concentrating: bool = False
    
    # Inventory
    inventory: List[str] = field(default_factory=list)
    gold: float = 0.0
    equipment: List[str] = field(default_factory=list)
    
    # Skill Proficiencies
    skill_profs: List[Skill] = field(default_factory=list)
    
    # Tools, languages, other proficiencies
    tool_profs: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    
    # Appearance & Backstory
    appearance: str = ""
    backstory: str = ""
    personality_traits: str = ""
    ideals: str = ""
    bonds: str = ""
    flaws: str = ""
    
    @property
    def ability_modifiers(self) -> Dict[str, int]:
        def mod(score):
            return (score - 10) // 2
        
        return {
            'STR': mod(self.strength),
            'DEX': mod(self.dexterity),
            'CON': mod(self.constitution),
            'INT': mod(self.intelligence),
            'WIS': mod(self.wisdom),
            'CHA': mod(self.charisma),
        }
    
    @property
    def passive_perception(self) -> int:
        return 10 + self._get_skill_bonus(Skill.PERCEPTION)
    
    @property
    def passive_insight(self) -> int:
        return 10 + self._get_skill_bonus(Skill.INSIGHT)
    
    @property
    def passive_investigation(self) -> int:
        return 10 + self._get_skill_bonus(Skill.INVESTIGATION)
    
    @property
    def proficiency_bonuses(self) -> Dict[str, int]:
        """Return proficiency bonus for each saving throw"""
        mods = self.ability_modifiers
        bonuses = {}
        for ability in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
            prof = self.is_proficient.get(f"{ability}_save", False)
            bonuses[ability] = mods[ability] + (self.proficiency_bonus if prof else 0)
        return bonuses
    
    def _get_skill_bonus(self, skill: Skill) -> int:
        """Calculate the total bonus for a skill check"""
        skill_ability_map = {
            Skill.ATHLETICS: 'STR',
            Skill.ACROBATICS: 'DEX',
            Skill.SLEIGHT_OF_HAND: 'DEX',
            Skill.STEALTH: 'DEX',
            Skill.ARCANA: 'INT',
            Skill.HISTORY: 'INT',
            Skill.INVESTIGATION: 'INT',
            Skill.NATURE: 'INT',
            Skill.RELIGION: 'INT',
            Skill.ANIMAL_HANDLING: 'WIS',
            Skill.INSIGHT: 'WIS',
            Skill.MEDICINE: 'WIS',
            Skill.PERCEPTION: 'WIS',
            Skill.SURVIVAL: 'WIS',
            Skill.DECEPTION: 'CHA',
            Skill.INTIMIDATION: 'CHA',
            Skill.PERFORMANCE: 'CHA',
            Skill.PERSUASION: 'CHA',
        }
        
        ability = skill_ability_map[skill]
        ability_bonus = self.ability_modifiers[ability]
        
        # Check if proficient
        is_proficient = skill in self.skill_profs
        is_expert = skill.value in self.expertise
        
        prof_bonus = self.proficiency_bonus if is_proficient else 0
        if is_expert:
            prof_bonus *= 2
        
        # Apply condition penalties (simplified)
        condition_penalty = 0
        if 'poisoned' in self.conditions:
            condition_penalty -= 2
        if 'prone' in self.conditions and skill != Skill.ACROBATICS:
            condition_penalty -= 2
        
        return ability_bonus + prof_bonus + condition_penalty
    
    def make_save(self, ability: str) -> Dict[str, Any]:
        """Make a saving throw"""
        mods = self.ability_modifiers
        base_mod = mods.get(ability.upper(), 0)
        prof_bonus = self.proficiency_bonus if self.is_proficient.get(f"{ability.upper()}_save", False) else 0
        
        roll_val, rolls = roll_d20()
        total = roll_val + base_mod + prof_bonus
        
        return {
            'roll': roll_val,
            'rolls': rolls,
            'ability': ability,
            'modifier': base_mod + prof_bonus,
            'total': total,
            'natural': rolls[0],
            'is_critical': rolls[0] == 20,
            'is_critical_failure': rolls[0] == 1,
        }
    
    def check_skill(self, skill: Skill) -> Dict[str, Any]:
        """Make a skill check"""
        bonus = self._get_skill_bonus(skill)
        roll_val, rolls = roll_d20()
        total = roll_val + bonus
        
        return {
            'roll': roll_val,
            'rolls': rolls,
            'skill': skill.value,
            'modifier': bonus,
            'total': total,
            'natural': rolls[0],
            'is_critical': rolls[0] == 20,
            'is_critical_failure': rolls[0] == 1,
            'is_advantage': len(rolls) > 1,
        }
    
    def attack(self, weapon: 'Weapon') -> Dict[str, Any]:
        """Make an attack roll"""
        # Determine attack ability
        if weapon.is_finesse:
            ability = 'DEX' if self.ability_modifiers['DEX'] > self.ability_modifiers['STR'] else 'STR'
        elif weapon.is_ranged:
            ability = 'DEX'
        else:
            ability = 'STR'
        
        ability_mod = self.ability_modifiers[ability]
        prof_bonus = self.proficiency_bonus if self.is_proficient.get('weapons', False) or not weapon.is_simple else 0
        
        attack_bonus = ability_mod + prof_bonus
        
        # Apply conditions
        has_advantage = 'blinded' not in self.conditions and 'restrained' not in self.conditions
        has_disadvantage = 'blinded' in self.conditions or 'restrained' in self.conditions or 'prone' in self.conditions
        
        roll_val, rolls = roll_d20(advantage=has_advantage, disadvantage=has_disadvantage)
        is_crit = rolls[0] == 20 or rolls[-1] == 20
        is_crit_fail = rolls[0] == 1 and rolls[-1] == 1
        
        return {
            'weapon': weapon.name,
            'attack_roll': roll_val,
            'natural': rolls[0],
            'rolls': rolls,
            'attack_bonus': attack_bonus,
            'total': roll_val + attack_bonus,
            'damage_bonus': ability_mod,
            'is_critical': is_crit,
            'is_critical_failure': is_crit_fail,
            'is_advantage': len(rolls) > 1,
        }
    
    def take_damage(self, amount: int, is_critical: bool = False) -> Dict[str, Any]:
        """Apply damage to the character"""
        if is_critical:
            amount = amount * 2
        
        self.current_hp -= amount
        damage_log = {
            'amount': amount,
            'is_critical': is_critical,
            'remaining_hp': self.current_hp,
            'is_down': self.current_hp <= 0,
        }
        
        return damage_log


@dataclass
class Weapon:
    """Represents a weapon in D&D 5e"""
    name: str
    damage_dice: str  # e.g., "1d8"
    damage_type: str  # e.g., "slashing"
    properties: List[str] = field(default_factory=list)  # e.g., ["finesse", "ranged", "thrown"]
    is_simple: bool = False  # Simple weapon?
    is_ranged: bool = False
    is_finesse: bool = False
    range_normal: int = 0
    range_long: int = 0


@dataclass
class Armor:
    """Represents armor in D&D 5e"""
    name: str
    base_ac: int
    dex_mod_max: Optional[int] = None  # None means no maximum (light armor)
    is_heavy: bool = False
    stealth_disadvantage: bool = False
    price: float = 0.0
    weight: float = 0.0


@dataclass
class Shield:
    """Represents a shield"""
    name: str
    ac_bonus: int = 2
    stealth_disadvantage: bool = False


# =============================================================================
# Spell System
# =============================================================================

@dataclass
class Spell:
    """Represents a D&D 5e spell"""
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: str
    duration: str
    description: str
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    save_type: Optional[str] = None  # e.g., "Dexterity"
    requires_concentration: bool = False
    is_ritual: bool = False
    classes: List[str] = field(default_factory=list)


# =============================================================================
# Encounter Manager
# =============================================================================

@dataclass
class Monster:
    """Basic monster representation"""
    name: str
    size: str
    type: str
    alignment: str
    challenge_rating: str
    xp: int
    armor_class: int
    hit_points: int
    speed: str
    
    # Ability Scores
    str_score: int = 10
    dex_score: int = 10
    con_score: int = 10
    int_score: int = 10
    wis_score: int = 10
    cha_score: int = 10
    
    # Skills and Saves
    saving_throws: Dict[str, int] = field(default_factory=dict)
    skills: Dict[str, int] = field(default_factory=dict)
    
    # Damage Resistances/Immunities
    damage_resistances: List[str] = field(default_factory=list)
    damage_immunities: List[str] = field(default_factory=list)
    condition_immunities: List[str] = field(default_factory=list)
    
    # Senses
    senses: str = "Passive Perception 10"
    languages: str = " — "
    challenge_rating_xp: str = ""
    
    # Traits and Actions
    traits: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    
    @property
    def modifiers(self) -> Dict[str, int]:
        def mod(score):
            return (score - 10) // 2
        
        return {
            'STR': mod(self.str_score),
            'DEX': mod(self.dex_score),
            'CON': mod(self.con_score),
            'INT': mod(self.int_score),
            'WIS': mod(self.wis_score),
            'CHA': mod(self.cha_score),
        }


class EncounterManager:
    """Manages combat encounters and initiative"""
    
    def __init__(self):
        self.combatants: List[Dict[str, Any]] = []
        self.initiative_order: List[Dict[str, Any]] = []
        self.current_turn_index: int = 0
        self.round_number: int = 0
        self.is_active: bool = False
    
    def add_character(self, character: Character, group: str = "player") -> int:
        """Add a character to the encounter"""
        mods = character.ability_modifiers
        dex_mod = mods['DEX']
        
        roll_val, rolls = roll_d20()
        init_bonus = dex_mod + (character.proficiency_bonus if character.is_proficient.get('initiative', False) else 0)
        init_value = roll_val + init_bonus
        
        combatant = {
            'name': character.name,
            'type': 'player',
            'character': character,
            'initiative_roll': init_value,
            'initiative_natural': rolls[0],
            'initiative_modifier': init_bonus,
            'current_hp': character.current_hp,
            'max_hp': character.max_hp,
            'armor_class': character.armor_class,
            'group': group,
            'conditions': [],
            'is_concentrating': False,
        }
        
        self.combatants.append(combatant)
        return len(self.combatants) - 1
    
    def add_monster(self, monster: Monster, count: int = 1, group: str = "enemy") -> List[int]:
        """Add monsters to the encounter"""
        indices = []
        for i in range(count):
            mods = monster.modifiers
            dex_mod = mods['DEX']
            
            roll_val, rolls = roll_d20()
            init_value = roll_val + dex_mod
            
            name = monster.name if count == 1 else f"{monster.name} #{i+1}"
            
            combatant = {
                'name': name,
                'type': 'monster',
                'monster': monster,
                'initiative_roll': init_value,
                'initiative_natural': rolls[0],
                'initiative_modifier': dex_mod,
                'current_hp': monster.hit_points,
                'max_hp': monster.hit_points,
                'armor_class': monster.armor_class,
                'group': group,
                'conditions': [],
                'is_concentrating': False,
            }
            
            self.combatants.append(combatant)
            indices.append(len(self.combatants) - 1)
        
        return indices
    
    def roll_initiative(self) -> Dict[str, Any]:
        """Roll initiative for all combatants"""
        self.initiative_order = sorted(self.combatants, key=lambda x: x['initiative_roll'], reverse=True)
        self.current_turn_index = 0
        self.round_number = 1
        self.is_active = True
        
        return {
            'order': [(c['name'], c['initiative_roll'], c['initiative_natural']) for c in self.initiative_order],
            'current': self.initiative_order[0]['name'] if self.initiative_order else None,
        }
    
    def next_turn(self) -> Optional[Dict[str, Any]]:
        """Advance to the next turn"""
        if not self.is_active:
            return None
        
        self.current_turn_index = (self.current_turn_index + 1) % len(self.initiative_order)
        
        if self.current_turn_index == 0:
            self.round_number += 1
        
        current = self.initiative_order[self.current_turn_index]
        return {
            'name': current['name'],
            'round': self.round_number,
            'is_player': current['type'] == 'player',
            'current_hp': current['current_hp'],
            'max_hp': current['max_hp'],
            'armor_class': current['armor_class'],
            'conditions': current['conditions'],
        }
    
    def get_current_combatant(self) -> Optional[Dict[str, Any]]:
        """Get the current combatant"""
        if not self.is_active or not self.initiative_order:
            return None
        
        return self.initiative_order[self.current_turn_index]
    
    def end_combat(self) -> Dict[str, Any]:
        """End the combat encounter"""
        self.is_active = False
        defeated_enemies = []
        surviving_allies = []
        
        for c in self.combatants:
            if c['group'] == 'enemy' and c['current_hp'] <= 0:
                defeated_enemies.append(c['name'])
            elif c['group'] == 'player' and c['current_hp'] > 0:
                surviving_allies.append(c['name'])
        
        self.combatants = []
        self.initiative_order = []
        self.current_turn_index = 0
        self.round_number = 0
        
        return {
            'is_victorious': len(defeated_enemies) > 0 and all(c['current_hp'] <= 0 for c in self.combatants if c['group'] == 'enemy'),
            'defeated_enemies': defeated_enemies,
            'surviving_allies': surviving_allies,
        }


# =============================================================================
# Predefined Content
# =============================================================================

class ContentLibrary:
    """Library of predefined D&D content"""
    
    @staticmethod
    def get_weapons() -> Dict[str, Weapon]:
        """Return common weapons"""
        return {
            # Simple Melee Weapons
            "Club": Weapon("Club", "1d4", "bludgeoning", ["thrown"], is_simple=True, is_ranged=True, range_normal=20, range_long=60),
            "Dagger": Weapon("Dagger", "1d4", "piercing", ["finesse", "light", "thrown"], is_simple=True, is_finesse=True),
            "Greatclub": Weapon("Greatclub", "1d8", "bludgeoning", ["heavy", "two-handed"], is_simple=True),
            "Handaxe": Weapon("Handaxe", "1d6", "slashing", ["light", "thrown"], is_simple=True, is_ranged=True),
            "Javelin": Weapon("Javelin", "1d6", "piercing", ["thrown"], is_simple=True, is_ranged=True),
            "Light Hammer": Weapon("Light Hammer", "1d4", "bludgeoning", ["light", "thrown"], is_simple=True),
            "Mace": Weapon("Mace", "1d6", "bludgeoning", is_simple=True),
            "Quarterstaff": Weapon("Quarterstaff", "1d6", "bludgeoning", ["versatile"]),
            "Sickle": Weapon("Sickle", "1d4", "slashing", ["light"], is_simple=True),
            "Spear": Weapon("Spear", "1d6", "piercing", ["thrown", "versatile"], is_ranged=True),
            
            # Simple Ranged Weapons
            "Crossbow, Light": Weapon("Light Crossbow", "1d8", "piercing", ["ammunition", "loading", "two-handed"], is_simple=True, is_ranged=True, range_normal=80, range_long=320),
            "Dart": Weapon("Dart", "1d4", "piercing", ["finesse", "thrown"], is_simple=True, is_ranged=True),
            "Shortbow": Weapon("Shortbow", "1d6", "piercing", ["ammunition", "range", "two-handed"], is_simple=True, is_ranged=True, range_normal=80, range_long=320),
            "Sling": Weapon("Sling", "1d4", "bludgeoning", ["ammunition", "range"], is_simple=True, is_ranged=True, range_normal=30, range_long=120),
            
            # Martial Melee Weapons
            "Battleaxe": Weapon("Battleaxe", "1d8", "slashing", ["versatile"]),
            "Flail": Weapon("Flail", "1d8", "bludgeoning"),
            "Glaive": Weapon("Glaive", "1d10", "slashing", ["heavy", "reach", "two-handed"]),
            "Greataxe": Weapon("Greataxe", "1d12", "slashing", ["heavy", "two-handed"]),
            "Greatsword": Weapon("Greatsword", "2d6", "slashing", ["heavy", "two-handed"]),
            "Halberd": Weapon("Halberd", "1d10", "slashing", ["heavy", "reach", "two-handed"]),
            "Lance": Weapon("Lance", "1d12", "piercing", ["mounted", "reach", "special"]),
            "Longsword": Weapon("Longsword", "1d8", "slashing", ["versatile"]),
            "Maul": Weapon("Maul", "2d6", "bludgeoning", ["heavy", "two-handed"]),
            "Morningstar": Weapon("Morningstar", "1d8", "piercing"),
            "Pike": Weapon("Pike", "1d10", "piercing", ["heavy", "reach", "two-handed"]),
            "Rapier": Weapon("Rapier", "1d8", "piercing", ["finesse", "light"]),
            "Scimitar": Weapon("Scimitar", "1d6", "slashing", ["finesse", "light"]),
            "Shortsword": Weapon("Shortsword", "1d6", "piercing", ["finesse", "light"]),
            "Trident": Weapon("Trident", "1d8", "piercing", ["thrown", "versatile"]),
            "Warhammer": Weapon("Warhammer", "1d8", "bludgeoning", ["versatile"]),
            "Whip": Weapon("Whip", "1d4", "slashing", ["finesse", "reach", "special"]),
            
            # Martial Ranged Weapons
            "Crossbow, Hand": Weapon("Hand Crossbow", "1d6", "piercing", ["ammunition", "light", "loading"], is_ranged=True, range_normal=30, range_long=120),
            "Crossbow, Heavy": Weapon("Heavy Crossbow", "1d10", "piercing", ["ammunition", "heavy", "loading", "two-handed"], is_ranged=True, range_normal=100, range_long=400),
            "Longbow": Weapon("Longbow", "1d8", "piercing", ["ammunition", "heavy", "range", "two-handed"], is_ranged=True, range_normal=150, range_long=600),
            "Net": Weapon("Net", "0", "none", ["special", "thrown", "range"], is_ranged=True, range_normal=5, range_long=15),
        }
    
    @staticmethod
    def get_armors() -> Dict[str, Armor]:
        """Return common armor"""
        return {
            "Padded": Armor("Padded", 11, None, stealth_disadvantage=True, price=5, weight=15),
            "Leather": Armor("Leather", 11, None, price=10, weight=10),
            "Studded Leather": Armor("Studded Leather", 12, None, price=45, weight=13),
            "Hide": Armor("Hide", 12, 2, stealth_disadvantage=True, price=10, weight=12),
            "Chain Shirt": Armor("Chain Shirt", 13, 2, price=50, weight=20),
            "Half Plate": Armor("Half Plate", 15, 2, stealth_disadvantage=True, price=750, weight=40),
            "Ring Mail": Armor("Ring Mail", 14, 0, stealth_disadvantage=True, price=30, weight=40),
            "Chain Mail": Armor("Chain Mail", 16, 0, stealth_disadvantage=True, price=75, weight=55),
            "Splint": Armor("Splint", 17, 0, stealth_disadvantage=True, price=200, weight=60),
            "Plate": Armor("Plate", 18, 0, stealth_disadvantage=True, price=1500, weight=65),
        }
    
    @staticmethod
    def get_sample_monsters() -> Dict[str, Monster]:
        """Return some common monster templates"""
        return {
            "Orc": Monster(
                name="Orc",
                size="Medium",
                type="humanoid (orc)",
                alignment="chaotic evil",
                challenge_rating="1/8",
                xp=25,
                armor_class=13,
                hit_points=15,
                speed="30 ft.",
                str_score=15,
                dex_score=11,
                con_score=12,
                int_score=8,
                wis_score=9,
                cha_score=8,
                skills={"Intimidation": 3, "Perception": 1},
                challenge_rating_xp="1/8 (25 XP)",
                traits=["Aggressive"],
                actions=["Greataxe"],
            ),
            "Goblin": Monster(
                name="Goblin",
                size="Small",
                type="humanoid (goblinoid)",
                alignment="neutral evil",
                challenge_rating="1/4",
                xp=50,
                armor_class=15,
                hit_points=7,
                speed="30 ft.",
                str_score=8,
                dex_score=14,
                con_score=10,
                int_score=10,
                wis_score=8,
                cha_score=8,
                skills={"Stealth": 6, "Perception": 1},
                challenge_rating_xp="1/4 (50 XP)",
                actions=["Scimitar", "Shortbow"],
            ),
            "Skeleton": Monster(
                name="Skeleton",
                size="Medium",
                type="undead",
                alignment="lawful evil",
                challenge_rating="1/4",
                xp=50,
                armor_class=13,
                hit_points=13,
                speed="30 ft.",
                str_score=10,
                dex_score=14,
                con_score=15,
                int_score=6,
                wis_score=8,
                cha_score=7,
                skills={"Perception": 1},
                damage_resistances=["bludgeoning", "piercing"],
                damage_immunities=["poison"],
                condition_immunities=["poisoned"],
                senses="Darkvision 60 ft., passive Perception 11",
                languages="understands all languages it knew in life but can't speak",
                challenge_rating_xp="1/4 (50 XP)",
                actions=["Shortsword", "Shortbow"],
            ),
        }


# =============================================================================
# Utility Functions
# =============================================================================

def generate_ability_scores(racial_bonuses: Dict[str, int] = None) -> Dict[str, int]:
    """
    Generate 6 ability scores using 4d6 drop lowest method
    Apply racial bonuses if provided
    """
    racials = racial_bonuses or {}
    scores = {}
    
    for ability in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
        # Roll 4d6
        dice = [random.randint(1, 6) for _ in range(4)]
        dice.remove(min(dice))  # Drop lowest
        score = sum(dice)
        # Apply racial bonus
        bonus = racials.get(ability, 0)
        scores[ability] = score + bonus
    
    return scores


def calculate_modifier(score: int) -> int:
    """Calculate ability modifier from score"""
    return (score - 10) // 2


def initiative_bonus(dex_mod: int, proficiency_bonus: int = 0, has_alertness: bool = False) -> Tuple[int, int]:
    """Calculate initiative bonus"""
    bonus = dex_mod + (proficiency_bonus if has_alertness else 0)
    roll, _ = roll_d20()
    total = roll + bonus
    return total, roll


def calculate_encounter_difficulty(characters: List[Character], monster_xp_list: List[int]) -> Dict[str, Any]:
    """Calculate encounter difficulty using bounded accuracy"""
    total_party_xp = sum(monster_xp_list)
    avg_party_level = sum(c.level for c in characters) / len(characters)
    
    # Adjust for party size
    multiplier = 1.0
    if len(characters) == 1:
        multiplier = 1.5
    elif len(characters) == 2:
        multiplier = 1.25
    elif len(characters) <= 4:
        multiplier = 1.0
    elif len(characters) >= 5:
        multiplier = 0.8
    
    adjusted_xp = total_party_xp * multiplier
    
    # Determine difficulty
    thresholds = {
        'Easy': avg_party_level * 25,
        'Medium': avg_party_level * 50,
        'Hard': avg_party_level * 75,
        'Deadly': avg_party_level * 100,
    }
    
    difficulty = "Trivial"
    for level_name, threshold in [(k, v) for k, v in thresholds.items()]:
        if adjusted_xp >= threshold:
            difficulty = level_name
        else:
            break
    
    return {
        'total_party_xp': total_party_xp,
        'adjusted_xp': adjusted_xp,
        'difficulty': difficulty,
        'avg_party_level': avg_party_level,
        'party_size_multiplier': multiplier,
    }


def format_character_sheet(character: Character) -> str:
    """Format character sheet as readable text"""
    mods = character.ability_modifiers
    
    lines = [
        f"### {character.name} - Level {character.level} {character.class_name}",
        f"**Race:** {character.race}  |  **Background:** {character.background}",
        f"**Player:** {character.player_name}",
        "",
        "#### Ability Scores",
        f"| STR | DEX | CON | INT | WIS | CHA |",
        f"|-----|-----|-----|-----|-----|-----|",
        f"| {character.strength} ({mods['STR']:+}) | {character.dexterity} ({mods['DEX']:+}) | {character.constitution} ({mods['CON']:+}) | {character.intelligence} ({mods['INT']:+}) | {character.wisdom} ({mods['WIS']:+}) | {character.charisma} ({mods['CHA']:+}) |",
        "",
        f"**HP:** {character.current_hp}/{character.max_hp}  |  **AC:** {character.armor_class}  |  **Speed:** {character.speed} ft",
        f"**Initiative:** {character.initiative:+.2f}  |  **Proficiency Bonus:** +{character.proficiency_bonus}",
        f"**Passive Perception:** {character.passive_perception}  |  **Passive Insight:** {character.passive_insight}",
    ]
    
    if character.conditions:
        lines.append("")
        lines.append(f"**Conditions:** {', '.join(c.value if hasattr(c, 'value') else str(c) for c in character.conditions)}")
    
    if character.inventory:
        lines.append("")
        lines.append(f"**Inventory:** {', '.join(character.inventory)}")
    
    return "\n".join(lines)


# =============================================================================
# D&D Agent
# =============================================================================

class DnDAgent:
    """
    The main D&D 5e agent that facilitates gameplay

    This agent can:
    - Handle dice rolls and ability checks (interactive or automatic)
    - Manage character sheets
    - Facilitate combat encounters
    - Reference rulebook content
    - Generate random content
    """
    
    def __init__(self, session_file: str = "dnd_session.json"):
        self.session_file = session_file
        self.characters: Dict[str, Character] = {}
        self.encounter_manager = EncounterManager()
        self.content_library = ContentLibrary()
        self.weapons = self.content_library.get_weapons()
        self.armors = self.content_library.get_armors()
        self.monsters = self.content_library.get_sample_monsters()
        self.history: List[Dict[str, Any]] = []
        self._load_session()
    
    def _save_session(self):
        """Save current session data"""
        session_data = {
            'characters': {name: asdict(char) for name, char in self.characters.items()},
            'history': self.history[-100:],  # Keep last 100 entries
        }
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
        except Exception:
            pass  # Session saving is optional
    
    def _load_session(self):
        """Load session data from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                for name, char_data in data.get('characters', {}).items():
                    self.characters[name] = Character(**char_data)
                self.history = data.get('history', [])
        except Exception:
            pass  # Session loading is optional
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log an action to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details or {}
        }
        self.history.append(entry)
        self._save_session()
    
    def create_character(self, name: str, race: str, class_name: str, 
                        ability_scores: Dict[str, int] = None,
                        level: int = 1, background: str = "") -> Character:
        """Create a new character"""
        if ability_scores is None:
            ability_scores = generate_ability_scores()
        
        character = Character(
            name=name,
            race=race,
            class_name=class_name,
            level=level,
            background=background,
            strength=ability_scores['STR'],
            dexterity=ability_scores['DEX'],
            constitution=ability_scores['CON'],
            intelligence=ability_scores['INT'],
            wisdom=ability_scores['WIS'],
            charisma=ability_scores['CHA'],
        )
        
        # Calculate HP
        class_hit_dice = {
            'Barbarian': 12, 'Fighter': 10, 'Paladin': 10, 'Ranger': 10,
            'Bard': 8, 'Cleric': 8, 'Druid': 8, 'Monk': 8, 'Rogue': 8, 'Warlock': 8,
            'Sorcerer': 6, 'Wizard': 6,
        }
        hit_die = class_hit_dice.get(class_name, 8)
        const_mod = character.ability_modifiers['CON']
        character.max_hp = max(1, hit_die + const_mod)
        character.current_hp = character.max_hp
        character.hit_dice = f"d{hit_die}"
        
        # Calculate AC (unarmored)
        dex_mod = character.ability_modifiers['DEX']
        character.armor_class = 10 + dex_mod
        
        # Set proficiency bonus
        # D&D 5e ProfBonus scaling: 1-4: +2, 5-8: +3, 9-12: +4, 13-16: +5, 17-20: +6
        if level <= 4:
            character.proficiency_bonus = 2
        elif level <= 8:
            character.proficiency_bonus = 3
        elif level <= 12:
            character.proficiency_bonus = 4
        elif level <= 16:
            character.proficiency_bonus = 5
        else:
            character.proficiency_bonus = 6
        
        # Calculate initiative
        character.initiative = dex_mod + character.proficiency_bonus * 0.1  # Small bonus for proficiency awareness
        
        self.characters[name] = character
        self.log_action("create_character", {'name': name, 'class': class_name, 'race': race})
        
        return character
    
    def make_ability_check(self, character_name: str, ability: str, 
                          skill: str = None, advantage: bool = False, 
                          disadvantage: bool = False, interactive: bool = False) -> Dict[str, Any]:
        """
        Make an ability check with optional skill and advantage/disadvantage
        
        Args:
            character_name: Name of character making check
            ability: Ability (STR, DEX, CON, INT, WIS, CHA)
            skill: Optional skill name (e.g., "perception", "history")
            advantage: Whether to roll with advantage
            disadvantage: Whether to roll with disadvantage
            interactive: Whether to prompt for physical dice input
        """
        character = self.characters.get(character_name)
        if not character:
            return {"error": f"Character '{character_name}' not found"}
        
        mods = character.ability_modifiers
        ability_mod = mods.get(ability.upper(), 0)
        
        # Check for skill proficiency
        skill_mod = 0
        skill_name = skill.lower() if skill else None
        if skill_name:
            skill_map = {s.value: s for s in Skill}
            if skill_name in skill_map:
                skill_obj = skill_map[skill_name]
                skill_mod = character._get_skill_bonus(skill_obj) - ability_mod  # Extract just the skill portion
        
        total_modifier = ability_mod + skill_mod
        roll_val, rolls = roll_d20(advantage=advantage, disadvantage=disadvantage, interactive=interactive)
        total = roll_val + total_modifier
        
        result = {
            'character': character_name,
            'ability': ability,
            'skill': skill,
            'roll': roll_val,
            'natural': rolls[0],
            'modifier': total_modifier,
            'total': total,
            'is_advantage': advantage,
            'is_disadvantage': disadvantage,
            'is_critical': rolls[0] == 20 or rolls[-1] == 20,
            'is_critical_failure': rolls[0] == 1 and rolls[-1] == 1,
            'breakdown': f"d20 ({rolls[0]}) + {total_modifier} = {total}",
        }
        
        self.log_action("ability_check", result)
        return result
    
    def make_saving_throw(self, character_name: str, ability: str,
                         dc: int = None, advantage: bool = False,
                         disadvantage: bool = False, interactive: bool = False) -> Dict[str, Any]:
        """Make a saving throw"""
        character = self.characters.get(character_name)
        if not character:
            return {"error": f"Character '{character_name}' not found"}
        
        save_result = character.make_save(ability.lower())
        
        if dc is not None:
            save_result['dc'] = dc
            save_result['success'] = save_result['total'] >= dc
            save_result['is_critical_success'] = save_result['natural'] == 20
            save_result['is_critical_failure'] = save_result['natural'] == 1
        
        self.log_action("saving_throw", save_result)
        return save_result
    
    def roll_initiative_for_party(self, character_names: List[str]) -> Dict[str, Any]:
        """Roll initiative for a party of characters"""
        results = {}
        for name in character_names:
            character = self.characters.get(name)
            if character:
                self.encounter_manager.add_character(character)
                combatant = self.encounter_manager.combatants[-1]
                results[name] = {
                    'initiative': combatant['initiative_roll'],
                    'roll': combatant['initiative_natural'],
                    'modifier': combatant['initiative_modifier'],
                }
        
        if len(self.encounter_manager.combatants) > 1:
            init_order = self.encounter_manager.roll_initiative()
            results['order'] = init_order
        
        self.log_action("initiative_roll", results)
        return results
    
    def roll_ability_scores(self, method: str = "4d6_drop_lowest", count: int = 6) -> Dict[str, int]:
        """Roll ability scores for character creation"""
        scores = {}
        abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        
        for ability in abilities:
            if method == "4d6_drop_lowest":
                dice = [random.randint(1, 6) for _ in range(4)]
                dice.remove(min(dice))
                score = sum(dice)
            elif method == "3d6":
                score = sum(random.randint(1, 6) for _ in range(3))
            else:
                score = 10  # Default
            
            scores[ability] = score
        
        self.log_action("roll_ability_scores", {'method': method, 'scores': scores})
        return scores
    
    def describe_encounter(self, environment: str = "dungeon") -> str:
        """Generate a descriptive encounter description"""
        descriptions = {
            'dungeon': [
                "The torchlight flickers against cold stone walls, casting dancing shadows that seem almost alive. Ancient runes carved into the walls glow with a faint blue light, humming with residual magic. You hear the distant echo of dripping water somewhere in the depths below.",
                "Moss-covered stone steps wind down into darkness. The air is damp and carries the scent of mildew. Strange scratches mark the walls at irregular intervals, clearly made by something with sharp claws.",
                "The chamber opens before you, dominated by a massive statue of a forgotten king. Dust blankets everything, disturbed only by recent footprints that lead toward the altar at the far end of the room.",
            ],
            'forest': [
                "Towering trees form a natural cathedral, their canopy filtering sunlight into ethereal beams. The forest hushes as you enter—a moment of perfect stillness broken only by the distant call of an owl. Something watches from the shadows between the trunks.",
                "The path winds through a grove of ancient trees, their roots twisting like sleeping serpents. Autumn leaves crunch underfoot, and the air carries the sharp scent of pine and something else... something sweet and dangerous.",
                "A mist clings to the forest floor, making each step uncertain. Strange mushrooms glow faintly in the dim light, and you notice claw marks high up on the tree trunks—far too high for any ordinary beast to have made them.",
            ],
            'city': [
                "The cobblestone street glistens with rain from the evening's storm. Gas lamps cast pools of yellow light that barely penetrate the perpetual fog. Behind you, the tavern's warm glow seems almost inviting, but the shadows in the alleyways move with purpose.",
                "Merchants call out their wares in the bustling market square, but their voices carry an edge of nervousness. Several stalls stand empty, their owners having packed up and fled. Something unsettles the regulars, and you can sense eyes watching your every move.",
                "The noble quarter's imposing buildings cast long shadows across manicured gardens. Guards patrol with increased alertness despite their bored expressions. A messenger just delivered an important-sealed letter to the mansion at the end of the street, and the occupants didn't look pleased.",
            ],
            'tavern': [
                "The tavern buzzes with conversation, but you notice a group of rough-looking mercenaries eyeing your table from across the room. The bartender wipes down glasses with mechanical precision, but his eyes keep darting toward the backdoor. A fire crackles merrily in the hearth, though it does little against the tension in the air.",
                "The common room is nearly empty save for a few lone travelers nursing drinks at the bar. One cloaked figure in the corner hasn't moved or spoken since their arrival, but you catch glimpses of parchment covered in strange symbols beneath their hood. The innkeeper avoids looking directly at them.",
                "The dining area fills with the smell of roasting meat and fresh bread, but the atmosphere is tense. Two nobles at the lord's table argue in hushed tones about politics, while the barkeep subtly slides an extra drink to the largest patron at closing time.",
            ],
        }
        
        table = descriptions.get(environment.lower(), descriptions['dungeon'])
        return random.choice(table)
    
    def roll_on_table(self, table_name: str) -> str:
        """Roll on various D&D random tables"""
        tables = {
            'tavern_patron': [
                "A nervous merchant counting coin",
                "A cloaked traveler with secrets",
                "An off-duty city guard",
                "A traveling minstrel",
                "A noble in disguise",
                "An old soldier with war stories",
                "A nervous scholar with ancient texts",
                "A drunk who knows more than they seem",
            ],
            'weather': [
                "Clear skies, pleasant temperature",
                "Light rain, muddy ground",
                "Thunderstorm, difficult terrain",
                "Heavy fog, visibility 10 feet",
                "Snowfall, difficult terrain",
                "Strong winds, ranged attacks at disadvantage",
            ],
            'dungeon_encounter': [
                "A pair of guard drakes blocking the corridor",
                "A group of goblins arguing over treasure",
                "An old hermit who's been here for years",
                "A trapped treasure room with a skeleton",
                "A rival adventuring party",
                "An ancient shrine with divine magic",
                "A collapsed tunnel with fresh footprints",
                "A mysterious portal pulsing with energy",
            ],
            'treasure': [
                "A beautifully crafted longsword with strange runes",
                "A potion of healing (2 doses)",
                "A scroll with a mysterious spell",
                "A gemstone worth 50gp",
                "An ancient coin from a lost kingdom",
                "A map to a hidden location",
                "A ring that glows faintly in darkness",
                "A book of blank pages that write themselves",
            ],
        }
        
        if table_name not in tables:
            return f"Unknown table: {table_name}"
        
        table = tables[table_name]
        return random.choice(table)


# =============================================================================
# Encounter & Content Generation (Module-level aliases)
# =============================================================================

_encounter_descriptions = {
    'dungeon': [
        "The torchlight flickers against cold stone walls, casting dancing shadows that seem almost alive. Ancient runes carved into the walls glow with a faint blue light, humming with residual magic. You hear the distant echo of dripping water somewhere in the depths below.",
        "Moss-covered stone steps wind down into darkness. The air is damp and carries the scent of mildew. Strange scratches mark the walls at irregular intervals, clearly made by something with sharp claws.",
        "The chamber opens before you, dominated by a massive statue of a forgotten king. Dust blankets everything, disturbed only by recent footprints that lead toward the altar at the far end of the room.",
    ],
    'forest': [
        "Towering trees form a natural cathedral, their canopy filtering sunlight into ethereal beams. The forest hushes as you enter—a moment of perfect stillness broken only by the distant call of an owl. Something watches from the shadows between the trunks.",
        "The path winds through a grove of ancient trees, their roots twisting like sleeping serpents. Autumn leaves crunch underfoot, and the air carries the sharp scent of pine and something else... something sweet and dangerous.",
        "A mist clings to the forest floor, making each step uncertain. Strange mushrooms glow faintly in the dim light, and you notice claw marks high up on the tree trunks—far too high for any ordinary beast to have made them.",
    ],
    'city': [
        "The cobblestone street glistens with rain from the evening's storm. Gas lamps cast pools of yellow light that barely penetrate the perpetual fog. Behind you, the tavern's warm glow seems almost inviting, but the shadows in the alleyways move with purpose.",
        "Merchants call out their wares in the bustling market square, but their voices carry an edge of nervousness. Several stalls stand empty, their owners having packed up and fled. Something unsettles the regulars, and you can sense eyes watching your every move.",
        "The noble quarter's imposing buildings cast long shadows across manicured gardens. Guards patrol with increased alertness despite their bored expressions. A messenger just delivered an important-sealed letter to the mansion at the end of the street, and the occupants didn't look pleased.",
    ],
    'tavern': [
        "The tavern buzzes with conversation, but you notice a group of rough-looking mercenaries eyeing your table from across the room. The bartender wipes down glasses with mechanical precision, but his eyes keep darting toward the backdoor. A fire crackles merrily in the hearth, though it does little against the tension in the air.",
        "The common room is nearly empty save for a few lone travelers nursing drinks at the bar. One cloaked figure in the corner hasn't moved or spoken since their arrival, but you catch glimpses of parchment covered in strange symbols beneath their hood. The innkeeper avoids looking directly at them.",
        "The dining area fills with the smell of roasting meat and fresh bread, but the atmosphere is tense. Two nobles at the lord's table argue in hushed tones about politics, while the barkeep subtly slides an extra drink to the largest patron at closing time.",
    ],
}

_random_tables = {
    'tavern_patron': [
        "A nervous merchant counting coin",
        "A cloaked traveler with secrets",
        "An off-duty city guard",
        "A traveling minstrel",
        "A noble in disguise",
        "An old soldier with war stories",
        "A nervous scholar with ancient texts",
        "A drunk who knows more than they seem",
    ],
    'weather': [
        "Clear skies, pleasant temperature",
        "Light rain, muddy ground",
        "Thunderstorm, difficult terrain",
        "Heavy fog, visibility 10 feet",
        "Snowfall, difficult terrain",
        "Strong winds, ranged attacks at disadvantage",
    ],
    'dungeon_encounter': [
        "A pair of guard drakes blocking the corridor",
        "A group of goblins arguing over treasure",
        "An old hermit who's been here for years",
        "A trapped treasure room with a skeleton",
        "A rival adventuring party",
        "An ancient shrine with divine magic",
        "A collapsed tunnel with fresh footprints",
        "A mysterious portal pulsing with energy",
    ],
    'treasure': [
        "A beautifully crafted longsword with strange runes",
        "A potion of healing (2 doses)",
        "A scroll with a mysterious spell",
        "A gemstone worth 50gp",
        "An ancient coin from a lost kingdom",
        "A map to a hidden location",
        "A ring that glows faintly in darkness",
        "A book of blank pages that write themselves",
    ],
}


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Command-line interface for the D&D agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='D&D 5e Dungeon Master Agent')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Roll command (with interactive option)
    roll_parser = subparsers.add_parser('roll', help='Roll dice')
    roll_parser.add_argument('dice', help='Dice notation (e.g., 2d6+3, 1d20, d100)')
    roll_parser.add_argument('--interactive', '-i', action='store_true', help='Prompt for physical dice')
    
    # Check command (with interactive option)
    check_parser = subparsers.add_parser('check', help='Make an ability check')
    check_parser.add_argument('character', help='Character name')
    check_parser.add_argument('ability', choices=['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'])
    check_parser.add_argument('--skill', '-s', help='Optional skill')
    check_parser.add_argument('--advantage', '-a', action='store_true')
    check_parser.add_argument('--disadvantage', '-d', action='store_true')
    check_parser.add_argument('--interactive', '-i', action='store_true', help='Prompt for physical dice')
    
    # Save command (with interactive option)
    save_parser = subparsers.add_parser('save', help='Make a saving throw')
    save_parser.add_argument('character', help='Character name')
    save_parser.add_argument('ability', choices=['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'])
    save_parser.add_argument('--dc', '-c', type=int, help='Difficulty class')
    save_parser.add_argument('--advantage', '-a', action='store_true')
    save_parser.add_argument('--disadvantage', '-d', action='store_true')
    save_parser.add_argument('--interactive', '-i', action='store_true', help='Prompt for physical dice')
    
    # Character command
    char_parser = subparsers.add_parser('create-character', help='Create a character')
    char_parser.add_argument('name', help='Character name')
    char_parser.add_argument('race', help='Character race')
    char_parser.add_argument('class_name', help='Character class')
    char_parser.add_argument('--level', '-l', type=int, default=1)
    char_parser.add_argument('--background', '-b', default='')
    
    # Initiative command
    init_parser = subparsers.add_parser('initiative', help='Roll initiative')
    init_parser.add_argument('characters', nargs='+', help='Character names')
    
    # Roll stats command
    stats_parser = subparsers.add_parser('roll-stats', help='Roll ability scores')
    stats_parser.add_argument('--method', choices=['4d6_drop_lowest', '3d6'], default='4d6_drop_lowest')
    
    # Encounter command
    enc_parser = subparsers.add_parser('encounter', help='Generate encounter description')
    enc_parser.add_argument('environment', choices=['dungeon', 'forest', 'city', 'tavern'], default='dungeon')
    
    # Table command
    table_parser = subparsers.add_parser('table', help='Roll on random table')
    table_parser.add_argument('table_name', choices=['tavern_patron', 'weather', 'dungeon_encounter'], default='tavern_patron')
    
    args = parser.parse_args()
    
    # Initialize the agent
    agent = DnDAgent()
    
    if args.command == 'roll':
        print(parse_dice_notation(args.dice, interactive=args.interactive))
    elif args.command == 'check':
        result = agent.make_ability_check(args.character, args.ability, args.skill, 
                                         args.advantage, args.disadvantage, args.interactive)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"🎲 {args.character} makes a {args.ability}" +
                  (f" ({args.skill})" if args.skill else ""))
            print(f"   d20 roll: {result['natural']}" +
                  (" (advantage)" if args.advantage else ""))
            print(f"   Modifier: {result['modifier']:+d}")
            print(f"   Total: {result['total']}")
            if result['is_critical']:
                print(f"   🎯 Critical success!")
            elif result['is_critical_failure']:
                print(f"   💥 Critical failure!")
    elif args.command == 'save':
        result = agent.make_saving_throw(args.character, args.ability, args.dc, 
                                        args.advantage, args.disadvantage, args.interactive)
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"🛡️ {args.character} saving throw: {args.ability}")
            print(f"   d20 roll: {result.get('natural', result.get('roll', '?'))}")
            print(f"   Total: {result.get('total', '?')}")
            if args.dc:
                success = result.get('success', False)
                print(f"   DC {args.dc}: {'✅ Success' if success else '❌ Failure'}")
    elif args.command == 'create-character':
        scores = agent.roll_ability_scores()
        character = agent.create_character(
            name=args.name,
            race=args.race,
            class_name=args.class_name,
            ability_scores=scores,
            level=args.level,
            background=args.background
        )
        print(format_character_sheet(character))
    elif args.command == 'initiative':
        result = agent.roll_initiative_for_party(args.characters)
        print("🎲 Initiative Order:")
        for name, info in result.items():
            if name == 'order':
                continue
            print(f"   {name}: {info['initiative']} (rolled {info['roll']}, modifier {info['modifier']:+d})")
        if 'order' in result:
            print(f"\n   Initiative order: {result['order']['order']}")
            print(f"   First turn: {result['order']['current']}")
    elif args.command == 'roll-stats':
        scores = agent.roll_ability_scores(args.method)
        print(f"🎲 {args.method.replace('_', ' ').title()} Result:")
        print(f"   STR: {scores['STR']} ({calculate_modifier(scores['STR']):+d})")
        print(f"   DEX: {scores['DEX']} ({calculate_modifier(scores['DEX']):+d})")
        print(f"   CON: {scores['CON']} ({calculate_modifier(scores['CON']):+d})")
        print(f"   INT: {scores['INT']} ({calculate_modifier(scores['INT']):+d})")
        print(f"   WIS: {scores['WIS']} ({calculate_modifier(scores['WIS']):+d})")
        print(f"   CHA: {scores['CHA']} ({calculate_modifier(scores['CHA']):+d})")
    elif args.command == 'encounter':
        print(agent.describe_encounter(args.environment))
    elif args.command == 'table':
        print(agent.roll_on_table(args.table_name))


if __name__ == '__main__':
    main()