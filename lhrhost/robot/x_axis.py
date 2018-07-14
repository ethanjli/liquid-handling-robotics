"""Abstractions for the pipettor axis of a liquid-handling robot."""

# Local package imiports
from lhrhost.robot.axes import DiscreteRobotAxis
from lhrhost.util.cli import Prompt


class ManualAxis(DiscreteRobotAxis):
    """High-level controller for x-axis."""

    def __init__(self):
        """Initialize member variables."""
        super().__init__()

    def at_cuvette(self):
        """Return whether the axis is already at the column for the cuvette rack."""
        return self.current_discrete_position == 'the cuvette rack'

    async def go_to_cuvette(self):
        """Move to the column for the cuvette rack."""
        if self.at_cuvette():
            return
        self.current_discrete_position = 'the cuvette rack'
        await self.go_to_discrete_position(self.current_discrete_position)

    def at_96_well_plate(self, plate_column):
        """Return whether the axis is already at the column for the cuvette rack."""
        return (
            self.current_discrete_position ==
            'column {} of the 96-well plate'.format(plate_column)
        )

    async def go_to_96_well_plate(self, plate_column):
        """Move to the specified row position for the 96-well plate."""
        if self.at_96_well_plate(plate_column):
            return
        self.current_discrete_position = \
            'column {} of the 96-well plate'.format(plate_column)
        await self.go_to_discrete_position(self.current_discrete_position)

    # Implement RobotAxis

    @property
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return None

    def physical_to_sensor(self, physical_position):
        """Convert a position in physical units to a unitless sensor position."""
        return 0

    def sensor_to_physical(self, sensor_position):
        """Convert a unitless sensor position to a position in physical units."""
        return 0

    async def wait_until_initialized(self):
        """Wait until the axis is ready to control."""
        self.prompt = Prompt(end='', flush=True)

    @property
    def physical_unit(self):
        """Return a string representation of the physical units."""
        return None

    # Implement DiscreteRobotAxis

    def discrete_to_physical(self, physical_position):
        """Convert a position in physical units to a physical position."""
        return 0

    async def go_to_discrete_position(self, discrete_position):
        """Go to the specified discrete position.

        Returns the sensor position error between the desired sensor position
        and the final sensor position.
        """
        await self.prompt('Please move the sample platform to {}: '.format(
            discrete_position
        ))
        self.current_discrete_position = discrete_position
        return 0
