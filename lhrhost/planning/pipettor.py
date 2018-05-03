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
    ASCIITranslator, MessageReceiver, MessageEchoer, VersionReceiver
)
from lhrhost.modules.actuators import (
    ConvergedPositionReceiver, StalledPositionReceiver
)
from lhrhost.modules.pipettor import Pipettor

class BatchTargeting(ConvergedPositionReceiver, StalledPositionReceiver, MessageReceiver):
    def __init__(self, pipettor, targets, max_steps=None, interactive=False):
        super().__init__()
        self.pipettor = pipettor
        self.interactive = interactive
        self.targets = targets
        self.current_step = 0
        self.stalled_steps = 0
        self.max_steps = max_steps
        self.initialized = False

    def on_converged_position(self, actuator, position_unitless, position_mL_mark):
        if not self.initialized:
            return
        try:
            next_target = next(self.targets)
            print('{}: Completed step {}. '.format(datetime.datetime.now(), self.current_step),
                  end='')
        except (IndexError, StopIteration):
            self.quit()
        if self.current_step % 1000 == 0 and self.current_step > 0:
            self.print_stats()
        time.sleep(0.5)
        print('Moving to the {:.2f} mark...'.format(next_target), end='')
        #if next_target == self.pipettor.bottom_mark:
        #    self.pipettor.set_direct_duty(255)
        #else:
        #    self.pipettor.set_target_position(next_target, units=self.pipettor.physical_unit)
        self.pipettor.set_target_position(next_target, units=self.pipettor.physical_unit)
        self.current_step += 1
        if self.max_steps is not None and self.current_step > self.max_steps:
            self.quit()

    def on_stalled_position(self, actuator, position_unitless, position_mL_mark):
        if not self.initialized:
            return
        try:
            next_target = next(self.targets)
            print('{}: Stalled at step {}. '.format(datetime.datetime.now(), self.current_step),
                  end='')
        except (IndexError, StopIteration):
            self.quit()
        time.sleep(0.5)
        if self.current_step % 500 == 0 and self.current_step > 0:
            self.print_stats()
        print('Moving to the {:.2f} mark...'.format(next_target), end='')
        #if next_target == self.pipettor.bottom_mark:
        #    self.pipettor.set_direct_duty(255)
        #else:
        #    self.pipettor.set_target_position(next_target, units=self.pipettor.physical_unit)
        self.pipettor.set_target_position(next_target, units=self.pipettor.physical_unit)
        self.current_step += 1
        if self.max_steps and self.current_step > self.max_steps:
            self.quit()
        self.stalled_steps += 1

    def on_message(self, message):
        #if message.channel == 'yrc':
        if message.channel == 'zrc':
            if not self.initialized:
                self.initialized = True
                #message = Message('yt', 720)
                #for listener in self.pipettor.message_listeners:
                #    listener.on_message(message)
                self.pipettor.set_pid_k_d(1)
                self.pipettor.set_pid_k_p(30)
                self.pipettor.set_limit_position_low(980)
                for listener in self.pipettor.message_listeners:
                    listener.on_message(message)
            #else:
                #message = Message('zt', 300)
                #for listener in self.pipettor.message_listeners:
                #    listener.on_message(message)
                message = Message('{}d'.format(self.pipettor.node_prefix), 0)
                for listener in self.pipettor.message_listeners:
                    listener.on_message(message)

    def print_stats(self):
        print('{}/{} steps were stalled, which is an error rate of {:.3f}.'.format(
            self.stalled_steps, self.current_step, self.stalled_steps / self.current_step
        ))

    def quit(self):
        print('Finished the batch sequence!')
        print()
        self.print_stats()
        self.pipettor.running = False
        raise KeyboardInterrupt

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    console = ASCIIConsole(connection)

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
    targeting = BatchTargeting(
        pipettor, itertools.cycle([pipettor.bottom_mark, pipettor.top_mark]), None
    )

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    for version_channel in ['v0', 'v1', 'v2']:
        dispatcher.receivers[version_channel].append(version_receiver)
    dispatcher.receivers[None].append(echoer)
    dispatcher.receivers[None].append(pipettor)
    #dispatcher.receivers['yrc'].append(targeting)
    dispatcher.receivers['zrc'].append(targeting)
    pipettor.converged_position_listeners.append(targeting)
    pipettor.stalled_position_listeners.append(targeting)
    pipettor.message_listeners.append(translator)

    connection.open()
    monitor.start_thread()
    console.start_input_loop()
    monitor._thread.join()
    connection.reset()


if __name__ == '__main__':
    main()

