"""Abstractions for the axes of a liquid-handling robot."""

# Standard imports
from abc import abstractmethod

# Local package imiports
from lhrhost.protocol.linear_actuator import Receiver as LinearActuatorReceiver
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.util.containers import add_to_tree, get_from_tree
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
        self._calibration_data = []
        self._linear_regression = None

    def clear_calibration_samples(self):
        """Discard the stored calibration data."""
        self._calibration_data = []
        self._linear_regression = None

    def add_calibration_sample(self, sensor_position, physical_position):
        """Add a (sensor, physical) position pair for calibration."""
        self._linear_regression = None
        self._calibration_data.append((sensor_position, physical_position))

    def fit_calibration_linear(self):
        """Perform a linear regression on the calibration data and store results.

        Returns the regression slope, intercept, R-value, and standard error.
        """
        linear_regression = stats.linregress(self._calibration_data)
        self._linear_regression = (
            linear_regression[0], linear_regression[1],
            linear_regression[2], linear_regression[4]
        )
        return self._linear_regression

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


class PAxis(ContinuousRobotAxis, DiscreteRobotAxis):
    """High-level controller for pipettor axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self._protocol = LinearActuatorProtocol('PAxis', 'p')

    # Implement RobotAxis

    @property
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return self._protocol

    @property
    def physical_unit(self):
        """Return a string representation of the physical units."""
        return 'mL mark'


class ZAxis(ContinuousRobotAxis, DiscreteRobotAxis):
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


class YAxis(ContinuousRobotAxis, DiscreteRobotAxis):
    """High-level controller for y-axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self._protocol = LinearActuatorProtocol('YAxis', 'y')

    # Implement RobotAxis

    @property
    def protocol(self):
        """Return the associated linear actuator protocol."""
        return self._protocol

    @property
    def physical_unit(self):
        """Return a string representation of the physical units."""
        return 'cm'


class ManualXAxis(DiscreteRobotAxis):
    """High-level controller for x-axis."""

    def __init__(self, prompt):
        """Initialize member variables."""
        super().__init__()
        self.prompt = prompt

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
        return 0
