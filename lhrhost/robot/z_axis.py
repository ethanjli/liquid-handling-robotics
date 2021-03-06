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
