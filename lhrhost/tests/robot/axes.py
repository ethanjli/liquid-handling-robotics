"""Runs some basic axes class tests."""

# Local package imports
from lhrhost.robot.axes import ContinuousRobotAxis, DiscreteRobotAxis


class TestContinuousRobotAxis(ContinuousRobotAxis):
    """Test derived class for ContinuousRobotAxis."""

    # Implement RobotAxis

    def protocol(self):
        """Return the associated linear actuator protocol."""
        return None

    def physical_unit(self):
        """Return a string representation of the physical units."""
        return None


class TestDiscreteRobotAxis(DiscreteRobotAxis):
    """Test derived class for DiscreteRobotAxis."""

    # Implement RobotAxis

    def protocol(self):
        """Return the associated linear actuator protocol."""
        return None

    def physical_unit(self):
        """Return a string representation of the physical units."""
        return None

    def physical_to_sensor(self, physical_position):
        """Convert a position in physical units to a unitless sensor position."""
        return physical_position * 10

    def sensor_to_physical(self, sensor_position):
        """Convert a unitless sensor position to a position in physical units."""
        return sensor_position / 10


def test_continuous():
    """Test the ContinuousRobotAxis class."""
    continuous = TestContinuousRobotAxis()
    continuous.add_calibration_sample(0, 1)
    continuous.add_calibration_sample(1, 4)
    assert continuous.fit_calibration_linear() == (3.0, 1.0, 1.0, 0.0)
    assert continuous.sensor_to_physical(0) == 1
    assert continuous.sensor_to_physical(0.5) == 2.5
    assert continuous.sensor_to_physical(1) == 4
    assert continuous.sensor_to_physical(2) == 7
    assert continuous.physical_to_sensor(1) == 0
    assert continuous.physical_to_sensor(2.5) == 0.5
    assert continuous.physical_to_sensor(4) == 1
    assert continuous.physical_to_sensor(7) == 2


def test_discrete():
    """Test the DiscreteRobotAxis class."""
    discrete = TestDiscreteRobotAxis()
    discrete.set_discrete_sensor_position(('cuvette', 1), 10)
    discrete.set_discrete_sensor_position(('cuvette', 2), 20)
    discrete.set_discrete_sensor_position(('96-well plate row', 'a'), 123)
    discrete.set_discrete_sensor_position(('96-well plate row', 'b'), 456)
    discrete.set_discrete_sensor_position(('96-well plate row', 'c'), 789)
    discrete.set_discrete_sensor_position('foobar', 42)
    try:
        discrete.set_discrete_physical_position(('cuvette', 1), 20)
        assert False
    except KeyError:
        assert True
    discrete.set_discrete_physical_position(('cuvette', 3), 3)
    assert discrete.discrete_to_sensor(('cuvette', 1)) == 10
    assert discrete.discrete_to_physical(('cuvette', 1)) == 1
    assert discrete.discrete_to_sensor(('cuvette', 2)) == 20
    assert discrete.discrete_to_physical(('cuvette', 2)) == 2
    assert discrete.discrete_to_sensor(('cuvette', 3)) == 30
    assert discrete.discrete_to_physical(('cuvette', 3)) == 3
    assert discrete.discrete_to_sensor(('96-well plate row', 'a')) == 123
    assert discrete.discrete_to_sensor(('96-well plate row', 'b')) == 456
    assert discrete.discrete_to_sensor(('96-well plate row', 'c')) == 789
    assert discrete.discrete_to_sensor('foobar') == 42


def main():
    """Run some tests of axes classes."""
    test_continuous()
    test_discrete()


if __name__ == '__main__':
    main()
