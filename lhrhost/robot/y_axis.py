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

    def _get_module_position(self, module_type, index):
        module_params = self.preset_physical_position_tree[module_type]
        min_index = module_params['min index']
        max_index = module_params['max index']
        origin_index = module_params['origin index']
        if (index < min_index) or (index > max_index):
            raise IndexError
        return (
            self._get_origin_position(module_type) +
            (index - origin_index) * module_params['increment']
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
        if self.at_module_position(module_type, position):
            return
        await self.go_to_physical_position(
            self._get_module_position(module_type, position)
        )
        self.current_preset_position = (module_type, position)

    async def go_to_flat_surface(self, physical_position):
        """Move to the specified physical position for the flat surface."""
        await self.go_to_physical_position(
            self._get_origin_position('flat surface') + physical_position
        )
