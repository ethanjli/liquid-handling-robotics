"""Abstractions for the pipettor axis of a liquid-handling robot."""

# Local package imports
from lhrhost.protocol.linear_actuator import Protocol as LinearActuatorProtocol
from lhrhost.robot.axes import ContinuousRobotAxis, DiscreteRobotAxis
from lhrhost.util.files import load_from_json, save_to_json


class Axis(ContinuousRobotAxis, DiscreteRobotAxis):
    """High-level controller for pipettor axis."""

    def __init__(self):
        """Initialize member variables.."""
        super().__init__()
        self.position_pid_params = []
        self.volume_pid_params = []
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

    def load_pid_json(self, json_path=None):
        """Load a discrete positions tree from the provided JSON file path.

        Default path: 'calibrations/{}_discrete.json' where {} is replaced with the
        axis name.
        """
        trees = super().load_pid_json(json_path)
        self.volume_tunings = trees['volumes']

    def save_pid_json(self, json_path=None):
        """Save a discrete positions tree to the provided JSON file path.

        Default path: 'calibrations/{}_physical.json' where {} is replaced with the
        axis name.
        """
        if json_path is None:
            json_path = 'calibrations/{}_pid.json'.format(self.name)
        save_to_json({
            'default': self.default_tuning,
            'target positions': self.target_position_tunings,
            'volumes': self.volume_tunings
        }, json_path)

    async def go_to_pre_intake(self, volume):
        """Move to the pre-intake position for dispensing precise volumes."""
        await self.go_to_discrete_position(('pre-intake', int(volume * 1000)))

    async def intake(self, volume):
        """Intake the specified volume."""
        return await self.move_by_physical_delta(volume)

    async def dispense(self, volume=None):
        """Dispense by the specified volume.

        By default, dispenses all contents.
        """
        if volume is None:
            await self.go_to_low_end_position()
        else:
            await self.move_by_physical_delta(-volume)
