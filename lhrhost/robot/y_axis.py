"""Abstractions for the y-axis (pipettor head positioner) of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import ManuallyAlignedRobotAxis, ModularRobotAxis


class Axis(ManuallyAlignedRobotAxis, ModularRobotAxis):
    """High-level controller for y-axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self._protocol = LinearActuatorProtocol('YAxis', 'y')

    # Implement RobotAxis

    @property
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return self._protocol

    @property
    def physical_unit(self):
        """Return a string representation of the physical units."""
        return 'cm'

    async def go_to_flat_surface(self, physical_position):
        """Move to the specified physical position for the flat surface."""
        await self.go_to_physical_position(
            self._get_origin_position('flat surface') + physical_position
        )

