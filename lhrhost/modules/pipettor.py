# Standard imports
import time
import argparse

# Local package imports
from lhrhost.serialio.transport import (
    ASCIIConnection, ASCIIMonitor
)
from lhrhost.serialio.dispatch import (
    Message, Dispatcher,
    ASCIITranslator
)
from lhrhost.modules.actuators import AbsoluteLinearActuator, ConvergedPositionReceiver
from lhrhost.util.math import map_value

class Pipettor(AbsoluteLinearActuator):
    def __init__(self):
        super().__init__()
        self.running = False

        self.top_position = 11  # unitless
        self.top_mark = 0.95  # mL mark
        self.bottom_position = 999  # unitless
        self.bottom_mark = 0.05  # mL mark

    # Implement ChannelTreeNode

    @property
    def node_prefix(self):
        return 'p'

    @property
    def physical_unit(self):
        return 'mL mark'

    # Implement AbsoluteLinearActuator

    def to_unit_position(self, unitless_position):
        return map_value(
            unitless_position, self.bottom_position, self.top_position,
            self.bottom_mark, self.top_mark
        )

    def to_unitless_position(self, unit_position):
        return int(map_value(
            unit_position, self.bottom_mark, self.top_mark,
            self.bottom_position, self.top_position
        ))

class InteractiveTargeting(ConvergedPositionReceiver):
    def __init__(self, pipettor):
        self.pipettor = pipettor

    def parse_input(self, user_input):
        if user_input.lower().endswith('ml'):
            user_input = user_input[:-2]
        user_input = user_input.strip()
        user_input = float(user_input)
        if (user_input < self.pipettor.bottom_mark or
                user_input > self.pipettor.top_mark):
            raise ValueError
        return user_input

    # Implement ConvergedPositionReceiver

    def on_converged_position(self, position_unitless, position_mL_mark):
        need_input = True
        while need_input:
            try:
                user_input = input(
                    'Please specify the next pipettor position to go to between {} {} and {} {}: '
                    .format(
                        self.pipettor.bottom_mark, self.pipettor.physical_unit,
                        self.pipettor.top_mark, self.pipettor.physical_unit
                    )
                )
                user_input = self.parse_input(user_input)
                need_input = False
            except ValueError:
                print('Invalid input: {}'.format(user_input))
                pass
            except EOFError:
                self.pipettor.running = False
                return
        self.pipettor.set_target_position(user_input, units=self.pipettor.physical_unit)

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    translator = ASCIITranslator()
    dispatcher = Dispatcher()
    pipettor = Pipettor()
    targeting = InteractiveTargeting(pipettor)

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    dispatcher.receivers[None].append(pipettor)
    pipettor.converged_position_listeners.append(targeting)
    pipettor.message_listeners.append(translator)

    connection.open()
    monitor.start_reading_lines()
    connection.reset()


if __name__ == '__main__':
    main()

