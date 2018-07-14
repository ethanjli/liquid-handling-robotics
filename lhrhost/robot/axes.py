"""Abstractions for the axes of a liquid-handling robot."""

# Standard imports
from abc import abstractmethod

# Local package imiports
from lhrhost.protocol.linear_actuator import Receiver as LinearActuatorReceiver
from lhrhost.util.containers import add_to_tree, get_from_tree
from lhrhost.util.files import load_from_json, save_to_json
from lhrhost.util.interfaces import InterfaceClass

# External imports
import scipy.stats as stats


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

    async def go_to_sensor_position(self, sensor_position):
        """Go to the specified sensor position.

        Returns the final sensor position.
        """
        await self.protocol.feedback_controller.request_complete(
            int(sensor_position)
        )
        await self.protocol.position.request()
        return self.protocol.position.last_response_payload

    async def go_to_end_position(self, speed=255):
        """Go to the farthest allowed sensor position at the specified speed.

        Speed must be given as a signed motor duty cycle.
        """
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

    async def wait_until_initialized(self):
        """Wait until the axis is ready to control."""
        await self.protocol.initialized.wait()

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
    async def position(self):
        """Get the current position of the axis."""
        await self.protocol.position.request()
        return self.last_position

    @property
    def last_position(self):
        """Get the last received position of the axis."""
        return self.protocol.position.last_response_payload


class ContinuousRobotAxis(RobotAxis):
    """High-level controller mixin interface for axes with continuous positions.

    Assumes a linear transformation exists between sensor and physical positions.
    """

    def __init__(self):
        """Initialize member variables."""
        super().__init__()
        self._calibration_samples = []
        self._linear_regression = None

    def clear_calibration_samples(self):
        """Discard the stored calibration data."""
        self._calibration_samples = []
        self._linear_regression = None

    def add_calibration_sample(self, sensor_position, physical_position):
        """Add a (sensor, physical) position pair for calibration."""
        self._linear_regression = None
        self._calibration_samples.append((sensor_position, physical_position))

    def fit_calibration_linear(self):
        """Perform a linear regression on the calibration data and store results.

        Returns the regression slope, intercept, R-value, and standard error.
        """
        linear_regression = stats.linregress(self._calibration_samples)
        self._linear_regression = (
            linear_regression[0], linear_regression[1],
            linear_regression[2], linear_regression[4]
        )
        return self._linear_regression

    @property
    def calibration_data(self):
        """Return a JSON-exportable structure of calibration data."""
        calibration_data = {
            'parameters': {
                'slope': self._linear_regression[0],
                'intercept': self._linear_regression[1],
                'rsquared': self._linear_regression[2],
                'stderr': self._linear_regression[3]
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
        """Load a calibration from a provided JSON file path.

        Default path: 'calibrations/{}_physical.json' where {} is replaced with the
        axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_physical.json'.format(self.name)
        save_to_json(self.calibration_data, json_path)

    @property
    def sensor_to_physical_scaling(self):
        """Return the scaling factor from sensor to physical positions."""
        if self._linear_regression is None:
            self._fit_calibration_linear()
        return self._linear_regression[0]

    @property
    def sensor_to_physical_offset(self):
        """Return the post-scaling offset from sensor to physical positions."""
        if self._linear_regression is None:
            self._fit_calibration_linear()
        return self._linear_regression[1]

    # Implement RobotAxis

    def physical_to_sensor(self, physical_position):
        """Convert a position in physical units to a unitless sensor position."""
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


class DiscreteRobotAxis(RobotAxis):
    """High-level controller mixin for axes with continuous positions."""

    def __init__(self):
        """Initialize member variables."""
        super().__init__()
        self.discrete_sensor_position_tree = {}
        self.discrete_physical_position_tree = {}

    def set_discrete_sensor_position(self, discrete_position, sensor_position):
        """Associate a discrete position with a sensor position."""
        try:
            physical_position = self.discrete_to_physical(
                discrete_position, use_sensor_if_needed=False
            )
        except KeyError:
            physical_position = None
        if physical_position is not None:
            raise KeyError(
                'Discrete position {} is already set to physical position {} {}!'
                .format(discrete_position, physical_position, self.physical_units)
            )
        add_to_tree(
            self.discrete_sensor_position_tree, discrete_position,
            sensor_position
        )

    def set_discrete_physical_position(self, discrete_position, physical_position):
        """Associate a discrete position with a physical position."""
        try:
            sensor_position = self.discrete_to_sensor(
                discrete_position, use_physical_if_needed=False
            )
        except KeyError:
            sensor_position = None
        if sensor_position is not None:
            raise KeyError(
                'Discrete position {} is already set to sensor position {}!'
                .format(discrete_position, sensor_position)
            )
        add_to_tree(
            self.discrete_physical_position_tree, discrete_position,
            physical_position
        )

    def discrete_to_sensor(self, discrete_position, use_physical_if_needed=True):
        """Convert a discrete position to a sensor position."""
        try:
            return get_from_tree(
                self.discrete_sensor_position_tree, discrete_position
            )
        except KeyError:
            if use_physical_if_needed:
                physical_position = get_from_tree(
                    self.discrete_physical_position_tree, discrete_position
                )
                return self.physical_to_sensor(physical_position)
            else:
                raise

    def discrete_to_physical(self, discrete_position, use_sensor_if_needed=True):
        """Convert a discrete position to a physical position."""
        try:
            return get_from_tree(
                self.discrete_physical_position_tree, discrete_position
            )
        except KeyError:
            if use_sensor_if_needed:
                sensor_position = get_from_tree(
                    self.discrete_sensor_position_tree, discrete_position
                )
                return self.sensor_to_physical(sensor_position)
            else:
                raise

    async def go_to_discrete_position(self, discrete_position):
        """Go to the specified discrete position.

        Returns the physical position error between the desired physical position
        and the final physical position.
        """
        physical_position = self.discrete_to_physical(discrete_position)
        sensor_position = self.discrete_to_sensor(discrete_position)
        final_sensor_position = await self.go_to_sensor_position(sensor_position)
        final_physical_position = self.sensor_to_physical(final_sensor_position)
        return physical_position - final_physical_position
