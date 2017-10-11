"""
Define a family of algorithms, encapsulate each one, and make them
interchangeable. Strategy lets the algorithm vary independently from
clients that use it.
"""

import abc


class Strategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy):
        """Create a strategy using the IStrategy implementation passed in"""
        self.strategy = strategy
        self.strategy.poststartup()

    def execute(self, context):
        """Execute the strategies on the given context"""
        self.strategy.premessage(context)
        context = self.strategy.bind(context)
        self.strategy.postmessage(context)
        return context

    def _shutdown(self):
        pass

    def shutdown(self):
        """Perform cleanup! We're goin' down!!!"""
        self.strategy.preshutdown()
        self._shutdown()
        self.strategy.postshutdown()


class IStrategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. Context
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    """
    @abc.abstractmethod
    def bind(self, context):
        """Bind to the context"""
        pass

    def poststartup(self):
        """Implement this for post-initialization"""
        pass

    def preshutdown(self):
        """Implement this for pre-shutdown cleanup"""
        pass

    def postshutdown(self):
        """Implement this for post-shutdown cleanup"""
        pass

    def premessage(self, context):
        """Implement this to run something prior to receiving a message"""
        pass

    def postmessage(self, context):
        """Implement this to run something after receiving a message"""
        pass
