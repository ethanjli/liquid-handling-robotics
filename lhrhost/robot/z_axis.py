"""Abstractions for the pipettor axis of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import ContinuousRobotAxis, DiscreteRobotAxis


class Axis(ContinuousRobotAxis, DiscreteRobotAxis):
    """High-level controller for z-axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self._protocol = LinearActuatorProtocol('ZAxis', 'z')

    # Implement RobotAxis

    @property
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return self._protocol

    @property
    def physical_unit(self):
        """Return a string representation of the physical units."""
        return 'cm'

    def at_cuvette(self, cuvette_height):
        """Return whether the axis is already at the height for the cuvette rack."""
        return self.current_discrete_position == ('cuvette', cuvette_height)

    async def go_to_cuvette(self, cuvette_height):
        """Move to the specified height for the cuvette."""
        if not self.at_cuvette(cuvette_height):
            await self.go_to_discrete_position(('cuvette', cuvette_height))

    def at_96_well_plate(self, plate_height):
        """Return whether the axis is already at the height for the cuvette rack."""
        return self.current_discrete_position == ('96-well plate', plate_height)

    async def go_to_96_well_plate(self, plate_height):
        """Move to the specified height for the 96-well plate."""
        if not self.at_96_well_plate(plate_height):
            await self.go_to_discrete_position(('96-well plate', plate_height))
