"""Player state during a run."""
from dataclasses import dataclass


@dataclass
class PlayerState:
    hp: int = 50
    max_hp: int = 50
    energy: int = 3
    max_energy: int = 3
    block: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0
