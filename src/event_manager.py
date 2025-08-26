class EventManager:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type, listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def post(self, event):
        event_type = event.get("type")
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener(event)

# Global instance of the event manager
event_manager = EventManager()
