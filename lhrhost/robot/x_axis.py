"""Abstractions for the x-axis (sample stage positioner) of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import ContinuousRobotAxis, DiscreteRobotAxis
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
        """Move to the specified column position for the 96-well plate."""
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


class Axis(ContinuousRobotAxis, DiscreteRobotAxis):
    """High-level controller for x-axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self._protocol = LinearActuatorProtocol('XAxis', 'x')
        self.configuration = None
        self.configuration_tree = None

    def _get_origin_position(self, module_name):
        mount_params = self.discrete_physical_position_tree['mount']
        mount_index = self.configuration_tree[module_name]['mount']
        min_index = mount_params['min index']
        max_index = mount_params['max index']
        if (mount_index < min_index) or (mount_index > max_index):
            raise IndexError
        module_type = self.configuration_tree[module_name]['type']
        index_type = 'even' if mount_index % 2 == 0 else 'odd'
        origin_type = '{} origin'.format(index_type)
        origin_index = mount_params['{} index'.format(origin_type)]
        return (
            mount_params[origin_type] +
            (mount_index - origin_index) *
            mount_params['increment'] +
            self.discrete_physical_position_tree[module_type]['origin']
        )

    def _get_module_position(self, module_name, index):
        module_type = self.configuration_tree[module_name]['type']
        module_params = self.discrete_physical_position_tree[module_type]
        min_index = module_params['min index']
        max_index = module_params['max index']
        origin_index = module_params['origin index']
        if (ord(index) < ord(min_index)) or (ord(index) > ord(max_index)):
            raise IndexError
        return (
            self._get_origin_position(module_name) +
            (ord(index) - ord(origin_index)) * module_params['increment']
        )

    def _at_module(self, module_name, position):
        return self.current_discrete_position == (module_name, position)

    async def _go_to_module(self, module_name, position):
        if self._at_module(module_name, position):
            return
        await self.go_to_physical_position(
            self._get_module_position(module_name, position)
        )
        self._current_discrete_position = (module_name, position)

    # Extend DiscreteRobotAxis

    def load_discrete_json(self, json_path=None):
        """Load a discrete positions tree from the provided JSON file path.

        Default path: 'calibrations/{}_discrete.json' where {} is replaced with the
        axis name.
        """
        super().load_discrete_json(json_path)
        self.configuration = self.trees['configuration']
        self.configuration_tree = self.trees['configurations'][self.configuration]

    # Implement RobotAxis

    @property
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return self._protocol

    @property
    def physical_unit(self):
        """Return a string representation of the physical units."""
        return 'cm'

    def at_cuvette(self, module_name, cuvette_column):
        """Return whether the axis is already at the column for the cuvette rack."""
        return self._at_module(module_name, cuvette_column)

    async def go_to_cuvette(self, module_name, cuvette_column):
        """Move to the column position for the specified cuvette."""
        await self._go_to_module(module_name, cuvette_column)

    def at_96_well_plate(self, module_name, plate_column):
        """Return whether the axis is already at the column for the cuvette rack."""
        return self._at_module(module_name, plate_column)

    async def go_to_96_well_plate(self, module_name, plate_column):
        """Move to the specified column position for the 96-well plate."""
        await self._go_to_module(module_name, plate_column)

    async def go_to_flat_surface(self, module_name, physical_position):
        """Move to the specified physical position for the flat surface."""
        await self.go_to_physical_position(
            self._get_origin_position(module_name) + physical_position
        )
