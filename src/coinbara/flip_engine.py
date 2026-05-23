from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Literal

FlipSide = Literal["heads", "tails"]


@dataclass
class FlipEngine:
    history_limit: int = 10
    is_flipping: bool = False
    heads_count: int = 0
    tails_count: int = 0
    history: list[FlipSide] = field(default_factory=list)

    def choose_result(self) -> FlipSide:
        return secrets.choice(("heads", "tails"))

    def begin_flip(self) -> FlipSide | None:
        if self.is_flipping:
            return None
        self.is_flipping = True
        return self.choose_result()

    def finish_flip(self, result: FlipSide) -> None:
        if result == "heads":
            self.heads_count += 1
        else:
            self.tails_count += 1

        self.history.insert(0, result)
        del self.history[self.history_limit :]
        self.is_flipping = False

    def reset(self) -> None:
        self.is_flipping = False
        self.heads_count = 0
        self.tails_count = 0
        self.history.clear()
