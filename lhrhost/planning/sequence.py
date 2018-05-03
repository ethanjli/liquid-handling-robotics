# Standard imports
import time

# Local package imports
from lhrhost.serialio.transport import (
    ASCIIConnection, ASCIIMonitor
)
from lhrhost.serialio.dispatch import (
    Message, Dispatcher,
    ASCIITranslator, MessageReceiver, MessageEchoer, VersionReceiver
)
from lhrhost.modules.actuators import (
    ConvergedPositionReceiver, StalledPositionReceiver
)
from lhrhost.modules.pipettor import Pipettor
from lhrhost.modules.verticalpositioner import VerticalPositioner
from lhrhost.modules.ypositioner import YPositioner

class BatchTargeting(ConvergedPositionReceiver, StalledPositionReceiver, MessageReceiver):
    def __init__(self, pipettor, vertical_positioner, y_positioner,
                 actions, initialization=[],
                 interactive=True):
        self.pipettor = pipettor
        self.vertical_positioner = vertical_positioner
        self.y_positioner = y_positioner
        self.actions = actions
        self.initialization = initialization
        self.initialization_step = 0
        self.sequence_step = 0
        self.interactive = interactive
        self.initialized = False

    def on_converged_position(self, actuator, position_unitless, position_mark):
        self.on_new_position(actuator, position_unitless, position_mark)

    def on_stalled_position(self, actuator, position_unitless, position_mark):
        self.on_new_position(actuator, position_unitless, position_mark)

    def on_message(self, message):
        if self.modules_initialized and not self.initialized:
            self.advance_initialization()

    @property
    def modules_initialized(self):
        return (
            self.pipettor.initialized and
            self.vertical_positioner.initialized and
            self.y_positioner.initialized
        )

    def on_new_position(self, actuator, position_unitless, position_mark):
        if self.initialized:
            self.advance_sequence()

    def advance_initialization(self):
        try:
            (action, parameter) = self.initialization[self.initialization_step]
        except (IndexError, StopIteration):
            self.initialized = True
            print('Completed robot initialization! Starting action sequence...')
            self.advance_sequence()
            return
        print('Performing the next initialization step ({}, {})...'.format(
            action, parameter
        ))
        self.initialization_step += 1
        action(parameter)

    def advance_sequence(self):
        try:
            (next_action, next_parameter) = self.actions[self.sequence_step]
        except (IndexError, StopIteration):
            self.quit()
            return
        print()
        if next_action is None:
            input('{}\n[{}] Press enter to continue: '.format(
                next_parameter, self.sequence_step
            ))
            self.sequence_step += 1
            self.advance_sequence()
        elif self.interactive:
            input('[{}] Press enter to perform the next action ({}, {}): '.format(
                self.sequence_step, next_action, next_parameter
            ))
            self.sequence_step += 1
            next_action(next_parameter)
        else:
            print('[{}] Performing the next action ({}, {})...'.format(
                self.sequence_step, next_action, next_parameter
            ))
            self.sequence_step += 1
            next_action(next_parameter)

    def quit(self):
        print('Finished the batch sequence!')
        print()
        self.pipettor.running = False
        self.vertical_positioner.running = False
        self.y_positioner.running = False
        raise KeyboardInterrupt

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)

    translator = ASCIITranslator()
    echoer = MessageEchoer({
        'v0', 'v1', 'v2',
        'pt', 'prc', 'prt', 'pd',
        'zt', 'zrc', 'zrt', 'zd',
        'yt', 'yrc', 'yrt', 'yd'
    })
    version_receiver = VersionReceiver()
    dispatcher = Dispatcher()
    pipettor = Pipettor()
    vertical_positioner = VerticalPositioner()
    y_positioner = YPositioner()

    initialization = [
        (pipettor.set_pid_k_p, 30),
        (pipettor.set_pid_k_d, 1)
    ]
    """
    initialization = [
        (pipettor.set_pid_k_p, 50),
        (pipettor.set_pid_k_d, 0.5),
        (pipettor.set_limit_duty_reverse, -160),
        (pipettor.set_limit_duty_forward, 160),
        (pipettor.set_threshold_brake_forward, 150),
        (pipettor.set_threshold_brake_reverse, -150),
    ]
    """
    sequence = [
        (None, 'Ready to begin.'),

        (pipettor.set_target_mark, 0),

        # Fill wells H,G,F,E with 0.2 mL water each using water in cuvette G
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),

        (y_positioner.set_cuvette_position, 'G'),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.8),

        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),

        (y_positioner.set_well_position, 'H'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.6),
        (vertical_positioner.set_well_position, 'above'),

        (y_positioner.set_well_position, 'G'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.4),
        (vertical_positioner.set_well_position, 'above'),

        (y_positioner.set_well_position, 'F'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        (y_positioner.set_well_position, 'E'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.0),
        (vertical_positioner.set_well_position, 'above'),

        # Fill wells D,C,B,A with 0.2 mL water each using water in cuvette G
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),

        (y_positioner.set_cuvette_position, 'G'),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.8),

        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),

        (y_positioner.set_well_position, 'D'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.6),
        (vertical_positioner.set_well_position, 'above'),

        (y_positioner.set_well_position, 'C'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.4),
        (vertical_positioner.set_well_position, 'above'),

        (y_positioner.set_well_position, 'B'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        (y_positioner.set_well_position, 'A'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_target_mark, 0.0),
        (vertical_positioner.set_well_position, 'above'),

        # Prepare for serial dilution using blue-colored water in cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),

        (y_positioner.set_cuvette_position, 'F'),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.2),

        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),

        # Dilute well H
        (y_positioner.set_well_position, 'H'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        # Dilute well G
        (y_positioner.set_well_position, 'G'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        # Dilute well F
        (y_positioner.set_well_position, 'F'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        # Dilute well E
        (y_positioner.set_well_position, 'E'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        # Dilute well D
        (y_positioner.set_well_position, 'D'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        # Dilute well C
        (y_positioner.set_well_position, 'C'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        # Dilute well B
        (y_positioner.set_well_position, 'B'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (vertical_positioner.set_well_position, 'above'),

        # Dilute well A
        (y_positioner.set_well_position, 'A'),
        (vertical_positioner.set_well_position, 'low'),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (pipettor.set_target_mark, 0.2),
        (pipettor.set_target_mark, 0.0),
        (vertical_positioner.set_well_position, 'above'),

        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
    ]
    """
    sequence = [
        (None, 'Ready to begin.'),

        (pipettor.set_target_mark, 0),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position H
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'H'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position G
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'G'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'F'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position E
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'E'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position D
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'D'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position C
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'C'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position B
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'B'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        # Acquire blue food coloring from cuvette F
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the cuvette column.'),
        (y_positioner.set_cuvette_position, 'F'),
        (pipettor.set_target_mark, 0.02),
        (vertical_positioner.set_cuvette_position, 'mid'),
        (pipettor.set_target_mark, 0.04),

        # Dispense droplet to plate position A
        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
        (None, 'Please move the sample stage to the plate column 1.'),
        (y_positioner.set_well_position, 'A'),
        (vertical_positioner.set_well_position, 'high'),
        (pipettor.set_direct_duty, 255),

        (vertical_positioner.set_target_mark, vertical_positioner.top_mark),
    ]
    """
    targeting = BatchTargeting(
        pipettor, vertical_positioner, y_positioner, sequence, initialization,
        interactive=False
    )

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    for version_channel in ['v0', 'v1', 'v2']:
        dispatcher.receivers[version_channel].append(version_receiver)
    dispatcher.receivers[None].append(echoer)
    for actuator in [pipettor, vertical_positioner, y_positioner]:
        dispatcher.receivers[None].append(actuator)
        actuator.converged_position_listeners.append(targeting)
        actuator.stalled_position_listeners.append(targeting)
        actuator.message_listeners.append(translator)
    dispatcher.receivers[None].append(targeting)

    connection.open()
    monitor.start_reading_lines()
    connection.reset()


if __name__ == '__main__':
    main()

