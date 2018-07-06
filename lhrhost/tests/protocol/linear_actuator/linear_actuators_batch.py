"""Test LinearActuator RPC command functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator, MessagePrinter
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.protocol.linear_actuator import Printer, Protocol
from lhrhost.tests.messaging.transport.batch import (
    Batch, BatchExecutionManager, LOGGING_CONFIG, main
)
from lhrhost.util import batch

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(LOGGING_CONFIG)


class Batch(Batch):
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.z_printer = Printer(
            'Z-Axis', prefix=batch.RESPONSE_PREFIX
        )
        self.y_printer = Printer(
            'Y-Axis', prefix=batch.RESPONSE_PREFIX
        )
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.z = Protocol(
            'ZAxis', 'z',
            response_receivers=[self.z_printer],
            command_receivers=[self.command_printer]
        )
        self.y = Protocol(
            'YAxis', 'y',
            response_receivers=[self.y_printer],
            command_receivers=[self.command_printer]
        )
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.translator = BasicTranslator(
            message_receivers=[self.response_printer, self.z, self.y]
        )
        self.z.command_receivers.append(self.translator)
        self.y.command_receivers.append(self.translator)
        self.response_receiver = ResponseReceiver(
            response_receivers=[self.translator]
        )
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop, response_receiver=self.response_receiver
        )
        self.translator.serialized_message_receivers.append(
            self.transport_manager.command_sender
        )
        self.batch_execution_manager = BatchExecutionManager(
            self.arbiter, self.transport_manager.command_sender, self.test_routine,
            header=batch.OUTPUT_HEADER,
            ready_waiter=self.transport_manager.connection_synchronizer.wait_connected
        )

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Running test routine...')
        await asyncio.gather(self.z.initialized.wait(), self.y.initialized.wait())

        print('Sequential positioning')
        await self.y.feedback_controller.request_complete(720)
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))
        await self.z.feedback_controller.request_complete(0)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        await self.z.feedback_controller.request_complete(1000)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        await self.y.feedback_controller.request_complete(0)
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        print('Concurrent positioning')
        z_task = self.z.feedback_controller.request_complete(0)
        y_task = self.y.feedback_controller.request_complete(720)
        await asyncio.gather(z_task, y_task)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))
        z_task = self.z.feedback_controller.request_complete(1000)
        y_task = self.y.feedback_controller.request_complete(0)
        await asyncio.gather(z_task, y_task)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        print('Concurrent sequential positioning')

        async def z_sequence():
            for i in range(4):
                await self.z.feedback_controller.request_complete(0)
                print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
                await self.z.feedback_controller.request_complete(1000)
                print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))

        async def y_sequence():
            for i in range(4):
                await self.y.feedback_controller.request_complete(0)
                print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))
                await self.y.feedback_controller.request_complete(720)
                print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        await asyncio.gather(z_sequence(), y_sequence())

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
