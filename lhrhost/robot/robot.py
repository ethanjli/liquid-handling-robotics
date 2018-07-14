"""Abstractions for a liquid-handling robot."""

# Standard imports
import asyncio

# Local package imports
from lhrhost.robot.p_axis import Axis as PAxis
from lhrhost.robot.x_axis import ManualAxis as XAxis
from lhrhost.robot.y_axis import Axis as YAxis
from lhrhost.robot.z_axis import Axis as ZAxis


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
        self.prompt = None

    async def wait_until_initialized(self):
        """Wait until all axes are initialized."""
        await asyncio.gather(
            self.p.wait_until_initialized(),
            self.z.wait_until_initialized(),
            self.y.wait_until_initialized(),
            self.x.wait_until_initialized()
        )
        self.prompt = self.x.prompt

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

    async def go_to_alignment_hole(self):
        """Move the pipettor head to the alignment hole."""
        await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.y.go_to_low_end_position(), self.x.go_to_96_well_plate(1)
        )
        await self.z.go_to_discrete_position('alignment hole')
        await self.prompt(
            'Align the sample stage so that the pipette tip is in the alignment hole: '
        )

    async def go_to_cuvette(self, cuvette_row):
        """Move the pipettor head to the specified cuvette of the cuvette rack."""
        if self.x.at_cuvette():
            await self.z.go_to_cuvette('far above')
        else:
            await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.x.go_to_cuvette(), self.y.go_to_cuvette(cuvette_row)
        )

    async def go_to_96_well_plate(self, plate_column, plate_row):
        """Move the pipettor head to the specified well of the 96-well plate."""
        if self.x.at_96_well_plate(plate_column):
            await self.z.go_to_96_well_plate('far above')
        else:
            await self.z.go_to_high_end_position()
        await asyncio.gather(
            self.x.go_to_96_well_plate(plate_column),
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
        await z_positioner('far above')
        await self.p.go_to_pre_intake(volume)
        await z_positioner(height)
        await self.p.intake(volume)
        await self.z.go_to_high_end_position()

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
