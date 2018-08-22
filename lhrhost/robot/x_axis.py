"""Abstractions for the x-axis (sample stage positioner) of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import ManuallyAlignedRobotAxis, ModularRobotAxis
from lhrhost.util.cli import Prompt


class ManualAxis(ManuallyAlignedRobotAxis, ModularRobotAxis):
    """High-level controller for x-axis."""

    def __init__(self):
        """Initialize member variables."""
        super().__init__()

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
        await self.prompt(
            'Please move the sample platform on the x-axis to {}: '
            .format(discrete_position)
        )
        self.current_discrete_position = discrete_position
        return 0

    # Implement ManuallyAlignedRobotAxis

    async def set_alignment(self):
        """Update the physical calibration to align against the current position."""
        pass

    # Implement ModularRobotAxis

    async def go_to_module_position(self, module_name, position):
        """Move to the position for the specified module."""
        await self.prompt(
            'Please move the sample platform on the x-axis to the {} module\'s '
            '{} position: '
            .format(module_name, position)
        )
        self.current_discrete_position = (module_name, position)
        return 0


class Axis(ManuallyAlignedRobotAxis, ModularRobotAxis):
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
        module_type = self.get_module_type(module_name)
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
        module_type = self.get_module_type(module_name)
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

    def get_module_type(self, module_name):
        """Return the module type of the named module."""
        return self.configuration_tree[module_name]['type']

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

    async def go_to_module_position(self, module_name, position):
        """Move to the position for the specified module."""
        if self.at_module_position(module_name, position):
            return
        await self.go_to_physical_position(
            self._get_module_position(module_name, position)
        )
        self.current_discrete_position = (module_name, position)

    async def go_to_flat_surface(self, module_name, physical_position):
        """Move to the specified physical position for the flat surface."""
        await self.go_to_physical_position(
            self._get_origin_position(module_name) + physical_position
        )
