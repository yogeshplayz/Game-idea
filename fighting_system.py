"""
Roguelike Fighting System
A comprehensive combat system featuring:
- Character leveling with dynamic stat progression
- Equipment system (weapons, armor, accessories, scrolls)
- Rarity-based item scaling
- Turn-based tactical combat with action choices
- Experience rewards and permadeath tracking
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from abc import ABC, abstractmethod


class ItemRarity(Enum):
    """Item rarity levels affecting stat scaling"""
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5

    @property
    def color(self) -> str:
        """Return color representation for display"""
        colors = {
            ItemRarity.COMMON: "⚪",
            ItemRarity.UNCOMMON: "🟢",
            ItemRarity.RARE: "🔵",
            ItemRarity.EPIC: "🟣",
            ItemRarity.LEGENDARY: "🟡"
        }
        return colors.get(self, "⚪")


class BonusType(Enum):
    """Types of bonuses accessories can provide"""
    HEALTH = "health"
    DAMAGE = "damage"
    DEFENSE = "defense"
    CRIT = "crit"


@dataclass
class Weapon:
    """Weapon item with damage and critical strike stats"""
    name: str
    base_damage: int
    crit_chance: float
    rarity: ItemRarity
    
    def get_damage(self) -> int:
        """Calculate weapon damage with critical hit multiplier"""
        base = self.base_damage * self.rarity.value
        if random.random() < self.crit_chance:
            return int(base * 1.5)  # 50% critical damage multiplier
        return base
    
    def __str__(self) -> str:
        return f"{self.rarity.color} {self.name} (DMG: {self.base_damage}, CRIT: {self.crit_chance*100:.0f}%)"


@dataclass
class Armor:
    """Armor item providing defense scaling based on rarity"""
    name: str
    defense: int
    rarity: ItemRarity
    
    def get_defense(self) -> int:
        """Calculate armor defense value"""
        return self.defense * self.rarity.value
    
    def __str__(self) -> str:
        return f"{self.rarity.color} {self.name} (DEF: {self.defense})"


@dataclass
class Accessory:
    """Accessory items with special stat bonuses"""
    name: str
    bonus_type: BonusType
    bonus_value: float
    rarity: ItemRarity
    
    def __str__(self) -> str:
        return f"{self.rarity.color} {self.name} ({self.bonus_type.value.upper()}: +{self.bonus_value})"


@dataclass
class Scroll:
    """Magic scrolls providing single-use combat effects"""
    name: str
    effect_type: str  # 'heal', 'damage_boost', 'shield', 'revive'
    power: int
    rarity: ItemRarity
    
    def cast(self) -> int:
        """Cast the scroll and return effect power"""
        return self.power * self.rarity.value
    
    def __str__(self) -> str:
        return f"{self.rarity.color} {self.name} ({self.effect_type})"


class Character:
    """Base character class for both players and enemies"""
    
    def __init__(self, name: str, base_health: int = 100, class_type: str = "Warrior"):
        self.name = name
        self.class_type = class_type
        self.max_health = base_health
        self.current_health = base_health
        self.level = 1
        self.experience = 0
        self.experience_to_level = 100
        self.kills = 0
        self.deaths = 0
        
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
        
        # Status effects
        self.damage_boost = 0.0  # Percentage boost
        self.shield_hp = 0  # Temporary health shield
    
    def equip_weapon(self, weapon: Weapon) -> bool:
        """Equip a weapon, replacing previous if any"""
        if weapon is None:
            return False
        self.weapon = weapon
        return True
    
    def equip_armor(self, armor: Armor) -> bool:
        """Equip armor, replacing previous if any"""
        if armor is None:
            return False
        self.armor = armor
        return True
    
    def add_accessory(self, accessory: Accessory) -> bool:
        """Add an accessory (max 3 per character)"""
        if accessory is None or len(self.accessories) >= 3:
            return False
        self.accessories.append(accessory)
        return True
    
    def add_scroll(self, scroll: Scroll) -> bool:
        """Add a scroll to inventory"""
        if scroll is None:
            return False
        self.scrolls.append(scroll)
        return True
    
    def gain_experience(self, amount: int) -> None:
        """Gain experience and trigger level-ups if threshold exceeded"""
        self.experience += amount
        
        while self.experience >= self.experience_to_level:
            self.level_up()
    
    def level_up(self) -> None:
        """Increase character level and improve all stats"""
        self.level += 1
        self.experience -= self.experience_to_level
        self.experience_to_level = int(self.experience_to_level * 1.1)
        
        # Stat scaling: health by 20%, damage by 5, defense by 2, multipliers by 10%
        self.max_health = int(self.max_health * 1.2)
        self.current_health = self.max_health
        self.base_damage += 5
        self.base_defense += 2
        self.strength += 0.1
        self.agility += 0.05
        
        print(f"🎉 {self.name} leveled up to {self.level}! "
              f"HP: {self.max_health} | DMG: {self.base_damage} | DEF: {self.base_defense}")
    
    def calculate_total_damage(self) -> float:
        """Calculate total damage output including all bonuses"""
        damage = self.base_damage * self.strength * (1 + self.damage_boost)
        
        if self.weapon:
            damage += self.weapon.get_damage()
        
        # Add accessory damage bonuses
        for accessory in self.accessories:
            if accessory.bonus_type == BonusType.DAMAGE:
                damage += accessory.bonus_value
        
        return damage
    
    def calculate_total_defense(self) -> float:
        """Calculate total defense including all bonuses"""
        defense = self.base_defense
        
        if self.armor:
            defense += self.armor.get_defense()
        
        # Add accessory defense bonuses
        for accessory in self.accessories:
            if accessory.bonus_type == BonusType.DEFENSE:
                defense += accessory.bonus_value
        
        return defense
    
    def take_damage(self, damage: float) -> float:
        """Take damage, applying defense reduction and shield"""
        defense = self.calculate_total_defense()
        actual_damage = max(1, damage - defense * 0.5)  # Defense reduces 50% per point
        
        # Damage shield first
        if self.shield_hp > 0:
            shield_absorbed = min(self.shield_hp, actual_damage)
            self.shield_hp -= shield_absorbed
            actual_damage -= shield_absorbed
        
        self.current_health -= actual_damage
        return actual_damage
    
    def is_alive(self) -> bool:
        """Check if character is still alive"""
        return self.current_health > 0
    
    def heal(self, amount: int) -> int:
        """Heal the character and return actual healing done"""
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - old_health
    
    def add_shield(self, amount: int) -> None:
        """Add temporary health shield"""
        self.shield_hp += amount
    
    def reset_buffs(self) -> None:
        """Reset temporary buffs (used between battles)"""
        self.damage_boost = 0.0
        self.shield_hp = 0
    
    def get_status(self) -> str:
        """Get formatted character status"""
        shield_display = f" | Shield: {int(self.shield_hp)}" if self.shield_hp > 0 else ""
        boost_display = f" | Boost: +{self.damage_boost*100:.0f}%" if self.damage_boost > 0 else ""
        
        return (
            f"\n{'='*60}\n"
            f"⚔️  {self.name} ({self.class_type})\n"
            f"{'='*60}\n"
            f"Level: {self.level:2d} | EXP: {self.experience:3d}/{self.experience_to_level}\n"
            f"HP: {int(self.current_health):3d}/{int(self.max_health):3d}{shield_display}{boost_display}\n"
            f"DMG: {self.calculate_total_damage():.1f} | DEF: {self.calculate_total_defense():.1f}\n"
            f"STR: {self.strength:.2f} | AGI: {self.agility:.2f}\n"
            f"Kills: {self.kills} | Deaths: {self.deaths}\n"
            f"{'─'*60}\n"
            f"Weapon:     {self.weapon or '─ Empty'}\n"
            f"Armor:      {self.armor or '─ Empty'}\n"
            f"Accessories: {len(self.accessories)}/3"
            if self.accessories:
                for i, acc in enumerate(self.accessories, 1):
                    f"\n  {i}. {acc}"
            else:
                "─ None"
            f"\nScrolls:    {len(self.scrolls)} available"
            if self.scrolls:
                for i, scroll in enumerate(self.scrolls, 1):
                    f"\n  {i}. {scroll}"
            else:
                ""
            f"\n{'='*60}"
        )
    
    def get_brief_status(self) -> str:
        """Get compact status for battle display"""
        return f"{self.name} [{self.class_type}] HP: {int(self.current_health)}/{int(self.max_health)}"


class CombatSystem:
    """Manages turn-based combat between characters"""
    
    # Action weights for enemy AI (can be adjusted per difficulty)
    ATTACK_WEIGHT = 50
    DEFEND_WEIGHT = 20
    SCROLL_WEIGHT = 30
    
    def __init__(self, verbose: bool = True):
        self.turn_count = 0
        self.combat_log: List[str] = []
        self.verbose = verbose
    
    def log_action(self, action: str) -> None:
        """Log and display combat action"""
        log_entry = f"[Turn {self.turn_count}] {action}"
        self.combat_log.append(log_entry)
        if self.verbose:
            print(action)
    
    def player_attack(self, attacker: Character, defender: Character) -> float:
        """Execute an attack action"""
        damage = attacker.calculate_total_damage()
        actual_damage = defender.take_damage(damage)
        
        shield_text = f" (Shield blocked {int(min(actual_damage, defender.shield_hp))} DMG)" if defender.shield_hp > 0 else ""
        self.log_action(
            f"⚔️  {attacker.name} attacks {defender.name} for {int(actual_damage)} damage!{shield_text}\n"
            f"   {defender.get_brief_status()}"
        )
        return actual_damage
    
    def use_scroll(self, character: Character, scroll: Scroll) -> bool:
        """Use a scroll in combat"""
        if scroll not in character.scrolls:
            return False
        
        power = scroll.cast()
        
        if scroll.effect_type == 'heal':
            healed = character.heal(power)
            self.log_action(f"✨ {character.name} uses {scroll.name} and heals for {healed} HP!")
        
        elif scroll.effect_type == 'damage_boost':
            character.damage_boost += power / 100
            self.log_action(f"💥 {character.name} uses {scroll.name}! Damage +{power}% next turn!")
        
        elif scroll.effect_type == 'shield':
            character.add_shield(power)
            self.log_action(f"🛡️  {character.name} uses {scroll.name} and gains {power} shield!")
        
        elif scroll.effect_type == 'revive':
            if not character.is_alive():
                character.current_health = int(character.max_health * 0.5)
                self.log_action(f"🔄 {character.name} uses {scroll.name} and is revived with 50% HP!")
        
        character.scrolls.remove(scroll)
        return True
    
    def choose_action(self, character: Character, is_player: bool = False) -> Tuple[str, Optional[Scroll]]:
        """Choose next action (smart AI for enemies, random for players in this implementation)"""
        if is_player:
            # In a real game, this would be user input
            return random.choice(['attack', 'defend', 'scroll']), None
        else:
            # Enemy AI: weighted random based on health percentage
            health_percent = character.current_health / character.max_health
            
            # Low health: prioritize scrolls
            if health_percent < 0.3 and character.scrolls:
                weights = [self.ATTACK_WEIGHT, self.DEFEND_WEIGHT, self.SCROLL_WEIGHT * 2]
            else:
                weights = [self.ATTACK_WEIGHT, self.DEFEND_WEIGHT, self.SCROLL_WEIGHT]
            
            action = random.choices(['attack', 'defend', 'scroll'], weights=weights)[0]
            
            scroll = None
            if action == 'scroll' and character.scrolls:
                scroll = random.choice(character.scrolls)
            
            return action, scroll
    
    def battle(self, player: Character, enemy: Character, max_turns: int = 50) -> bool:
        """Execute a complete battle sequence"""
        self.turn_count = 0
        self.combat_log = []
        
        # Reset temporary buffs
        player.reset_buffs()
        enemy.reset_buffs()
        
        self.log_action(
            f"\n{'*'*60}\n"
            f"⚔️  BATTLE START\n"
            f"{player.get_brief_status()}\n"
            f"vs\n"
            f"{enemy.get_brief_status()}\n"
            f"{'*'*60}\n"
        )
        
        while player.is_alive() and enemy.is_alive() and self.turn_count < max_turns:
            self.turn_count += 1
            
            # Player turn
            action, scroll = self.choose_action(player, is_player=True)
            
            if action == 'attack':
                self.player_attack(player, enemy)
            elif action == 'scroll' and scroll:
                self.use_scroll(player, scroll)
            elif action == 'defend':
                shield = int(player.calculate_total_defense() * 2)
                player.add_shield(shield)
                self.log_action(f"🛡️  {player.name} takes a defensive stance! +{shield} Shield")
            
            if not enemy.is_alive():
                break
            
            # Enemy turn
            action, scroll = self.choose_action(enemy, is_player=False)
            
            if action == 'attack':
                self.player_attack(enemy, player)
            elif action == 'scroll' and scroll:
                self.use_scroll(enemy, scroll)
            elif action == 'defend':
                shield = int(enemy.calculate_total_defense() * 2)
                enemy.add_shield(shield)
                self.log_action(f"🛡️  {enemy.name} takes a defensive stance! +{shield} Shield")
        
        # Battle conclusion
        self.log_action("\n" + "="*60)
        if player.is_alive():
            reward_exp = max(50, enemy.level * 50)
            player.gain_experience(reward_exp)
            player.kills += 1
            self.log_action(f"🎉 {player.name} WINS! Gained {reward_exp} experience!")
            return True
        else:
            player.deaths += 1
            self.log_action(f"💀 {enemy.name} WINS! {player.name} has been defeated!")
            return False


# ============================================================================
# ITEM FACTORIES
# ============================================================================

def create_weapons() -> List[Weapon]:
    """Create weapon catalog"""
    return [
        Weapon("Iron Sword", 15, 0.1, ItemRarity.COMMON),
        Weapon("Steel Blade", 20, 0.15, ItemRarity.UNCOMMON),
        Weapon("Excalibur", 35, 0.25, ItemRarity.LEGENDARY),
        Weapon("Dagger", 10, 0.3, ItemRarity.COMMON),
        Weapon("Battle Axe", 25, 0.12, ItemRarity.RARE),
        Weapon("Mystic Staff", 28, 0.20, ItemRarity.RARE),
    ]


def create_armor() -> List[Armor]:
    """Create armor catalog"""
    return [
        Armor("Leather Armor", 5, ItemRarity.COMMON),
        Armor("Iron Plate", 12, ItemRarity.UNCOMMON),
        Armor("Mithril Suit", 20, ItemRarity.RARE),
        Armor("Dragon Scale", 30, ItemRarity.EPIC),
        Armor("Enchanted Robe", 8, ItemRarity.UNCOMMON),
    ]


def create_accessories() -> List[Accessory]:
    """Create accessories catalog"""
    return [
        Accessory("Ruby Ring", BonusType.DAMAGE, 5, ItemRarity.UNCOMMON),
        Accessory("Sapphire Amulet", BonusType.DEFENSE, 3, ItemRarity.UNCOMMON),
        Accessory("Dragon Pendant", BonusType.HEALTH, 25, ItemRarity.RARE),
        Accessory("Emerald Crown", BonusType.CRIT, 0.1, ItemRarity.EPIC),
        Accessory("Void Bracelet", BonusType.DAMAGE, 10, ItemRarity.RARE),
    ]


def create_scrolls() -> List[Scroll]:
    """Create scrolls catalog"""
    return [
        Scroll("Healing Scroll", "heal", 50, ItemRarity.COMMON),
        Scroll("Power Scroll", "damage_boost", 30, ItemRarity.UNCOMMON),
        Scroll("Shield Scroll", "shield", 40, ItemRarity.UNCOMMON),
        Scroll("Greater Healing", "heal", 100, ItemRarity.RARE),
        Scroll("Massive Heal", "heal", 200, ItemRarity.EPIC),
        Scroll("Revive Scroll", "revive", 1, ItemRarity.LEGENDARY),
    ]


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    """Run a combat demo"""
    # Load item catalogs
    weapons = create_weapons()
    armor_list = create_armor()
    accessories = create_accessories()
    scrolls = create_scrolls()
    
    # Create player character
    player = Character("Hero", 120, "Warrior")
    player.equip_weapon(weapons[0])  # Iron Sword
    player.equip_armor(armor_list[0])  # Leather Armor
    player.add_accessory(accessories[0])  # Ruby Ring
    player.add_scroll(scrolls[0])  # Healing Scroll
    player.add_scroll(scrolls[2])  # Shield Scroll
    
    # Create enemy character
    enemy = Character("Goblin Warrior", 60, "Rogue")
    enemy.equip_weapon(weapons[3])  # Dagger
    enemy.equip_armor(armor_list[0])  # Leather Armor
    enemy.add_scroll(scrolls[0])  # Healing Scroll
    
    # Display initial status
    print(player.get_status())
    print(enemy.get_status())
    
    # Start combat
    combat = CombatSystem(verbose=True)
    victory = combat.battle(player, enemy)
    
    # Display final status
    print(player.get_status())
    print(f"\nBattle Result: {'VICTORY' if victory else 'DEFEAT'}")


if __name__ == "__main__":
    main()
