from dnd.monsters.goblin import create_goblin
from dnd.monsters.skeleton import create_skeleton
from dnd.dnd_enums import AttackType, AttackHand, RangeType, ActionType
from dnd.actions import Attack, ActionCost
from dnd.statsblock import StatsBlock

from pydantic import BaseModel, Field,computed_field
from typing import Optional, List
from dnd.logger import (ActionLog, AttackRollOut, DamageRollOut, ValueOut, 
                        AttackBonusOut, WeaponAttackBonusOut)
from dnd.dnd_enums import AdvantageStatus, AutoHitStatus, CriticalStatus

class ActionText(BaseModel):
    action_log: ActionLog
    attacker: StatsBlock
    defender: StatsBlock
    verbose_level: int = Field(default=1, ge=0, le=2)

    @computed_field
    def attacker_name(self) -> str:
        return self.attacker.name
    
    @computed_field
    def defender_name(self) -> str:
        return self.defender.name

    def to_html(self) -> str:
        if self.verbose_level == 0:
            return self._format_basic()
        elif self.verbose_level == 1:
            return self._format_detailed()
        else:
            return self._format_highly_detailed()
    def _format_basic(self) -> str:
        result = "Hit!" if self.action_log.success else "Miss."
        return f"<p>{self.attacker_name} attacks {self.defender_name}. {result}</p>"

    def _format_detailed(self) -> str:
        attack_roll = self._get_attack_roll()
        damage_roll = self._get_damage_roll()

        if not attack_roll:
            return self._format_basic()

        text = f"<p>{self.attacker_name} attacks {self.defender_name} with {attack_roll.hand.value}. "
        text += f"{self._format_attack_roll(attack_roll, detailed=False)}"

        if damage_roll and self.action_log.success:
            text += f" {self._format_damage_roll(damage_roll, detailed=False)}"

        text += "</p>"
        return text



    def _get_attack_roll(self) -> Optional[AttackRollOut]:
        return next((roll for roll in self.action_log.dice_rolls if roll.log_type == "AttackRoll"), None)

    def _get_damage_roll(self) -> Optional[DamageRollOut]:
        return next((roll for roll in self.action_log.damage_rolls if roll.log_type == "DamageRoll"), None)

    def _format_highly_detailed(self) -> str:
        attack_roll = self._get_attack_roll()
        damage_roll = self._get_damage_roll()

        text = f"<p><b><a href=\"entity:{self.attacker.id}\">{self.attacker.name}</a>'s turn:</b><br>"
        text += f"  - Action: Attack with {attack_roll.hand.value}<br>"
        text += f"{self._format_attack_roll(attack_roll, detailed=True)}"
        text += f"  - Result: {'Hit' if self.action_log.success else 'Miss'}<br>"

        if damage_roll and self.action_log.success:
            text += f"{self._format_damage_roll(damage_roll, detailed=True)}"

        text += "</p>"
        return text

    def _format_attack_roll(self, attack_roll: AttackRollOut, detailed: bool) -> str:
        base_roll = attack_roll.roll.base_roll.result
        modifiers = self._format_attack_bonus_out(attack_roll.attack_bonus)
        total = attack_roll.total_roll
        ac = attack_roll.total_target_ac
        return (f"  - Attack Roll: {base_roll} (d20) + {modifiers} = {total}<br>"
                f"  - Target: <a href=\"entity:{self.defender.id}\">{self.defender.name}</a> (AC {ac})<br>")

    def _format_damage_roll(self, damage_roll: DamageRollOut, detailed: bool) -> str:
        dice_roll = damage_roll.dice_roll.result
        bonus = self._format_damage_bonus(damage_roll.damage_bonus)
        total = damage_roll.total_damage
        damage_type = damage_roll.damage_type.value
        return f"  - Damage Roll: {dice_roll} (dice) {bonus} = {total} {damage_type} damage<br>"

    def _format_damage_bonus(self, damage_bonus: ValueOut) -> str:
        # First, look for the ability bonus (should be Strength or Dexterity)
        ability_bonus = next((
            (key, value) for key, value in damage_bonus.bonuses.bonuses.items()
            if key in ["base_strength", "base_dexterity"]
        ), None)

        if ability_bonus:
            ability_name, ability_modifier = ability_bonus
            ability_name = ability_name.replace("base_", "").capitalize()
            ability_value = ability_modifier*2 + 10
            return f"+ {ability_modifier} [{ability_value}] ({ability_name})"
        
        # If no ability bonus found, check for a general damage bonus
        total_bonus = damage_bonus.total_bonus
        if total_bonus != 0:
            return f"{total_bonus} [DamageBonus]"
        else:
            return ""

    def _format_bonus(self, name: str, value: int) -> str:
        return f"{value} [{name}]"

    def _format_ability_bonus(self, ability_bonus: ValueOut) -> str:
        ability_name = next((key for key in ability_bonus.bonuses.bonuses.keys() if key.startswith("base_")), "")
        ability_score = ability_bonus.bonuses.bonuses.get(ability_name, 0)
        ability_modifier = self._ability_score_to_modifier(ability_score)
        ability_name = ability_name.replace("base_", "").capitalize()
        return f"{ability_modifier} ({ability_score}) [{ability_name}]"

    def _format_attack_bonus_out(self, attack_bonus: AttackBonusOut) -> str:
        components = []
        if attack_bonus.proficiency_bonus:
            components.append(self._format_bonus("ProficiencyBonus", attack_bonus.proficiency_bonus.total_bonus))
        if attack_bonus.ability_bonus:
            components.append(self._format_ability_bonus(attack_bonus.ability_bonus))
        if attack_bonus.weapon_bonus:
            weapon_bonus = self._format_weapon_attack_bonus_out(attack_bonus.weapon_bonus)
            if weapon_bonus:
                components.append(weapon_bonus)
        return " + ".join(components)

    def _format_weapon_attack_bonus_out(self, weapon_bonus: WeaponAttackBonusOut) -> str:
        if weapon_bonus.total_weapon_bonus.total_bonus != 0:
            return self._format_bonus("WeaponBonus", weapon_bonus.total_weapon_bonus.total_bonus)
        return ""

    def _format_sign(self, value: int) -> str:
        return f"+{value}" if value >= 0 else str(value)



    def _ability_score_to_modifier(self, score: int) -> int:
        return (score - 10) // 2

    def _ability_score_to_modifier(self, score):
        return (score - 10) // 2

    def _format_advantage_tracker(self, advantage_tracker):
        if advantage_tracker.status != AdvantageStatus.NONE:
            return f"Advantage: {advantage_tracker.status.value}"
        return ""

    def _format_critical_tracker(self, critical_tracker):
        if critical_tracker.status != CriticalStatus.NONE:
            return f"Critical: {critical_tracker.status.value}"
        return ""

    def _format_auto_hit_tracker(self, auto_hit_tracker):
        if auto_hit_tracker.status != AutoHitStatus.NONE:
            return f"Auto Hit: {auto_hit_tracker.status.value}"
        return ""

class CombatSimulator:
    def __init__(self):
        self.goblin = create_goblin("Goblin")
        self.skeleton = create_skeleton("Skeleton")
        
        # Set up initial positions
        self.goblin.sensory.update_origin((0, 0))
        self.skeleton.sensory.update_origin((1, 0))  # 5 feet away
        self.goblin.sensory.update_distance_matrix({(1, 0): 5})
        self.skeleton.sensory.update_distance_matrix({(0, 0): 5})
        self.goblin.sensory.update_fov(set([(1, 0)]))
        self.skeleton.sensory.update_fov(set([(0, 0)]))

        self.melee_attack_right = Attack(
            name="Melee Attack with right hand",
            description="A basic melee attack with the right hand",
            attack_type=AttackType.MELEE_WEAPON,
            attack_hand=AttackHand.MELEE_RIGHT,
            range_type=RangeType.REACH,
            range_normal=5
        )

        self.melee_attack_left = Attack(
            name="Melee Attack with left hand",
            description="A basic melee attack with the left hand",
            attack_type=AttackType.MELEE_WEAPON,
            attack_hand=AttackHand.MELEE_LEFT,
            range_type=RangeType.REACH,
            range_normal=5
        )
        self.round = 0
        self.max_rounds = 5

    def __iter__(self):
        return self

    def __next__(self):
        if self.round < self.max_rounds and self.goblin.health.current_hit_points > 0 and self.skeleton.health.current_hit_points > 0:
            self.round += 1
            attacker = self.goblin if self.round % 2 != 0 else self.skeleton
            defender = self.skeleton if attacker == self.goblin else self.goblin
            
            attacker.action_economy.reset()
            if attacker == self.goblin:
                attack_action = self.melee_attack_left
            else:
                attack_action = self.melee_attack_right
            attack_logs = attack_action.apply(attacker, defender)
            
            action_texts = [
                ActionText(
                    action_log=log,
                    attacker=attacker,
                    defender=defender,
                    verbose_level=2  # Set to 2 for highly detailed output
                ) for log in attack_logs
            ]
            
            return action_texts
        else:
            raise StopIteration