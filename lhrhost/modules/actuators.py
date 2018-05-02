# Standard imports
from abc import abstractmethod

# Local package imports
from lhrhost.util.interfaces import InterfaceClass, custom_repr
from lhrhost.serialio.dispatch import Message
from lhrhost.modules.channels import ChannelTreeNode

class ConvergedPositionReceiver(object, metaclass=InterfaceClass):
    @abstractmethod
    def on_converged_position(self, actuator, position_unitless, position_mark):
        pass

class StalledPositionReceiver(object, metaclass=InterfaceClass):
    @abstractmethod
    def on_stalled_position(self, actuator, position_unitless, position_mark):
        pass

class LinearActuator(ChannelTreeNode):
    def __init__(self):
        self.converged_position_listeners = []
        self.stalled_position_listeners = []
        self.message_listeners = []
        self.initialized = False

    def _emit_message(self, channel, payload):
        message = Message(channel, payload)
        for listener in self.message_listeners:
            listener.on_message(message)

    # Unit conversions

    @abstractmethod
    def to_unit_position(self, unitless_position):
        pass

    @abstractmethod
    def to_unitless_position(self, unitless_position):
        pass

    # Subchannel handlers

    def on_received_converge(self, subchannel, message):
        self.initialized = True
        unitless_position = int(message.payload)
        unit_position = self.to_unit_position(unitless_position)
        print('{}: Converged at {:.3f} {} ({} unitless)!'
              .format(self, unit_position, self.physical_unit, unitless_position))
        for listener in self.converged_position_listeners:
            listener.on_converged_position(self, unitless_position, unit_position)

    def on_received_stall(self, subchannel, message):
        self.initialized = True
        unitless_position = int(message.payload)
        unit_position = self.to_unit_position(unitless_position)
        print('{}: Stalled at {:.3f} {} ({} unitless)!'
              .format(self, unit_position, self.physical_unit, unitless_position))
        for listener in self.stalled_position_listeners:
            listener.on_stalled_position(self, unitless_position, unit_position)

    def set_target_position(self, target_position, units=None):
        if units is None:
            unitless_position = target_position
        elif units == self.physical_unit:
            unitless_position = self.to_unitless_position(target_position)
        else:
            raise NotImplementedError("Arbitrary unit conversions not yet supported!")
        self._emit_message('{}t'.format(self.node_prefix), unitless_position)

    @custom_repr('set target mark')
    def set_target_mark(self, target_mark):
        self.set_target_position(target_mark, units=self.physical_unit)

    @custom_repr('set direct duty')
    def set_direct_duty(self, duty):
        self._emit_message('{}d'.format(self.node_prefix), duty)

    @custom_repr('set PID k_p')
    def set_pid_k_p(self, k_p):
        self._emit_message('{}kp'.format(self.node_prefix), int(k_p * 100))

    @custom_repr('set PID k_d')
    def set_pid_k_d(self, k_d):
        self._emit_message('{}kd'.format(self.node_prefix), int(k_d * 100))

    @custom_repr('set PID k_i')
    def set_pid_k_i(self, k_i):
        self._emit_message('{}ki'.format(self.node_prefix), int(k_i * 100))

    @custom_repr('set limit position high')
    def set_limit_position_high(self, limit):
        self._emit_message('{}lph'.format(self.node_prefix), limit)

    @custom_repr('set limit position low')
    def set_limit_position_low(self, limit):
        self._emit_message('{}lpl'.format(self.node_prefix), limit)

    # Implement ChannelTreeNode

    @property
    def subchannel_handlers(self):
        return {
            'rc': self.on_received_converge,
            'rt': self.on_received_stall
        }

