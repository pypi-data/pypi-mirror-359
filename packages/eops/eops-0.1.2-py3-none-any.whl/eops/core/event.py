# eops/core/event.py
from enum import Enum
from typing import Any, Dict
# queue is no longer imported here, as the event_bus is no longer global.

class EventType(Enum):
    """
    Enumeration of all possible event types in the system.
    """
    # Market Events
    MARKET = 'MARKET'             # A new kline/bar is available
    TICKER = 'TICKER'             # A new ticker price update is available
    PUBLIC_TRADE = 'PUBLIC_TRADE' # A new public trade has occurred on the exchange
    
    # Signal Events
    SIGNAL = 'SIGNAL'         # A strategy logic has generated a trading signal
    
    # Order Lifecycle Events
    ORDER = 'ORDER'           # A request to place a new order
    FILL = 'FILL'             # A private order has been filled (or partially filled)
    
    # Informational Events
    HEARTBEAT = 'HEARTBEAT'   # A regular time-based event, e.g., every second


class Event:
    """
    Base class for all event objects. It defines the type and optional data payload.
    """
    def __init__(self, event_type: EventType, data: Any = None):
        """
        Initializes the event.
        
        Args:
            event_type: The type of the event, from the EventType enum.
            data: A dictionary payload containing event-specific information.
        """
        self.type = event_type
        self.data: Dict[str, Any] = data if data is not None else {}

    def __str__(self):
        # A more informative string representation
        # Truncate long data previews
        items_preview = list(self.data.items())[:3]
        data_preview = ', '.join(f"{k}={v}" for k, v in items_preview)
        if len(self.data) > 3:
            data_preview += ', ...'
        return f"Event(type={self.type.name}, data={{{data_preview}}})"