# eops/core/strategy.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

from .handler import (
    BaseUpdater,
    BaseEventHandler,
    BaseDecider,
    BaseExecutor
)

if TYPE_CHECKING:
    from .engine import BaseEngine

class BaseStrategy(ABC):
    """
    Abstract Base Class for a strategy in the UADE pipeline architecture.
    It holds the shared context and parameters for all its components and
    provides access to the parent engine's logger and event bus.
    """
    def __init__(self, engine: 'BaseEngine', context: Dict[str, Any], params: Dict[str, Any]):
        """
        Initializes the strategy and its component processors.

        Args:
            engine: The parent engine instance, providing access to logger and event_bus.
            context: Shared objects from the engine (e.g., exchange instances).
            params: Strategy-specific parameters from the config file.
        """
        self.engine = engine
        self.context: Dict[str, Any] = context
        self.params: Dict[str, Any] = params
        
        # Components can access the logger and event_bus via the strategy.
        self.log = self.engine.log
        self.event_bus = self.engine.event_bus
        
        self.shared_state: Dict[str, Any] = {}

        self.updaters: List[BaseUpdater] = self._create_updaters()
        self.event_handlers: List[BaseEventHandler] = self._create_event_handlers()
        self.deciders: List[BaseDecider] = self._create_deciders()
        self.executors: List[BaseExecutor] = self._create_executors()
        
        if not self.updaters:
            raise ValueError("A strategy must have at least one Updater.")
        if not self.deciders:
            raise ValueError("A strategy must have at least one Decider.")
        if not self.executors:
            raise ValueError("A strategy must have at least one Executor.")

        self.log.info(f"Strategy '{self.__class__.__name__}' initialized with:")
        self.log.info(f"  - {len(self.updaters)} Updater(s)")
        self.log.info(f"  - {len(self.event_handlers)} EventHandler(s)")
        self.log.info(f"  - {len(self.deciders)} Decider(s)")
        self.log.info(f"  - {len(self.executors)} Executor(s)")

    @abstractmethod
    def _create_updaters(self) -> List[BaseUpdater]:
        """Must be implemented by the user to define the data sources."""
        pass

    def _create_event_handlers(self) -> List[BaseEventHandler]:
        """Optional. Implement to define data processing/analysis handlers."""
        return []

    @abstractmethod
    def _create_deciders(self) -> List[BaseDecider]:
        """Must be implemented by the user to define the decision-making logic."""
        pass

    @abstractmethod
    def _create_executors(self) -> List[BaseExecutor]:
        """Must be implemented by the user to define the order execution logic."""
        pass