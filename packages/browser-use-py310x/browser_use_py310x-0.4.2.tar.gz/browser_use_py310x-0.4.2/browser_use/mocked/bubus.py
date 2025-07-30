class BaseEvent:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return None
    # def on(self, *args, **kwargs):
    #     pass
    # async def stop(self, *args, **kwargs):
    #     pass
    # def dispatch(self, *args, **kwargs):
    #     pass

class EventBus:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return None
    # def on(self, *args, **kwargs):
    #     pass
    # async def stop(self, *args, **kwargs):
    #     pass
    # def dispatch(self, *args, **kwargs):
    #     pass