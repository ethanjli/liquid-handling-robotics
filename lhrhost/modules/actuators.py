# Standard imports
from abc import abstractmethod

# Local package imports
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.serialio.dispatch import Message
from lhrhost.modules.channels import ChannelTreeNode

class ConvergedPositionReceiver(object, metaclass=InterfaceClass):
    @abstractmethod
    def on_converged_position(self):
        pass

class AbsoluteLinearActuator(ChannelTreeNode):
    def __init__(self):
        self.converged_position_listeners = []
        self.message_listeners = []

    # Unit conversions

    @abstractmethod
    def to_unit_position(self, unitless_position):
        pass

    @abstractmethod
    def to_unitless_position(self, unitless_position):
        pass

    # Subchannel handlers

    def on_received_converge(self, subchannel, message):
        unitless_position = int(message.payload)
        unit_position = self.to_unit_position(unitless_position)
        print('Converged at {:.2f} {} ({} unitless)!'
              .format(unit_position, self.physical_unit, unitless_position))
        for listener in self.converged_position_listeners:
            listener.on_converged_position(unitless_position, unit_position)

    def set_target_position(self, target_position, units=None):
        if units is None:
            unitless_position = target_position
        elif units == self.physical_unit:
            unitless_position = self.to_unitless_position(target_position)
        else:
            raise NotImplementedError("Arbitrary unit conversions not yet supported!")
        message = Message('{}t'.format(self.node_prefix), unitless_position)
        for listener in self.message_listeners:
            listener.on_message(message)

    # Implement ChannelTreeNode

    @property
    def subchannel_handlers(self):
        return {
            'rc': self.on_received_converge
        }

