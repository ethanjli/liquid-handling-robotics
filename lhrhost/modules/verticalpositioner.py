# Local package imports
from lhrhost.util.interfaces import custom_repr
from lhrhost.serialio.transport import (
    ASCIIConnection, ASCIIMonitor
)
from lhrhost.serialio.dispatch import (
    Message, Dispatcher,
    ASCIITranslator
)
from lhrhost.modules.actuators import (
    LinearActuator, ConvergedPositionReceiver
)
from lhrhost.util.math import map_value

class VerticalPositioner(LinearActuator):
    def __init__(self):
        super().__init__()
        self.running = False

        self.top_position = 970  # unitless
        self.top_mark = 5.2  # cm
        self.bottom_position = 20  # unitless
        self.bottom_mark = 0  # cm

        self.well_marks = {  # cm
            'above': 1.3,
            'high': 0.75,
            'low': 0.4,
            'bottom': 0.1
        }
        self.cuvette_marks = {  # cm
            'above': 4.5,
            'high': 3.5,
            'mid': 2,
            'low': 0.5,
            'bottom': 0.05
        }

    def __repr__(self):
        return 'Z Axis'

    @property
    def physical_unit(self):
        return 'cm'

    @custom_repr('set cuvette-relative height')
    def set_cuvette_position(self, cuvette):
        self.set_target_mark(self.cuvette_marks[cuvette])

    @custom_repr('set well-relative height')
    def set_well_position(self, well):
        self.set_target_mark(self.well_marks[well])

    # Implement ChannelTreeNode

    @property
    def node_prefix(self):
        return 'z'

    # Implement LinearActuator

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
    def __init__(self, vertical_positioner):
        self.vertical_positioner = vertical_positioner

    def parse_input(self, user_input):
        if user_input.lower().endswith(self.vertical_positioner.physical_unit):
            user_input = user_input[:-2]
        user_input = user_input.strip()
        user_input = float(user_input)
        if (user_input < self.vertical_positioner.bottom_mark or
                user_input > self.vertical_positioner.top_mark):
            raise ValueError
        return user_input

    # Implement ConvergedPositionReceiver

    def on_converged_position(self, position_unitless, position_physical):
        self.get_next_position()

    def on_stalled_position(self, position_unitless, position_physical):
        self.get_next_position()

    def get_next_position(self):
        need_input = True
        while need_input:
            try:
                user_input = input(
                    ('Please specify the next vertical positioner position to go to '
                     'between {} {} and {} {}: ')
                    .format(
                        self.vertical_positioner.bottom_mark,
                        self.vertical_positioner.physical_unit,
                        self.vertical_positioner.top_mark,
                        self.vertical_positioner.physical_unit
                    )
                )
                user_input = self.parse_input(user_input)
                need_input = False
            except ValueError:
                print('Invalid input: {}'.format(user_input))
                pass
            except EOFError:
                self.vertical_positioner.running = False
                return
        self.vertical_positioner.set_target_position(
            user_input, units=self.vertical_positioner.physical_unit
        )

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    translator = ASCIITranslator()
    dispatcher = Dispatcher()
    vertical_positioner = VerticalPositioner()
    targeting = InteractiveTargeting(vertical_positioner)

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    dispatcher.receivers[None].append(vertical_positioner)
    vertical_positioner.converged_position_listeners.append(targeting)
    vertical_positioner.stalled_position_listeners.append(targeting)
    vertical_positioner.message_listeners.append(translator)

    connection.open()
    monitor.start_reading_lines()
    connection.reset()


if __name__ == '__main__':
    main()

