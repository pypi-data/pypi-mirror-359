# eops/core/handler/updater.py
from abc import ABC, abstractmethod
import threading
from typing import TYPE_CHECKING
# Removed direct logger import, will get it from strategy

if TYPE_CHECKING:
    from ..strategy import BaseStrategy

class BaseUpdater(ABC):
    """
    Abstract Base Class for all data updaters.
    Updaters are the starting point of the pipeline. They fetch data
    and put events onto their strategy's dedicated event bus.
    """
    def __init__(self, strategy: 'BaseStrategy'):
        self.strategy = strategy
        # Get logger and event_bus from the parent strategy
        self.log = self.strategy.log
        self.event_bus = self.strategy.event_bus
        self.active = False
        self._thread: threading.Thread

    @abstractmethod
    def _run(self):
        """The main loop for the updater, which will be run in a thread."""
        pass

    def start(self):
        """Starts the updater's _run loop in a new daemon thread."""
        self.log.info(f"Starting updater '{self.__class__.__name__}'...")
        self.active = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the updater's loop gracefully."""
        self.log.info(f"Stopping updater '{self.__class__.__name__}'...")
        self.active = False