"""Abstractions for the y-axis (pipettor head positioner) of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import ContinuousRobotAxis, DiscreteRobotAxis


class Axis(ContinuousRobotAxis, DiscreteRobotAxis):
    """High-level controller for y-axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self._protocol = LinearActuatorProtocol('YAxis', 'y')

    def _get_origin_position(self, module_type):
        return (
            self.discrete_physical_position_tree['mount'] +
            self.discrete_physical_position_tree[module_type]['origin']
        )

    def _get_module_position(self, module_type, index):
        module_params = self.discrete_physical_position_tree[module_type]
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

    def at_cuvette(self, cuvette_row):
        """Return whether the axis is already at the row for the cuvette rack."""
        return self.current_discrete_position == ('cuvette', cuvette_row)

    async def go_to_cuvette(self, cuvette_row):
        """Move to the row position for the specified cuvette."""
        if self.at_cuvette(cuvette_row):
            return
        await self.go_to_physical_position(
            self._get_module_position('cuvette', cuvette_row)
        )
        self.current_discrete_position = ('cuvette', cuvette_row)

    def at_96_well_plate(self, plate_row):
        """Return whether the axis is already at the row for the cuvette rack."""
        return self.current_discrete_position == ('96-well plate', plate_row)

    async def go_to_96_well_plate(self, plate_row):
        """Move to the specified row position for the 96-well plate."""
        if self.at_96_well_plate(plate_row):
            return
        await self.go_to_physical_position(
            self._get_module_position('96-well plate', plate_row)
        )
        self.current_discrete_position = ('96-well plate', plate_row)

    async def go_to_flat_surface(self, physical_position):
        """Move to the specified physical position for the flat surface."""
        await self.go_to_physical_position(
            self._get_origin_position('flat surface') + physical_position
        )
