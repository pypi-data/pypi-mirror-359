from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_events_cls = CoreFactory.INSTANCE.getFiles()
class events:

    HOME = "home"
    RECENT = "recent"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"

    def __init__(self):
        ...

    @staticmethod
    def observeKey(event_callback):
        _events_cls.observeKey(event_callback)

    @staticmethod
    def stop():
       _events_cls.stop()





