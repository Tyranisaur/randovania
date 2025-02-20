from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import Self

    from randovania.game.game_enum import RandovaniaGame

import dataclasses

from randovania.bitpacking.json_dataclass import JsonDataclass


@dataclasses.dataclass(frozen=True)
class BaseCosmeticPatches(JsonDataclass):
    """Settings for game modifications that can be modified without invalidating a Permalink.
    Commonly used for player's model/sprite, hud color, defaults for in-game settings."""

    @classmethod
    def default(cls) -> Self:
        return cls()

    @classmethod
    def game(cls) -> RandovaniaGame:
        raise NotImplementedError
