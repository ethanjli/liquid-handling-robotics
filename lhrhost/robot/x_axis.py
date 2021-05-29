"""Abstractions for the x-axis (sample stage positioner) of a liquid-handling robot."""

# Local package imiports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import (
    ConfigurableRobotAxis, ManuallyAlignedRobotAxis, ModularRobotAxis
)
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

    # Implement PresetRobotAxis

    def preset_to_physical(self, physical_position):
        """Convert a position in physical units to a physical position."""
        return 0

    async def go_to_preset_position(self, preset_position):
        """Go to the specified preset position.

        Returns the sensor position error between the desired sensor position
        and the final sensor position.
        """
        await self.prompt(
            'Please move the sample platform on the x-axis to {}: '
            .format(preset_position)
        )
        self.current_preset_position = preset_position
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
        self.current_preset_position = (module_name, position)
        return 0


class Axis(ManuallyAlignedRobotAxis, ConfigurableRobotAxis):
    """High-level controller for x-axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self._protocol = LinearActuatorProtocol('XAxis', 'x')
        self.configuration = None
        self.configuration_tree = None

    # Implement RobotAxis

    @property
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return self._protocol

    @property
    def physical_unit(self):
        """Return a string representation of the physical units."""
        return 'cm'

    async def go_to_flat_surface(self, module_name, physical_position):
        """Move to the specified physical position for the flat surface."""
        await self.go_to_physical_position(
            self._get_origin_position(module_name) + physical_position
        )

    # Implement ModularRobotAxis

    def get_module_mount_position(self, presets_tree, module_name):
        """Get the position of the module's mount."""
        module_mount = self.get_module_mount(module_name)
        mount_type = 'even' if module_mount % 2 == 0 else 'odd'
        mount_params = presets_tree['mount']
        return (
            mount_params['{} origin'.format(mount_type)] +
            self.get_indexed_offset(
                mount_params, module_mount,
                origin_index_key='{} origin index'.format(mount_type)
            )
        )
