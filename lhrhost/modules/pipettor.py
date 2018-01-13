# Standard imports
import time
import argparse

# Local package imports
from lhrhost.serialio.transport import (
    ASCIIConnection, ASCIIMonitor
)
from lhrhost.serialio.dispatch import (
    Message, MessageReceiver, Dispatcher,
    ASCIITranslator
)
from lhrhost.util.math import map_range

class Pipettor(MessageReceiver):
    def __init__(self):
        self.stabilized_position_listeners = []
        self.message_listeners = []
        self.running = False

        self.top_position = 11  # unitless
        self.top_mark = 0.95  # mL mark
        self.bottom_position = 999  # unitless
        self.bottom_mark = 0.03  # mL mark

    def on_message(self, message):
        if message.channel != '':
            return
        converged_position = int(message.payload)
        print('Stabilized at the {:.2f} mL mark!'
              .format(self.to_mL_mark(converged_position)))
        for listener in self.stabilized_position_listeners:
            listener.on_stabilized_position(
                converged_position, self.to_mL_mark(converged_position)
            )

    def set_target_position(self, target_position):
        message = Message('', target_position)
        for listener in self.message_listeners:
            listener.on_message(message)

    def set_target_mark(self, target_mark):
        self.set_target_position(self.to_unitless_position(target_mark))

    # Unit conversion

    def to_mL_mark(self, unitless_position):
        return map_range(
            unitless_position, self.bottom_position, self.top_position,
            self.bottom_mark, self.top_mark
        )

    def to_unitless_position(self, mL_mark):
        return int(map_range(
            mL_mark, self.bottom_mark, self.top_mark,
            self.bottom_position, self.top_position
        ))

class Targeting(object):
    def __init__(self, pipettor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipettor = pipettor

    def on_stabilized_position(self, position_unitless, position_mL_mark):
        pass

class InteractiveTargeting(Targeting):
    def on_stabilized_position(self, position_unitless, position_mL_mark):
        need_input = True
        while need_input:
            try:
                user_input = input(
                    'Please specify the next position to go to between {} mL and {} mL: '
                    .format(self.pipettor.bottom_mark, self.pipettor.top_mark)
                )
                user_input = self.parse_input(user_input)
                need_input = False
            except ValueError:
                print('Invalid input: {}'.format(user_input))
                pass
            except EOFError:
                self.pipettor.running = False
                return
        self.pipettor.set_target_mark(user_input)

    def parse_input(self, user_input):
        if user_input.lower().endswith('ml'):
            user_input = user_input[:-2]
        user_input = user_input.strip()
        user_input = float(user_input)
        if (user_input < self.pipettor.bottom_mark or
                user_input > self.pipettor.top_mark):
            raise ValueError
        return user_input

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection, daemon_thread=False)
    translator = ASCIITranslator(channel_start=None, channel_end=None)
    dispatcher = Dispatcher()
    pipettor = Pipettor()
    targeting = InteractiveTargeting(pipettor)

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    dispatcher.receivers[''].append(pipettor)
    pipettor.stabilized_position_listeners.append(targeting)
    pipettor.message_listeners.append(translator)

    connection.open()
    monitor.start_reading_lines()
    connection.reset()


if __name__ == '__main__':
    main()

