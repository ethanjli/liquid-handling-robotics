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

class YPositioner(LinearActuator):
    def __init__(self):
        super().__init__()
        self.running = False

        self.top_position = 0  # unitless
        self.top_mark = 9.7  # cm
        self.bottom_position = 700  # unitless
        self.bottom_mark = 0  # cm

        self.cuvette_rows = {  # cm
            'G': 0.3,
            'F': 1.8,
            'E': 3.3,
            'D': 4.8,
            'C': 6.4,
            'B': 7.9,
            'A': 9.4
        }
        self.well_rows = {  # cm
            'H': 1.75,
            'G': 2.75,
            'F': 3.6,
            'E': 4.5,
            'D': 5.4,
            'C': 6.3,
            'B': 7.2,
            'A': 8.1
        }

    def __repr__(self):
        return 'Y Axis'

    @property
    def physical_unit(self):
        return 'cm'

    @custom_repr('set cuvette row')
    def set_cuvette_position(self, cuvette):
        self.set_target_mark(self.cuvette_rows[cuvette])

    @custom_repr('set 96-well plate row')
    def set_well_position(self, well):
        self.set_target_mark(self.well_rows[well])

    # Implement ChannelTreeNode

    @property
    def node_prefix(self):
        return 'y'

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
    def __init__(self, y_positioner):
        self.y_positioner = y_positioner

    def parse_input(self, user_input):
        if user_input.lower().endswith(self.y_positioner.physical_unit):
            user_input = user_input[:-2]
        user_input = user_input.strip()
        user_input = float(user_input)
        if (user_input < self.y_positioner.bottom_mark or
                user_input > self.y_positioner.top_mark):
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
                    ('Please specify the next y positioner position to go to '
                     'between {} {} and {} {}: ')
                    .format(
                        self.y_positioner.bottom_mark,
                        self.y_positioner.physical_unit,
                        self.y_positioner.top_mark,
                        self.y_positioner.physical_unit
                    )
                )
                user_input = self.parse_input(user_input)
                need_input = False
            except ValueError:
                print('Invalid input: {}'.format(user_input))
                pass
            except EOFError:
                self.y_positioner.running = False
                return
        self.y_positioner.set_target_position(
            user_input, units=self.y_positioner.physical_unit
        )

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    translator = ASCIITranslator()
    dispatcher = Dispatcher()
    y_positioner = YPositioner()
    targeting = InteractiveTargeting(y_positioner)

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    dispatcher.receivers[None].append(y_positioner)
    y_positioner.converged_position_listeners.append(targeting)
    y_positioner.stalled_position_listeners.append(targeting)
    y_positioner.message_listeners.append(translator)

    connection.open()
    monitor.start_reading_lines()
    connection.reset()


if __name__ == '__main__':
    main()

