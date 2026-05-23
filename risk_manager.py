Risk Management Engine.
Enforces daily loss limits, position sizing, and trade rules.

import logging
from config import Config

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_pnl = 0.0
        self.trades_today = 0

    def can_trade(self):
        if self.daily_pnl <= -self.config.DAILY_LOSS_LIMIT:
            logger.warning("Daily loss limit reached.")
            return False
        if self.trades_today >= self.config.MAX_TRADES_PER_DAY:
            return False
        return True

    def can_place_trade(self, setup):
        risk = abs(setup["entry"] - setup["sl"])
        if risk > self.config.MAX_SL:
            logger.warning(f"SL risk ${risk} exceeds max ${self.config.MAX_SL}")
            return False
        
        reward = abs(setup["tp"] - setup["entry"])
        rr = reward / risk if risk > 0 else 0
        if rr < self.config.MIN_RR:
            logger.warning(f"RR {rr:.2f} below minimum {self.config.MIN_RR}")
            return False
        return True

    def update_pnl(self, pnl):
        self.daily_pnl += pnl
        logger.info(f"Daily PnL: ${self.daily_pnl:.2f}")

    def daily_loss_exceeded(self):
        return self.daily_pnl <= -self.config.DAILY_LOSS_LIMIT

    def record_trade(self, pnl: float):
        """Call this after a trade is closed to update daily stats."""
        self.daily_pnl += pnl
        self.trades_today += 1
        logger.info(f"Trade recorded. Daily PnL: ${self.daily_pnl:.2f} | Trades today: {self.trades_today}")

    def reset_daily(self):
        """Call this at the start of a new trading day (e.g. 00:00 EST)."""
        self.daily_pnl = 0.0
        self.trades_today = 0
        logger.info("Daily risk counters reset.")