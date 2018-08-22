"""Abstractions for a liquid-handling robot."""

# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.robot.p_axis import Axis as PAxis
from lhrhost.robot.x_axis import Axis as XAxis
from lhrhost.robot.y_axis import Axis as YAxis
from lhrhost.robot.z_axis import Axis as ZAxis
from lhrhost.util.cli import Prompt

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Robot(object):
    """High-level controller for 4-axis liquid-handling robot.

    Currently the x-axis is moved manually by the user.
    """

    def __init__(self):
        """Initialize member variables."""
        self.p = PAxis()
        self.z = ZAxis()
        self.y = YAxis()
        self.x = XAxis()
        self.prompt = Prompt(end='', flush=True)

    def register_messaging_stack(self, messaging_stack):
        """Associate a messaging stack with the robot.

        The messaging stack is used for host-peripheral communication.
        """
        messaging_stack.register_response_receivers(
            self.p.protocol, self.z.protocol, self.y.protocol, self.x.protocol
        )
        messaging_stack.register_command_senders(
            self.p.protocol, self.z.protocol, self.y.protocol, self.x.protocol
        )

    async def wait_until_initialized(self):
        """Wait until all axes are initialized."""
        await asyncio.gather(
            self.p.wait_until_initialized(),
            self.z.wait_until_initialized(),
            self.y.wait_until_initialized(),
            self.x.wait_until_initialized()
        )

    async def synchronize_values(self):
        """Request the values of all protocol channels."""
        await self.p.synchronize_values()
        await self.z.synchronize_values()
        await self.y.synchronize_values()

    async def load_calibrations(self):
        """Load calibration parameters from json files."""
        self.p.load_calibration_json()
        self.p.load_discrete_json()
        self.p.load_pid_json()
        self.z.load_calibration_json()
        self.z.load_discrete_json()
        self.y.load_calibration_json()
        self.y.load_discrete_json()
        self.x.load_calibration_json()
        self.x.load_discrete_json()

    async def go_to_alignment_hole(self):
        """Move the pipettor head to the alignment hole."""
        await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.y.go_to_alignment_hole(), self.x.go_to_alignment_hole()
        )
        await self.z.go_to_alignment_hole()

    async def align_manually(self):
        """Do a manual alignment of x/y positioning."""
        await self.go_to_alignment_hole()
        await self.prompt(
            'Please move the x-axis and the y-axis so that the pipette tip is '
            'directly over the round alignment hole: '
        )
        await asyncio.gather(self.x.set_alignment(), self.y.set_alignment())
        logger.info('Aligned to the zero position at the alignment hole.')

    async def go_to_module_position(
        self, module_name, x_position, y_position, z_position=None
    ):
        """Move the pipettor head to the specified x/y position of the module."""
        module_type = self.x.get_module_type(module_name)
        if (
            self.x.current_discrete_position is not None and
            self.x.current_discrete_position[0] == module_name
        ):
            await self.z.go_to_module_position(module_type, 'far above')
        else:
            await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.x.go_to_module_position(module_name, x_position),
            self.y.go_to_module_position(module_type, y_position)
        )
        if z_position is not None:
            await self.z.go_to_module_position(module_type, 'far above')

    async def intake(self, module_type, volume, height=None):
        """Intake fluid at the specified height.

        Height should be a discrete z-axis position or a physical z-axis position.
        """
        if height is not None:
            try:
                await self.z.go_to_module_position(module_type, height)
            except KeyError:
                await self.z.go_to_physical_position(height)
        await self.p.intake(volume)

    async def intake_precise(self, module_type, volume, height=None):
        """Intake fluid at the specified height.

        Height should be a discrete z-axis position or a physical z-axis position.
        Volume should be either 20, 30, 40, 50, or 100.
        """
        if height is None:
            if self.z.current_discrete_position is not None:
                height = self.z.current_discrete_position[1]
            else:
                height = await self.z.physical_position
        await self.z.go_to_module_position(module_type, 'above')
        await self.p.go_to_pre_intake(volume)
        try:
            await self.z.go_to_module_position(module_type, height)
        except KeyError:
            await self.z.go_to_physical_position(height)
        await self.p.intake(volume)

    async def dispense(self, module_type, volume=None, height=None):
        """Dispense fluid at the specified height.

        If volume is none, dispenses all syringe contents.
        Height should be a discrete z-axis position or a physical z-axis position.
        """
        if height is not None:
            try:
                await self.z.go_to_module_position(module_type, height)
            except KeyError:
                await self.z.go_to_physical_position(height)
        await self.p.dispense(volume)
