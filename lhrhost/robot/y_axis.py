"""Abstractions for the pipettor axis of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import ContinuousRobotAxis, DiscreteRobotAxis


class Axis(ContinuousRobotAxis, DiscreteRobotAxis):
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

    async def move_cuvette(self, cuvette_row):
        """Move to the pre-intake position for dispensing precise volumes."""
        await self.go_to_discrete_position(('cuvette', cuvette_row))

    async def move_96_well_plate(self, plate_row):
        """Move to the pre-intake position for dispensing precise volumes."""
        await self.go_to_discrete_position(('96-well plate', plate_row))
