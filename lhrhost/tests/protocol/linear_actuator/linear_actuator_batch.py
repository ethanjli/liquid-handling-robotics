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
        self.protocol_printer = Printer(
            'Z-Axis', prefix=batch.RESPONSE_PREFIX
        )
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.protocol = Protocol(
            'ZAxis', 'z',
            response_receivers=[self.protocol_printer],
            command_receivers=[self.command_printer]
        )
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.translator = BasicTranslator(
            message_receivers=[self.response_printer, self.protocol]
        )
        self.protocol.command_receivers.append(self.translator)
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
        await asyncio.sleep(5.0)

        print('RPC-style with empty payloads:')
        await self.protocol.request()
        await self.protocol.position.request()
        await self.protocol.smoothed_position.request()
        await self.protocol.motor.request()
        await self.protocol.motor.motor_polarity.request()
        await self.protocol.motor.timer_timeout.request()
        await self.protocol.position.notify.request()
        await self.protocol.position.notify.interval.request()
        await self.protocol.position.notify.change_only.request()
        await self.protocol.position.notify.number.request()

        print('Motor direct duty control')
        # Test basic motor direct duty control
        await self.protocol.motor.request_complete(-255)
        await self.protocol.motor.request_complete(255)
        await self.protocol.motor.request_complete(-100)
        # Test motor polarity setting
        await self.protocol.motor.motor_polarity.request(-1)
        await self.protocol.motor.request_complete(-150)
        await self.protocol.motor.motor_polarity.request(1)
        await self.protocol.motor.request_complete(-100)
        # Test timer timeout
        await self.protocol.motor.timer_timeout.request(200)
        for i in range(10):
            await self.protocol.motor.request_complete(150)
            await asyncio.sleep(0.4)
        await self.protocol.motor.timer_timeout.request(10000)

        print('Motor direct duty control with position notification')
        await self.protocol.position.notify.change_only.request(0)
        task = self.protocol.position.notify.request_complete_time_interval(20, 100)
        await asyncio.sleep(1.0)
        await self.protocol.motor.request(-80)
        await task

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
