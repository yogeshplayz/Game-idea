"""
Roguelike Fighting System
A comprehensive combat system with leveling, equipment, and magical items
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class ItemRarity(Enum):
    """Item rarity levels"""
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


@dataclass
class Weapon:
    """Weapon item with damage stats"""
    name: str
    base_damage: int
    crit_chance: float
    rarity: ItemRarity
    
    def get_damage(self) -> int:
        """Calculate weapon damage with crit chance"""
        base = self.base_damage * self.rarity.value
        if random.random() < self.crit_chance:
            return int(base * 1.5)  # Critical hit
        return base


@dataclass
class Armor:
    """Armor item with defense stats"""
    name: str
    defense: int
    rarity: ItemRarity
    
    def get_defense(self) -> int:
        """Calculate armor defense"""
        return self.defense * self.rarity.value


@dataclass
class Accessory:
    """Accessory items with special effects"""
    name: str
    bonus_type: str  # 'health', 'damage', 'defense', 'crit'
    bonus_value: float
    rarity: ItemRarity


@dataclass
class Scroll:
    """Magic scrolls with special abilities"""
    name: str
    effect_type: str  # 'heal', 'damage_boost', 'shield', 'curse'
    power: int
    rarity: ItemRarity
    
    def cast(self) -> int:
        """Cast the scroll and return effect power"""
        return self.power * self.rarity.value


class Character:
    """Player or enemy character in combat"""
    
    def __init__(self, name: str, base_health: int = 100):
        self.name = name
        self.max_health = base_health
        self.current_health = base_health
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100
        
        # Equipment slots
        self.weapon: Optional[Weapon] = None
        self.armor: Optional[Armor] = None
        self.accessories: List[Accessory] = []
        self.scrolls: List[Scroll] = []
        
        # Combat stats
        self.base_damage = 10
        self.base_defense = 5
        self.strength = 1.0
        self.agility = 1.0
    
    def equip_weapon(self, weapon: Weapon) -> None:
        """Equip a weapon"""
        self.weapon = weapon
    
    def equip_armor(self, armor: Armor) -> None:
        """Equip armor"""
        self.armor = armor
    
    def add_accessory(self, accessory: Accessory) -> None:
        """Add an accessory (can have multiple)"""
        if len(self.accessories) < 3:  # Max 3 accessories
            self.accessories.append(accessory)
    
    def add_scroll(self, scroll: Scroll) -> None:
        """Add a scroll to inventory"""
        self.scrolls.append(scroll)
    
    def gain_experience(self, amount: int) -> None:
        """Gain experience and level up if threshold reached"""
        self.experience += amount
        
        while self.experience >= self.experience_to_level:
            self.level_up()
    
    def level_up(self) -> None:
        """Increase character level and stats"""
        self.level += 1
        self.experience -= self.experience_to_level
        self.experience_to_level = int(self.experience_to_level * 1.1)
        
        # Stat increases
        self.max_health += 20
        self.current_health = self.max_health
        self.base_damage += 5
        self.base_defense += 2
        self.strength += 0.1
        self.agility += 0.05
        
        print(f"{self.name} leveled up to {self.level}!")
    
    def calculate_total_damage(self) -> int:
        """Calculate total damage including weapon and accessories"""
        damage = self.base_damage * self.strength
        
        if self.weapon:
            damage += self.weapon.get_damage()
        
        # Add accessory bonuses
        for accessory in self.accessories:
            if accessory.bonus_type == 'damage':
                damage += accessory.bonus_value
        
        return int(damage)
    
    def calculate_total_defense(self) -> int:
        """Calculate total defense including armor and accessories"""
        defense = self.base_defense
        
        if self.armor:
            defense += self.armor.get_defense()
        
        # Add accessory bonuses
        for accessory in self.accessories:
            if accessory.bonus_type == 'defense':
                defense += int(accessory.bonus_value)
        
        return defense
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage taken"""
        defense = self.calculate_total_defense()
        actual_damage = max(1, damage - defense)
        self.current_health -= actual_damage
        return actual_damage
    
    def is_alive(self) -> bool:
        """Check if character is still alive"""
        return self.current_health > 0
    
    def heal(self, amount: int) -> None:
        """Heal the character"""
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def get_status(self) -> str:
        """Get character status string"""
        return (
            f"\n{'='*50}\n"
            f"Name: {self.name}\n"
            f"Level: {self.level} | HP: {self.current_health}/{self.max_health}\n"
            f"EXP: {self.experience}/{self.experience_to_level}\n"
            f"Damage: {self.calculate_total_damage()} | Defense: {self.calculate_total_defense()}\n"
            f"Weapon: {self.weapon.name if self.weapon else 'None'}\n"
            f"Armor: {self.armor.name if self.armor else 'None'}\n"
            f"Accessories: {len(self.accessories)}/3\n"
            f"Scrolls: {len(self.scrolls)}\n"
            f"{'='*50}"
        )


class CombatSystem:
    """Main combat system for roguelike battles"""
    
    def __init__(self):
        self.turn_count = 0
        self.combat_log = []
    
    def log_action(self, action: str) -> None:
        """Log combat action"""
        self.combat_log.append(f"[Turn {self.turn_count}] {action}")
        print(action)
    
    def player_attack(self, attacker: Character, defender: Character) -> None:
        """Execute a player attack"""
        damage = attacker.calculate_total_damage()
        actual_damage = defender.take_damage(damage)
        
        self.log_action(
            f"{attacker.name} attacks {defender.name} for {actual_damage} damage! "
            f"({defender.name} HP: {defender.current_health})"
        )
    
    def use_scroll(self, character: Character, scroll: Scroll, target: Optional[Character] = None) -> bool:
        """Use a scroll in combat"""
        if not character.scrolls:
            return False
        
        if scroll not in character.scrolls:
            return False
        
        power = scroll.cast()
        
        if scroll.effect_type == 'heal':
            character.heal(power)
            self.log_action(f"{character.name} uses {scroll.name} and heals for {power} HP!")
        
        elif scroll.effect_type == 'damage_boost':
            character.strength += power / 100
            self.log_action(f"{character.name} uses {scroll.name} and gains {power}% damage boost!")
        
        elif scroll.effect_type == 'shield':
            character.current_health += power
            self.log_action(f"{character.name} uses {scroll.name} and gains {power} temporary health!")
        
        character.scrolls.remove(scroll)
        return True
    
    def battle(self, player: Character, enemy: Character, max_turns: int = 50) -> bool:
        """Execute a battle between player and enemy"""
        self.turn_count = 0
        self.combat_log = []
        
        self.log_action(f"\n{'*'*50}\nBattle Start: {player.name} vs {enemy.name}\n{'*'*50}")
        
        while player.is_alive() and enemy.is_alive() and self.turn_count < max_turns:
            self.turn_count += 1
            
            # Player turn
            action = random.choice(['attack', 'defend', 'scroll'])
            
            if action == 'attack':
                self.player_attack(player, enemy)
            
            elif action == 'scroll' and player.scrolls:
                self.use_scroll(player, random.choice(player.scrolls))
            
            if not enemy.is_alive():
                break
            
            # Enemy turn
            self.player_attack(enemy, player)
        
        # Battle result
        if player.is_alive():
            reward_exp = enemy.level * 50
            player.gain_experience(reward_exp)
            self.log_action(f"\n{player.name} wins! Gained {reward_exp} experience!")
            return True
        else:
            self.log_action(f"\n{enemy.name} wins! {player.name} has been defeated!")
            return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def create_sample_weapons() -> List[Weapon]:
    """Create sample weapons"""
    return [
        Weapon("Iron Sword", 15, 0.1, ItemRarity.COMMON),
        Weapon("Steel Blade", 20, 0.15, ItemRarity.UNCOMMON),
        Weapon("Excalibur", 35, 0.25, ItemRarity.LEGENDARY),
        Weapon("Dagger", 10, 0.3, ItemRarity.COMMON),
    ]


def create_sample_armor() -> List[Armor]:
    """Create sample armor"""
    return [
        Armor("Leather Armor", 5, ItemRarity.COMMON),
        Armor("Iron Plate", 12, ItemRarity.UNCOMMON),
        Armor("Mithril Suit", 20, ItemRarity.RARE),
    ]


def create_sample_accessories() -> List[Accessory]:
    """Create sample accessories"""
    return [
        Accessory("Ruby Ring", "damage", 5, ItemRarity.UNCOMMON),
        Accessory("Sapphire Amulet", "defense", 3, ItemRarity.UNCOMMON),
        Accessory("Dragon Pendant", "health", 25, ItemRarity.RARE),
    ]


def create_sample_scrolls() -> List[Scroll]:
    """Create sample scrolls"""
    return [
        Scroll("Healing Scroll", "heal", 50, ItemRarity.COMMON),
        Scroll("Power Scroll", "damage_boost", 30, ItemRarity.UNCOMMON),
        Scroll("Shield Scroll", "shield", 40, ItemRarity.UNCOMMON),
        Scroll("Greater Healing", "heal", 100, ItemRarity.RARE),
    ]


def main():
    """Main game loop example"""
    # Create weapons, armor, accessories, and scrolls
    weapons = create_sample_weapons()
    armor_list = create_sample_armor()
    accessories = create_sample_accessories()
    scrolls = create_sample_scrolls()
    
    # Create player and enemy
    player = Character("Hero", 100)
    enemy = Character("Goblin Warrior", 50)
    
    # Equip player
    player.equip_weapon(weapons[0])  # Iron Sword
    player.equip_armor(armor_list[0])  # Leather Armor
    player.add_accessory(accessories[0])  # Ruby Ring
    player.add_scroll(scrolls[0])  # Healing Scroll
    
    # Equip enemy
    enemy.equip_weapon(weapons[3])  # Dagger
    enemy.equip_armor(armor_list[0])  # Leather Armor
    
    print(player.get_status())
    print(enemy.get_status())
    
    # Start combat
    combat = CombatSystem()
    combat.battle(player, enemy)
    
    # Show final status
    print(player.get_status())


if __name__ == "__main__":
    main()
