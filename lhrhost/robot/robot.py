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

    async def align_manually(self):
        """Do a manual alignment of x/y positioning."""
        await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.y.go_to_low_end_position(), self.x.go_to_low_end_position()
        )
        await self.z.go_to_discrete_position('alignment hole')
        await self.prompt(
            'Align the sample stage so that the pipette tip is in the round alignment hole: '
        )
        x_position = await self.x.sensor_position
        self.x.linear_regression[1] = -self.x.linear_regression[0] * x_position
        y_position = await self.y.sensor_position
        self.y.linear_regression[1] = -self.y.linear_regression[0] * y_position
        logger.info('Aligned to the zero position at the alignment hole.')

    async def go_to_alignment_hole(self):
        """Move the pipettor head to the alignment hole."""
        await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.y.go_to_physical_position(0), self.x.go_to_physical_position(0)
        )
        await self.z.go_to_discrete_position('alignment hole')

    async def go_to_cuvette(self, module_name, cuvette_column, cuvette_row):
        """Move the pipettor head to the specified cuvette of the cuvette rack."""
        if self.x.at_cuvette(module_name, cuvette_column):
            await self.z.go_to_cuvette('far above')
        else:
            await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.x.go_to_cuvette(module_name, cuvette_column), self.y.go_to_cuvette(cuvette_row)
        )

    async def go_to_96_well_plate(self, module_name, plate_column, plate_row):
        """Move the pipettor head to the specified well of the 96-well plate."""
        if self.x.at_96_well_plate(module_name, plate_column):
            await self.z.go_to_96_well_plate('far above')
        else:
            await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.x.go_to_96_well_plate(module_name, plate_column),
            self.y.go_to_96_well_plate(plate_row)
        )

    async def intake(self, container, height, volume):
        """Intake fluid at the specified height.

        Container should be either 'cuvette' or '96-well plate'.
        Height should be a discrete z-axis position.
        """
        if container == 'cuvette':
            await self.z.go_to_cuvette(height)
        elif container == '96-well plate':
            await self.z.go_to_96_well_plate(height)
        else:
            raise NotImplementedError('Unknown container \'{}\'!'.format(container))
        await self.p.intake(volume)

    async def intake_precise(self, container, height, volume):
        """Intake fluid at the specified height.

        Container should be either 'cuvette' or '96-well plate'.
        Height should be a discrete z-axis position.
        Volume should be either 20, 30, 40, 50, or 100.
        """
        if container == 'cuvette':
            z_positioner = self.z.go_to_cuvette
        elif container == '96-well plate':
            z_positioner = self.z.go_to_96_well_plate
        else:
            raise NotImplementedError('Unknown container \'{}\'!'.format(container))
        await z_positioner('above')
        await self.p.go_to_pre_intake(volume)
        await z_positioner(height)
        await self.p.intake(volume)

    async def dispense(self, container, height, volume=None):
        """Dispense fluid at the specified height.

        If volume is none, dispenses all syringe contents.
        Container should be either 'cuvette' or '96-well plate'.
        Height should be a discrete z-axis position.
        """
        if container == 'cuvette':
            if not self.z.at_cuvette(height):
                await self.z.go_to_cuvette(height)
        elif container == '96-well plate':
            if not self.z.at_96_well_plate(height):
                await self.z.go_to_96_well_plate(height)
        else:
            raise NotImplementedError('Unknown container \'{}\'!'.format(container))
        await self.p.dispense(volume)
