# eops/core/backtest/updater.py
import pandas as pd
from typing import TYPE_CHECKING

from ..handler.updater import BaseUpdater
from ..event import Event, EventType

if TYPE_CHECKING:
    from ..strategy import BaseStrategy

class BacktestUpdater(BaseUpdater):
    """
    An updater for backtesting. It reads a historical data file and puts
    MarketEvents onto the event bus in chronological order.
    """
    def __init__(self, strategy: 'BaseStrategy', data_path: str):
        super().__init__(strategy)
        self.data_path = data_path
        try:
            self.data = pd.read_csv(self.data_path, parse_dates=['time'], index_col='time')
            self.log.info(f"BacktestUpdater loaded {len(self.data)} data points from {self.data_path}")
        except FileNotFoundError:
            self.log.error(f"Data file not found at {self.data_path}")
            raise

    def _run(self):
        """The main data streaming loop."""
        self.log.info(f"BacktestUpdater starting to stream historical data from {self.data.index[0]} to {self.data.index[-1]}...")
        for index, row in self.data.iterrows():
            if not self.active:
                break
            
            event_data = row.to_dict()
            event_data['time'] = index

            market_event = Event(event_type=EventType.MARKET, data=event_data)
            self.event_bus.put(market_event)

        self.log.info("BacktestUpdater finished streaming all historical data.")