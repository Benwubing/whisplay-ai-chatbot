#!/usr/bin/env python3
"""
Simple interactive D&D 5e session runner
Supports both virtual dice (agent rolls) and physical dice (player enters results)
"""

from dnd_agent import *

def main():
    print("🎲 Welcome to the D&D 5e Interactive Session Runner!")
    print("=" * 50)
    
    # Create agents
    agent = DnDAgent()
    
    # Ask to create characters
    print("\nLet's create your party!")
    while True:
        name = input("\nCharacter name (or 'done' to continue): ")
        if name.lower() == 'done':
            break
        
        race = input("Race: ")
        class_name = input("Class: ")
        level_input = input("Level (default 1): ")
        level = int(level_input) if level_input else 1
        background = input("Background (optional): ")
        
        # Ask for dice rolling preference
        print("\nHow would you like to roll for ability scores?")
        print("  1. Virtual (agent rolls automatically)")
        print("  2. Physical (enter your own rolls)")
        roll_preference = input("Choice (1 or 2): ").strip()
        use_physical = roll_preference == '2'
        
        # Roll for stats
        if use_physical:
            print("\nEnter your physical ability score rolls (4d6 drop lowest for each):")
            scores = {}
            abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
            for ability in abilities:
                print(f"\n  {ability} - Roll 4d6 and drop the lowest:")
                rolls = []
                for i in range(4):
                    while True:
                        try:
                            val = input(f"    Die {i+1} (1-6): ").strip()
                            roll_val = int(val)
                            if 1 <= roll_val <= 6:
                                rolls.append(roll_val)
                                break
                            else:
                                print(f"    Invalid! Must be between 1 and 6")
                        except ValueError:
                            print("    Please enter a valid number 1-6")
                
                rolls_display = sorted(rolls, reverse=True)
                dropped = min(rolls)
                total = sum(rolls) - dropped
                print(f"    Roll: {sorted(rolls, reverse=True)} → Drop {dropped} → Total: {total}")
                scores[ability] = total
        else:
            print("\nRolling ability scores (4d6 drop lowest)...")
            scores = agent.roll_ability_scores()
        
        character = agent.create_character(name, race, class_name, scores, level, background)
        print(f"\nCharacter created!")
        print(format_character_sheet(character))
    
    if not agent.characters:
        print("\nNo characters created. Starting with no party...")
        print("You can create characters with: create <name> <race> <class>")
    
    print("\n" + "=" * 50)
    print("Your party is ready! What would you like to do?")
    
    while True:
        print("\nCommands:")
        print("  roll <dice> [-i]       - Roll dice (use -i for physical dice)")
        print("  check <char> <ability> [<skill>] [-a/-d] [-i] - Ability check")
        print("  save <char> <ability> [dc] [-a/-d] [-i] - Saving throw")
        print("  stats <char> - Show character sheet")
        print("  encounter [env] - Generate encounter description")
        print("  table <name> - Roll on random table")
        print("  help - Show this help")
        print("  quit - Exit session")
        
        command = input("\n> ").strip()
        if not command:
            continue
        
        parts = command.split()
        cmd = parts[0].lower()
        
        # Check for interactive flag
        interactive = '-i' in parts
        # Remove the -i flag from parts
        parts = [p for p in parts if p != '-i']
        
        # Check for advantage/disadvantage flags
        advantage = '-a' in parts
        disadvantage = '-d' in parts
        parts = [p for p in parts if p not in ['-a', '-d']]
        
        if cmd == 'quit':
            print("Thanks for playing! Session saved.")
            break
        
        elif cmd == 'help':
            print("\nCommands:")
            print("  roll <dice> [-i]       - Roll dice (use -i for physical dice)")
            print("  check <char> <ability> [<skill>] [-a/-d] [-i] - Ability check")
            print("  save <char> <ability> [dc] [-a/-d] [-i] - Saving throw")
            print("  stats <char> - Show character sheet")
            print("  encounter [env] - Generate encounter description")
            print("  table <name> - Roll on random table")
            print("  help - Show this help")
            print("  quit - Exit session")
        
        elif cmd == 'roll':
            if len(parts) < 2:
                print("Usage: roll <dice notation> [-i for physical dice]")
                continue
            dice = ' '.join(parts[1:])
            result = parse_dice_notation(dice, interactive=interactive)
            print(result)
        
        elif cmd == 'check':
            if len(parts) < 3:
                print("Usage: check <character> <ability> [skill] [-a/-d] [-i]")
                continue
            char_name = parts[1]
            ability = parts[2].upper()
            skill = parts[3] if len(parts) > 3 else None
            
            # If more than 3 parts, check if 4th is a skill or flag
            extra_parts = parts[3:] if len(parts) > 3 else []
            
            result = agent.make_ability_check(
                char_name, ability, skill,
                advantage=advantage,
                disadvantage=disadvantage,
                interactive=interactive
            )
            
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                mode_str = ""
                if interactive:
                    mode_str = " [physical dice]"
                elif advantage:
                    mode_str = " [advantage]"
                elif disadvantage:
                    mode_str = " [disadvantage]"
                
                print(f"🎲 {char_name} makes a {ability}" +
                      (f" ({skill})" if skill else "") + mode_str)
                print(f"   d20 roll: {result['natural']}" +
                      (" (advantage)" if result['is_advantage'] else ""))
                print(f"   Modifier: {result['modifier']:+d}")
                print(f"   Total: {result['total']}")
                if result['is_critical']:
                    print(f"   🎯 Critical success!")
                elif result['is_critical_failure']:
                    print(f"   💥 Critical failure!")
        
        elif cmd == 'save':
            if len(parts) < 3:
                print("Usage: save <character> <ability> [dc] [-a/-d] [-i]")
                continue
            char_name = parts[1]
            ability = parts[2].upper()
            dc = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else None
            
            result = agent.make_saving_throw(
                char_name, ability.lower(), dc,
                advantage=advantage,
                disadvantage=disadvantage,
                interactive=interactive
            )
            
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                mode_str = ""
                if interactive:
                    mode_str = " [physical dice]"
                elif advantage:
                    mode_str = " [advantage]"
                elif disadvantage:
                    mode_str = " [disadvantage]"
                
                print(f"🛡️ {char_name} saving throw: {ability}{mode_str}")
                print(f"   d20 roll: {result.get('natural', result.get('roll', '?'))}")
                print(f"   Total: {result.get('total', '?')}")
                if dc:
                    success = result.get('success', False)
                    print(f"   DC {dc}: {'✅ Success' if success else '❌ Failure'}")
        
        elif cmd == 'stats':
            if len(parts) < 2:
                print("Usage: stats <character name>")
                continue
            char_name = parts[1]
            character = agent.characters.get(char_name)
            if character:
                print(format_character_sheet(character))
            else:
                print(f"Character '{char_name}' not found")
        
        elif cmd == 'encounter':
            env = parts[1] if len(parts) > 1 else 'dungeon'
            if hasattr(agent, 'describe_encounter'):
                print(f"\n📍 {env.title()} Encounter:\n{agent.describe_encounter(env)}")
            else:
                print("Encounter generation not available")
        
        elif cmd == 'table':
            table_name = parts[1] if len(parts) > 1 else 'tavern_patron'
            if hasattr(agent, 'roll_on_table'):
                print(f"\n📜 Rolled on '{table_name}':\n   {agent.roll_on_table(table_name)}")
            else:
                print("Random tables not available")
        
        elif cmd == 'create':
            if len(parts) < 4:
                print("Usage: create <name> <race> <class> [--level N] [--bg background]")
                continue
            name = parts[1]
            race = parts[2]
            class_name = parts[3]
            
            level = 1
            bg = ""
            i = 4
            while i < len(parts):
                if parts[i] == '--level':
                    level = int(parts[i+1])
                    i += 2
                elif parts[i] == '--bg':
                    bg = parts[i+1]
                    i += 2
                else:
                    i += 1
            
            if agent.characters:
                # Use first character's stats as template
                pass
            
            scores = agent.roll_ability_scores()
            character = agent.create_character(name, race, class_name, scores, level, bg)
            print(format_character_sheet(character))
        
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")


if __name__ == '__main__':
    main()