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

    def _get_origin_position(self, module_type):
        return (
            self.preset_physical_position_tree['mount']['value'] +
            self.preset_physical_position_tree[module_type]['origin']
        )

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
        await self.go_to_preset_position((module_type, position))

    async def go_to_flat_surface(self, physical_position):
        """Move to the specified physical position for the flat surface."""
        await self.go_to_physical_position(
            self._get_origin_position('flat surface') + physical_position
        )

    # Implement ModularRobotAxis

    def parse_indexed_position(self, module_params, preset_position):
        """Parse a preset indexed position tree node into an actual preset position."""
        (module_type, index) = preset_position
        return (
            self._get_origin_position(module_type) +
            self.get_indexed_offset(module_params, index)
        )
