"""
Generation strategies with temperature control
"""

from enum import Enum


class Strategy(str, Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    CREATIVE = "creative"
    ADVERSARIAL = "adversarial"


STRATEGY_TEMPERATURES = {
    Strategy.CONSERVATIVE: 0.3,
    Strategy.BALANCED: 1.0,
    Strategy.CREATIVE: 1.8,
    Strategy.ADVERSARIAL: 2.5
}
