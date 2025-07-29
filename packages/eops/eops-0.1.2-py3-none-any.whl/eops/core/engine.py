# eops/core/engine.py
from abc import ABC, abstractmethod
from queue import Empty, Queue
from collections import defaultdict
from typing import Dict, Any, List, Type
from uuid import uuid4
import signal # Import the signal module

from .event import Event, EventType
from .strategy import BaseStrategy
from eops.utils.logger import setup_logger

class BaseEngine(ABC):
    """
    Abstract Base Class for all engines in the UADE architecture.
    
    The engine instantiates the strategy, registers all its processors
    (EventHandlers, Deciders, Executors), starts its data sources (Updaters),
    and runs the main event loop. Each engine instance has its own private
    event bus and logger.
    """
    def __init__(self, strategy_class: Type[BaseStrategy], context: Dict[str, Any], params: Dict[str, Any]):
        """
        Initializes the engine and the strategy with its full pipeline.
        """
        self.instance_id = str(uuid4())
        self.log = setup_logger(self.instance_id)

        self.event_bus = Queue()
        self.strategy = strategy_class(engine=self, context=context, params=params)
        
        self.handler_map = self._create_handler_map()
        self.running = False

    def _create_handler_map(self) -> Dict[EventType, List[Any]]:
        """
        Creates a mapping from EventType to a list of processors that subscribe to it.
        """
        handler_map = defaultdict(list)
        all_processors = (
            self.strategy.event_handlers + 
            self.strategy.deciders + 
            self.strategy.executors
        )
        for processor in all_processors:
            for event_type in processor.subscribed_events:
                handler_map[event_type].append(processor)
        
        self.log.debug("Handler map created:")
        for event_type, processor_list in handler_map.items():
            processor_names = [p.__class__.__name__ for p in processor_list]
            self.log.debug(f"  - {event_type.name}: {processor_names}")
        return handler_map

    def start_event_sources(self):
        """Starts all updaters defined in the strategy."""
        if not self.strategy.updaters:
            self.log.warning("No updaters found in the strategy. The engine will not receive any data.")
            return
        for updater in self.strategy.updaters:
            updater.start()

    def run(self):
        """The main event loop. This method blocks until the engine is stopped."""
        # --- NEW: Set up signal handler for graceful shutdown ---
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

        self.log.info(f"🚀 Starting engine '{self.__class__.__name__}' with instance ID: {self.instance_id}")
        self.running = True
        self.start_event_sources()
        
        while self.running:
            try:
                event = self.event_bus.get(block=True, timeout=1.0)
            except Empty:
                continue
            if event:
                self.dispatch(event)
        
        self.log.info(f"👋 Engine '{self.__class__.__name__}' has stopped.")

    def dispatch(self, event: Event):
        """Dispatches an event to all registered processors."""
        if event.type in self.handler_map:
            self.log.debug(f"Dispatching event: {event}")
            processors = self.handler_map[event.type]
            for processor in processors:
                try:
                    processor.process(event)
                except Exception as e:
                    self.log.error(f"Error in processor '{processor.__class__.__name__}' while processing {event.type.name} event: {e}", exc_info=True)

    def stop(self):
        """Stops the engine's event loop and all updaters gracefully."""
        if not self.running:
            return # Avoid multiple stop calls
        self.log.info(f"🛑 Stopping engine '{self.__class__.__name__}'...")
        self.running = False
        if hasattr(self, 'strategy') and hasattr(self.strategy, 'updaters'):
            for updater in self.strategy.updaters:
                updater.stop()

    def _handle_shutdown_signal(self, signum, frame):
        """Private method to handle OS signals like SIGTERM."""
        self.log.warning(f"Received signal {signum}. Initiating graceful shutdown...")
        self.stop()

# ====================================================================
#  Live Engine Definition (Placeholder for real-time trading)
# ====================================================================

class LiveEngine(BaseEngine):
    """
    The engine for running strategies in a live, event-driven environment.
    """
    def __init__(self, config: Dict[str, Any]):
        exchange_class = config.get("exchange_class")
        if not exchange_class:
            raise ValueError("`EXCHANGE_CLASS` must be specified in the config for live trading.")

        exchange_params = config.get("exchange_params", {})
        exchange = exchange_class(params=exchange_params)
        
        context = {"exchange": exchange}
        strategy_class = config["strategy_class"]
        strategy_params = config.get("strategy_params", {})

        super().__init__(strategy_class, context, strategy_params)

    def start_event_sources(self):
        self.log.warning("LiveEngine.start_event_sources() is not yet implemented. Live trading will not receive market data.")
        super().start_event_sources()