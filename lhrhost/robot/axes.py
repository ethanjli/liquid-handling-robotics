"""Abstractions for the axes of a liquid-handling robot."""

# Standard imports
import logging
from abc import abstractmethod

# Local package imiports
from lhrhost.protocol.linear_actuator import Receiver as LinearActuatorReceiver
from lhrhost.util.containers import add_to_tree, get_from_tree
from lhrhost.util.files import load_from_json, save_to_json
from lhrhost.util.interfaces import InterfaceClass

# External imports
import scipy.stats as stats

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RobotAxis(LinearActuatorReceiver, metaclass=InterfaceClass):
    """High-level controller mixin interface for axes with physical position units."""

    @property
    @abstractmethod
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return None

    @abstractmethod
    def physical_to_sensor(self, physical_position):
        """Convert a position in physical units to a unitless sensor position."""
        pass

    @abstractmethod
    def sensor_to_physical(self, sensor_position):
        """Convert a unitless sensor position to a position in physical units."""
        pass

    @property
    @abstractmethod
    def physical_unit(self):
        """Return a string representation of the physical units."""
        pass

    def load_tunings_json(self, json_path=None):
        """Load localized controller tunings from the provided JSON file path.

        Default path: 'calibrations/{}_tunings.json' where {} is replaced with
        the axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_tunings.json'.format(self.name)
        trees = load_from_json(json_path)
        self.default_tuning = trees['default']
        self.target_position_tunings = trees['target positions']
        return trees

    def save_tunings_json(self, json_path=None):
        """Save a localized controller tunings tree to the provided JSON file path."""
        if json_path is None:
            json_path = 'calibrations/{}_tunings.json'.format(self.name)
        save_to_json({
            'default': self.default_tuning,
            'target positions': self.target_position_tunings
        }, json_path)

    async def go_to_sensor_position(
        self, sensor_position, apply_tunings=True, restore_tunings=True
    ):
        """Go to the specified sensor position.

        Returns the final sensor position.
        """
        if apply_tunings:
            current_tuning = self.default_tuning
            for tuning in self.target_position_tunings:
                if sensor_position >= tuning['min'] and sensor_position < tuning['max']:
                    current_tuning = tuning
            else:
                logger.debug(
                    'PID tunings for sensor position {} unspecified, using defaults.'
                    .format(int(sensor_position))
                )
            kp = current_tuning['pid']['kp']
            kd = current_tuning['pid']['kd']
            motor_limits = current_tuning['limits']['motor']
            duty_forwards_max = motor_limits['forwards']['max']
            duty_forwards_min = motor_limits['forwards']['min']
            duty_backwards_max = motor_limits['backwards']['max']
            duty_backwards_min = motor_limits['backwards']['min']
            (prev_kp, prev_kd, prev_ki) = await self.set_pid_gains(kp=kp, kd=kd)
            (
                prev_duty_forwards_max, prev_duty_forwards_min,
                prev_duty_backwards_max, prev_duty_backwards_min
            ) = await self.set_motor_limits(
                forwards_max=duty_forwards_max, forwards_min=duty_forwards_min,
                backwards_max=duty_backwards_max, backwards_min=duty_backwards_min
            )
        await self.protocol.feedback_controller.request_complete(
            int(sensor_position)
        )
        if apply_tunings and restore_tunings:
            await self.set_pid_gains(kp=prev_kp, kd=prev_kd, ki=prev_ki)
            await self.set_motor_limits(
                forwards_max=duty_forwards_max, forwards_min=duty_forwards_min,
                backwards_max=duty_backwards_max, backwards_min=duty_backwards_min
            )
        return self.protocol.position.last_response_payload

    async def go_to_low_end_position(self, speed=None):
        """Go to the lowest possible sensor position at the maximum allowed speed.

        Speed must be given as a signed motor duty cycle.
        """
        if speed is None:
            speed = (
                self.protocol.feedback_controller.limits.motor
                .backwards.high.last_response_payload
            )
        await self.protocol.motor.request_complete(speed)
        await self.protocol.position.request()
        return self.protocol.position.last_response_payload

    async def go_to_high_end_position(self, speed=None):
        """Go to the highest possible sensor position at the maximum allowed speed.

        Speed must be given as a signed motor duty cycle.
        """
        if speed is None:
            speed = (
                self.protocol.feedback_controller.limits.motor
                .forwards.high.last_response_payload
            )
        await self.protocol.motor.request_complete(speed)
        await self.protocol.position.request()
        return self.protocol.position.last_response_payload

    async def go_to_physical_position(self, physical_position):
        """Go to the specified physical position.

        Returns the final physical position.
        """
        sensor_position = self.physical_to_sensor(physical_position)
        sensor_position = await self.go_to_sensor_position(sensor_position)
        return self.sensor_to_physical(sensor_position)

    async def move_by_sensor_delta(self, sensor_delta):
        """Go forwards/backwards by the specified sensor displacement.

        Returns the final physical displacement.
        """
        position = await self.sensor_position
        target_position = position + sensor_delta
        final_position = await self.go_to_sensor_position(target_position)
        return final_position - position

    async def move_by_physical_delta(self, physical_delta):
        """Go forwards/backwards by the specified physical displacement.

        Returns the final physical displacement.
        """
        position = await self.physical_position
        target_position = position + physical_delta
        final_position = await self.go_to_physical_position(target_position)
        return final_position - position

    async def wait_until_initialized(self):
        """Wait until the axis is ready to control."""
        await self.protocol.initialized.wait()
        await self.protocol.position.initialized.wait()
        await self.protocol.motor.initialized.wait()

    async def synchronize_values(self):
        """Request the values of all channels."""
        await self.protocol.request_all()

    @property
    def name(self):
        """Return the name of the axis."""
        return self.protocol.node_name

    @property
    def last_position_limits(self):
        """Get the last received position limits of the axis."""
        return (
            self.protocol.feedback_controller.limits.position.low.last_response_payload,
            self.protocol.feedback_controller.limits.position.high.last_response_payload
        )

    @property
    async def sensor_position(self):
        """Get the current sensor position of the axis."""
        await self.protocol.position.request()
        return self.last_sensor_position

    @property
    def last_sensor_position(self):
        """Get the last received sensor position of the axis."""
        return self.protocol.position.last_response_payload

    @property
    async def physical_position(self):
        """Get the current physical position of the axis."""
        await self.protocol.position.request()
        return self.last_physical_position

    @property
    def last_physical_position(self):
        """Get the last received physical position of the axis."""
        return self.sensor_to_physical(self.last_sensor_position)

    async def set_pid_gains(self, kp=None, kd=None, ki=None, floating_point=True):
        """Set values for the PID gains whose values are specified.

        Returns the previous values of the gains.
        """
        pid_protocol = self.protocol.feedback_controller.pid
        prev_kp = pid_protocol.kp.last_response_payload
        prev_kd = pid_protocol.kd.last_response_payload
        prev_ki = pid_protocol.ki.last_response_payload
        if kp is not None and prev_kp != int(kp * 100 if floating_point else kp):
            await pid_protocol.kp.request(int(kp * 100 if floating_point else kp))
        if kd is not None and prev_kd != int(kd * 100 if floating_point else kp):
            await pid_protocol.kd.request(int(kd * 100 if floating_point else kp))
        if ki is not None and prev_ki != int(ki * 100 if floating_point else kp):
            await pid_protocol.ki.request(int(ki * 100 if floating_point else kp))
        return (
            prev_kp / 100 if floating_point else prev_kp,
            prev_kd / 100 if floating_point else prev_kd,
            prev_ki / 100 if floating_point else prev_ki
        )

    async def set_motor_limits(
        self, forwards_max=None, forwards_min=None, backwards_max=None, backwards_min=None
    ):
        """Set values for the motor duty cycle limits where specified.

        Returns the previous values of the limits.
        """
        limits_protocol = self.protocol.feedback_controller.limits.motor
        prev_forwards_max = limits_protocol.forwards.high.last_response_payload
        prev_forwards_min = limits_protocol.forwards.low.last_response_payload
        prev_backwards_max = -limits_protocol.backwards.high.last_response_payload
        prev_backwards_min = -limits_protocol.backwards.low.last_response_payload
        if forwards_max is not None and prev_forwards_max != int(forwards_max):
            await limits_protocol.forwards.high.request(int(forwards_max))
        if forwards_min is not None and prev_forwards_min != int(forwards_min):
            await limits_protocol.forwards.high.request(int(forwards_min))
        if backwards_max is not None and prev_backwards_max != int(backwards_max):
            await limits_protocol.backwards.high.request(int(-backwards_max))
        if backwards_min is not None and prev_backwards_min != int(backwards_min):
            await limits_protocol.backwards.high.request(int(-backwards_min))
        return (
            prev_forwards_max, prev_forwards_min,
            prev_backwards_max, prev_backwards_min
        )


class ContinuousRobotAxis(RobotAxis):
    """High-level controller mixin interface for axes with continuous positions.

    Assumes a linear transformation exists between sensor and physical positions.
    """

    def __init__(self):
        """Initialize member variables."""
        super().__init__()
        self._calibration_samples = []
        self.linear_regression = None

    def clear_calibration_samples(self):
        """Discard the stored calibration data."""
        self._calibration_samples = []
        self.linear_regression = None

    def add_calibration_sample(self, sensor_position, physical_position):
        """Add a (sensor, physical) position pair for calibration."""
        self.linear_regression = None
        self._calibration_samples.append((sensor_position, physical_position))

    def fit_calibration_linear(self):
        """Perform a linear regression on the calibration data and store results.

        Returns the regression slope, intercept, R-value, and standard error.
        The regression is for physical_position = slope * sensor_position + intercept.
        """
        linear_regression = stats.linregress(self._calibration_samples)
        self.linear_regression = [
            linear_regression[0], linear_regression[1],
            linear_regression[2], linear_regression[4]
        ]
        return self.linear_regression

    @property
    def calibration_data(self):
        """Return a JSON-exportable structure of calibration data."""
        calibration_data = {
            'parameters': {
                'slope': self.linear_regression[0],
                'intercept': self.linear_regression[1],
                'rsquared': self.linear_regression[2],
                'stderr': self.linear_regression[3]
            },
            'physical unit': self.physical_unit,
            'samples': [
                {
                    'sensor': calibration_sample[0],
                    'physical': calibration_sample[1]
                }
                for calibration_sample in self._calibration_samples
            ]
        }
        return calibration_data

    def load_calibration(self, calibration_data):
        """Load a calibration from the provided calibration data structure."""
        self._calibration_samples = [
            (calibration_sample['sensor'], calibration_sample['physical'])
            for calibration_sample in calibration_data['samples']
        ]
        self.fit_calibration_linear()

    def load_calibration_json(self, json_path=None):
        """Load a calibration from a provided JSON file path.

        Default path: 'calibrations/{}_physical.json' where {} is replaced with the
        axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_physical.json'.format(self.name)
        self.load_calibration(load_from_json(json_path))

    def save_calibration_json(self, json_path=None):
        """Save the calibration to the provided JSON file path.

        Default path: 'calibrations/{}_physical.json' where {} is replaced with the
        axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_physical.json'.format(self.name)
        save_to_json(self.calibration_data, json_path)

    @property
    def sensor_to_physical_scaling(self):
        """Return the scaling factor from sensor to physical positions."""
        if self.linear_regression is None:
            self._fit_calibration_linear()
        return self.linear_regression[0]

    @property
    def sensor_to_physical_offset(self):
        """Return the post-scaling offset from sensor to physical positions."""
        if self.linear_regression is None:
            self._fit_calibration_linear()
        return self.linear_regression[1]

    # Implement RobotAxis

    def physical_to_sensor(self, physical_position):
        """Convert a position in physical units to a unitless integer sensor position."""
        return (
            (physical_position - self.sensor_to_physical_offset) /
            self.sensor_to_physical_scaling
        )

    def sensor_to_physical(self, sensor_position):
        """Convert a unitless sensor position to a position in physical units."""
        return (
            self.sensor_to_physical_scaling * sensor_position +
            self.sensor_to_physical_offset
        )


class PresetRobotAxis(RobotAxis):
    """High-level controller mixin for axes with preset positions."""

    def __init__(self):
        """Initialize member variables."""
        super().__init__()
        self.preset_sensor_position_tree = {}
        self.preset_physical_position_tree = {}
        self.current_preset_position = None

    def set_preset_sensor_position(self, preset_position, sensor_position):
        """Associate a preset position with a sensor position."""
        try:
            physical_position = self.preset_to_physical(
                preset_position, use_sensor_if_needed=False
            )
        except (AttributeError, KeyError):
            physical_position = None
        if physical_position is not None:
            raise KeyError(
                'Preset position {} is already set to physical position {} {}!'
                .format(preset_position, physical_position, self.physical_units)
            )
        add_to_tree(
            self.preset_sensor_position_tree, preset_position,
            sensor_position
        )

    def set_preset_physical_position(self, preset_position, physical_position):
        """Associate a preset position with a physical position."""
        try:
            sensor_position = self.preset_to_sensor(
                preset_position, use_physical_if_needed=False
            )
        except KeyError:
            sensor_position = None
        if sensor_position is not None:
            raise KeyError(
                'Preset position {} is already set to sensor position {}!'
                .format(preset_position, sensor_position)
            )
        add_to_tree(
            self.preset_physical_position_tree, preset_position,
            physical_position
        )

    def get_preset_position(self, presets_tree, preset_position):
        """Get an actual position from a preset position tree node."""
        position_node = get_from_tree(presets_tree, preset_position)
        if isinstance(position_node, dict):
            try:
                type = position_node['type']
            except KeyError:
                raise TypeError(
                    'Type-less preset position {}!'.format(preset_position)
                )
            if type == 'implicit':
                raise TypeError(
                    'Cannot use implicit preset position {}!'.format(preset_position)
                )
            if type == 'constants':
                raise TypeError(
                    'Cannot use partially-specified preset position {}!'
                    .format(preset_position)
                )
            if type == 'constant':
                return position_node['value']
            raise NotImplementedError(
                'Unknown type {} for preset position {}!'
                .format(type, preset_position)
            )
        return position_node

    def preset_to_sensor(self, preset_position, use_physical_if_needed=True):
        """Convert a preset position to a sensor position."""
        try:
            return self.get_preset_position(
                self.preset_sensor_position_tree, preset_position
            )
        except KeyError:
            if use_physical_if_needed:
                physical_position = self.preset_to_physical(preset_position, False)
                return self.physical_to_sensor(physical_position)
            else:
                raise

    def preset_to_physical(self, preset_position, use_sensor_if_needed=True):
        """Convert a preset position to a physical position."""
        try:
            return self.get_preset_position(
                self.preset_physical_position_tree, preset_position
            )
        except KeyError:
            if use_sensor_if_needed:
                sensor_position = self.preset_to_sensor(preset_position, False)
                return self.sensor_to_physical(sensor_position)
            else:
                raise

    async def go_to_preset_position(self, preset_position, force_go=False):
        """Go to the specified preset position.

        Returns the physical position error between the desired physical position
        and the final physical position.
        """
        if self.current_preset_position == preset_position and not force_go:
            return
        physical_position = self.preset_to_physical(preset_position)
        final_physical_position = await self.go_to_physical_position(physical_position)
        if isinstance(preset_position, str):
            preset_position = (preset_position,)
        self.current_preset_position = preset_position
        return physical_position - final_physical_position

    def load_preset_json(self, json_path=None):
        """Load a preset positions tree from the provided JSON file path.

        Default path: 'calibrations/{}_preset.json' where {} is replaced with the
        axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_preset.json'.format(self.name)
        trees = load_from_json(json_path)
        self.preset_physical_position_tree = trees['physical']
        self.preset_sensor_position_tree = trees['sensor']
        return trees

    def save_preset_json(self, json_path=None):
        """Save a preset positions tree to the provided JSON file path.

        Default path: 'calibrations/{}_physical.json' where {} is replaced with the
        axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_preset.json'.format(self.name)
        save_to_json({
            'physical': self.preset_physical_position_tree,
            'sensor': self.preset_sensor_position_tree
        }, json_path)

    # Implement RobotAxis

    async def go_to_sensor_position(self, sensor_position):
        """Go to the specified sensor position.

        Returns the final sensor position.
        """
        self.current_preset_position = None
        return await super().go_to_sensor_position(sensor_position)

    async def go_to_low_end_position(self, speed=None):
        """Go to the lowest possible sensor position at the maximum allowed speed.

        Speed must be given as a signed motor duty cycle.
        """
        try:
            return await self.go_to_preset_position('low end')
        except (KeyError, TypeError):
            if self.current_preset_position == ('low end',):
                return
            self.current_preset_position = ('low end',)
            return await super().go_to_low_end_position(speed)

    async def go_to_high_end_position(self, speed=None):
        """Go to the highest possible sensor position at the maximum allowed speed.

        Speed must be given as a signed motor duty cycle.
        """
        try:
            return await self.go_to_preset_position('high end')
        except (KeyError, TypeError):
            if self.current_preset_position == ('high end',):
                return
            self.current_preset_position = ('high end',)
            return await super().go_to_high_end_position(speed)


class AlignedRobotAxis(PresetRobotAxis):
    """High-level controller mixin for axes with alignment."""

    def at_alignment_hole(self):
        """Return whether the axis is already at the alignment hole."""
        return self.current_preset_position == ('alignment hole',)

    async def go_to_alignment_hole(self):
        """Move to the alignment hole."""
        if self.at_alignment_hole():
            return
        try:
            await self.go_to_preset_position('alignment hole')
        except TypeError:
            await self.go_to_physical_position(0)
            self.current_preset_position = ('alignment hole',)


class ManuallyAlignedRobotAxis(AlignedRobotAxis, ContinuousRobotAxis):
    """High-level controller mixin for axes with manual alignment."""

    async def set_alignment(self):
        """Update the physical calibration to align against the current position."""
        position = await self.sensor_position
        self.linear_regression[1] = -self.linear_regression[0] * position


class ModularRobotAxis(PresetRobotAxis):
    """High-level controller mixin for axes with modular sets of positions."""

    def at_module(self, module):
        """Return whether the axis is already at the module.

        Module may be the module's name or type, depending on the axis.
        """
        return self.current_preset_position[0] == module

    def at_module_position(self, module, position):
        """Return whether the axis is already at the position for the module.

        Module may be the module's name or type, depending on the axis.
        """
        return self.current_preset_position == (module, position)

    def get_indexed_offset(self, module_params, index, origin_index_key='origin index'):
        """Return the physical offset for the provided module indexed preset position."""
        def to_num(index):
            if isinstance(index, str) and len(index) == 1:
                return ord(index)
            return index
        index = to_num(index)
        min_index = to_num(module_params['min index'])
        max_index = to_num(module_params['max index'])
        origin_index = to_num(module_params[origin_index_key])
        if (index < min_index) or (max_index is not None and index > max_index):
            raise IndexError(
                'Index {} is out of the range ({}, {})!'
                .format(index, min_index, max_index)
            )
        return (index - origin_index) * module_params['increment']

    def get_continuous_offset(self, module_params, offset):
        """Return the physical offset for the provided module continuous preset position."""
        min = module_params['min']
        max = module_params['max']
        if (offset < min) or (max is not None and offset > max):
            raise ValueError(
                'Offset {} is out of the range ({}, {})!'
                .format(offset, min, max)
            )
        return offset

    def get_module_mount_position(self, presets_tree, module_type):
        """Get the position of the module's mount."""
        return self.get_preset_position(presets_tree, 'mount')

    def get_module_offset_position(self, module_params, offset):
        """Get the position on the  module relative to the module's origin."""
        if module_params['type'] == 'indexed':
            return self.get_indexed_offset(module_params, offset)
        elif module_params['type'] == 'continuous':
            return self.get_continuous_offset(module_params, offset)
        else:
            raise NotImplementedError(
                'Unknown module type {}!'.format(module_params['type'])
            )

    def get_module_position(self, presets_tree, module_params, preset_position):
        """Get the actual position from a preset module position tree node."""
        (module, offset) = preset_position
        return (
            self.get_module_mount_position(presets_tree, module) +
            module_params['origin'] +
            self.get_module_offset_position(module_params, offset)
        )

    async def go_to_module_position(self, module, position):
        """Move to the position for the specified module."""
        await self.go_to_preset_position((module, position))

    # Implement PresetRobotAxis

    def get_preset_position(self, presets_tree, preset_position):
        """Get an actual position from a preset position tree node."""
        try:
            return super().get_preset_position(presets_tree, preset_position)
        except KeyError:
            module_params = get_from_tree(presets_tree, preset_position[0])
            return self.get_module_position(presets_tree, module_params, preset_position)


class ConfigurableRobotAxis(ModularRobotAxis):
    """High-level controller mixin for axes with reconfigurable sets of modules."""

    def get_module_type(self, module_name):
        """Return the module type of the named module."""
        return self.configuration_tree[module_name]['type']

    def get_module_mount(self, module_name):
        """Return the module type of the named module."""
        return self.configuration_tree[module_name]['mount']

    # Implement PresetRobotAxis

    def load_preset_json(self, json_path=None):
        """Load a preset positions tree from the provided JSON file path.

        Default path: 'calibrations/{}_preset.json' where {} is replaced with the
        axis name.
        """
        trees = super().load_preset_json(json_path)
        if self.configuration is None:
            self.configuration = trees['default configuration']
        self.configurations = trees['configurations']
        self.configuration_tree = trees['configurations'][self.configuration]

    def save_preset_json(self, json_path=None):
        """Save a preset positions tree to the provided JSON file path.

        Default path: 'calibrations/{}_physical.json' where {} is replaced with the
        axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_preset.json'.format(self.name)
        save_to_json({
            'physical': self.preset_physical_position_tree,
            'sensor': self.preset_sensor_position_tree,
            'default configuration': self.configuration,
            'configurations': self.configurations
        }, json_path)

    def get_preset_position(self, presets_tree, preset_position):
        """Get an actual position from a preset position tree node."""
        try:
            return super().get_preset_position(presets_tree, preset_position)
        except KeyError:
            module_name = preset_position[0]
            module_type = self.get_module_type(module_name)
            module_params = get_from_tree(presets_tree, module_type)
            return self.get_module_position(presets_tree, module_params, preset_position)

