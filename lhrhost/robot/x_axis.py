"""Abstractions for the pipettor axis of a liquid-handling robot."""

# Local package imiports
from lhrhost.robot.axes import DiscreteRobotAxis


class ManualXAxis(DiscreteRobotAxis):
    """High-level controller for x-axis."""

    def __init__(self, prompt):
        """Initialize member variables."""
        super().__init__()
        self.prompt = prompt

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
        return 0
