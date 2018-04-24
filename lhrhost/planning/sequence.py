# Standard imports
import datetime
import itertools
import time

# Local package imports
from lhrhost.serialio.transport import (
    ASCIIConnection, ASCIIMonitor, ASCIIConsole
)
from lhrhost.serialio.dispatch import (
    Message, Dispatcher,
    ASCIITranslator, MessageReceiver, MessageEchoer
)
from lhrhost.modules.actuators import (
    ConvergedPositionReceiver, StalledPositionReceiver
)
from lhrhost.modules.pipettor import Pipettor

class BatchTargeting(ConvergedPositionReceiver, StalledPositionReceiver, MessageReceiver):
    def __init__(self, pipettor, targets, interactive=False):
        super().__init__()
        self.pipettor = pipettor
        self.interactive = interactive
        self.targets = targets
        self.current_step = 0
        self.stalled_steps = 0
        self.initialized = False

    def on_converged_position(self, position_unitless, position_mL_mark):
        if not self.initialized:
            return
        try:
            next_target = next(self.targets)
            print('{}: Completed step {}. '.format(datetime.datetime.now(), self.current_step),
                  end='')
        except IndexError:
            print('Finished the batch sequence!')
            self.pipettor.running = False
            return
        time.sleep(0.5)
        print('Moving to the {:.2f} mark...'.format(next_target), end='')
        self.pipettor.set_target_position(next_target, units=self.pipettor.physical_unit)
        self.current_step += 1

    def on_stalled_position(self, position_unitless, position_mL_mark):
        if not self.initialized:
            return
        try:
            next_target = next(self.targets)
            print('{}: Stalled at step {}. '.format(datetime.datetime.now(), self.current_step),
                  end='')
        except IndexError:
            print('Finished the batch sequence!')
            self.pipettor.running = False
            return
        time.sleep(0.5)
        print('Moving to the {:.2f} mark...'.format(next_target), end='')
        self.pipettor.set_target_position(next_target, units=self.pipettor.physical_unit)
        self.current_step += 1
        self.stalled_steps += 1

    def on_message(self, message):
        if not self.initialized and message.channel == 'yrc':
            self.initialized = True
            print('Initialized. Press enter twice to continue!', end='')
            input()
            message = Message('{}d'.format(self.pipettor.node_prefix), 0)
            for listener in self.pipettor.message_listeners:
                listener.on_message(message)

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    console = ASCIIConsole(connection)

    translator = ASCIITranslator()
    echoer = MessageEchoer(set(['pt', 'prc', 'zrc', 'yrc', 'prt', 'pd']))
    dispatcher = Dispatcher()
    pipettor = Pipettor()
    targeting = BatchTargeting(
        pipettor, itertools.cycle([pipettor.bottom_mark, pipettor.top_mark])
    )

    monitor.listeners.append(translator)
    translator.message_listeners.append(echoer)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    dispatcher.receivers[None].append(pipettor)
    dispatcher.receivers['yrc'].append(targeting)
    pipettor.converged_position_listeners.append(targeting)
    pipettor.stalled_position_listeners.append(targeting)
    pipettor.message_listeners.append(translator)

    connection.open()
    monitor.start_thread()
    console.start_input_loop()
    connection.reset()
    print()
    print('{}/{} steps were stalled, which is an error rate of {:.3f}.'.format(
        targeting.stalled_steps, targeting.current_step, targeting.stalled_steps / targeting.current_step
    ))


if __name__ == '__main__':
    main()

