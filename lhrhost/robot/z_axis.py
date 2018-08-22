"""Abstractions for the pipettor axis of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import AlignedRobotAxis, ContinuousRobotAxis, ModularRobotAxis


class Axis(ModularRobotAxis, AlignedRobotAxis, ContinuousRobotAxis):
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

    async def go_to_module_position(self, module_type, position):
        """Move to the position for the specified module."""
        print('z-axis going to module', module_type, 'position', position)
        if self.at_module_position(module_type, position):
            return
        await self.go_to_discrete_position((module_type, position))
