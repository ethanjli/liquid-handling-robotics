# Standard imports
import datetime
import itertools

# Local package imports
from lhrhost.serialio.transport import (
    ASCIIConnection, ASCIIMonitor
)
from lhrhost.serialio.dispatch import (
    Message, Dispatcher,
    ASCIITranslator
)
from lhrhost.modules.actuators import ConvergedPositionReceiver
from lhrhost.modules.pipettor import Pipettor

class BatchTargeting(ConvergedPositionReceiver):
    def __init__(self, pipettor, targets, interactive=False):
        super().__init__()
        self.pipettor = pipettor
        self.interactive = interactive
        self.targets = targets
        self.current_step = 0

    def on_converged_position(self, position_unitless, position_mL_mark):
        try:
            next_target = next(self.targets)
            print('{}: Completed step {}. '.format(datetime.datetime.now(), self.current_step),
                  end='')
        except IndexError:
            print('Finished the batch sequence!')
            self.pipettor.running = False
            return
        if self.interactive:
            input('Press enter to move the pipette to the {:.2f} mark: '.format(next_target))
        else:
            print('Moving to the {:.2f} mark...'.format(next_target), end='')
        self.pipettor.set_target_position(next_target, units=self.pipettor.physical_unit)
        self.current_step += 1

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    translator = ASCIITranslator()
    dispatcher = Dispatcher()
    pipettor = Pipettor()
    targeting = BatchTargeting(
        pipettor, itertools.cycle([pipettor.bottom_mark, pipettor.top_mark])
    )

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    dispatcher.receivers[None].append(pipettor)
    pipettor.converged_position_listeners.append(targeting)
    pipettor.message_listeners.append(translator)

    connection.open()
    try:
        monitor.start_reading_lines()
    except KeyboardInterrupt:
        pass
    connection.reset()


if __name__ == '__main__':
    main()

