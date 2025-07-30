

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")



class websocket:

    def __init__(self):
        self._websocket = CoreFactory.INSTANCE.getWebSocket();



