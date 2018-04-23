#ifndef LinearActuatorModule_h
#define LinearActuatorModule_h

#include <ASCIISerialIO.h>
#include <Smoothing.h>

#include "LinearActuator.h"

namespace LiquidHandlingRobotics {

// Constants channel
const char kConstantsChannel = 'k';
const char kConstantsProportionalChannel = 'p';
const char kConstantsDerivativeChannel = 'd';
const char kConstantsIntegralChannel = 'i';
const char kConstantsFeedforwardChannel = 'f';
// Limits channel
const char kLimitsChannel = 'l';
const char kLimitsPositionChannel = 'p';
const char kLimitsDutyChannel = 'd';
const char kLimitsBrakeChannel = 'b';
const char kLimitsLowerSubchannel = 'l';
const char kLimitsUpperSubchannel = 'h';
// Reporting channel
const char kReportingChannel = 'r';
const char kReportingQueryChannel = 'q';
const char kReportingConvergenceChannel = 'c';
const char kReportingStallTimeoutChannel = 't';
const char kReportingStreamingChannel = 's';
// PID Targeting channel
const char kTargetingChannel = 't';
// Direct Duty channel
const char kDutyChannel = 'd';

const float kConstantsFixedPointScaling = 100;

namespace States {
  enum class LinearActuatorControlMode : uint8_t {
    ready, pidTargeting, dutyControl
  };
}

template <class LinearActuator>
class LinearActuatorModule {
  public:
    LinearActuatorModule(
        MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
        char actuatorChannelPrefix,
        MotorPort motorPort, uint8_t sensorId,
        int minPosition, int maxPosition,
        int minDuty, int maxDuty,
        double pidKp, double pidKd, double pidKi,
        int pidSampleTime,
        int feedforward,
        int brakeLowerThreshold, int brakeUpperThreshold,
        bool swapMotorPolarity,
        int convergenceDelay,
        int stallTimeout, float stallSmootherSnapMultiplier, int stallSmootherMax,
        bool stallSmootherEnableSleep, float stallSmootherActivityThreshold
    );

    using Position = typename LinearActuator::Position;
    using Smoother = LinearPositionControl::Smoother<Position, int>;
    using State = States::LinearActuatorControlMode;

    MessageParser &messageParser;

    LinearActuator actuator;
    LinearPositionControl::StateVariable<State> state;
    Smoother smoother;

    void setup();
    void update();

    bool converged(unsigned int convergenceTime = 0) const;
    bool stopped(unsigned int convergenceTime = 0) const;
    bool stalled(unsigned int stallTime = 0) const;

    void targetPosition(Position position);
    void reportPosition(char reportingChannel);
    void setDirectDuty(int duty);

  private:
    bool setupCompleted = false;

    const char moduleChannel = '\0';

    // Parameters
    unsigned int convergenceDelay;
    unsigned int stallTimeout;

    // Convergence reporting state variables
    bool reportedConvergence = false;
    bool reportingConvergencePosition = true;
    // Stall timeout reporting state variables
    bool reportedStallTimeout = false;
    bool reportingStallTimeoutPosition = true;
    // Position streaming state variable
    int streamingPositionReportInterval = 0;
    int streamingPositionClock = 0;
    // Position query state variable
    int queryPositionCountdown = 0;

    void onReceivedMessage(unsigned int channelParsedLength);
    void onConstantsMessage(unsigned int channelParsedLength);
    void onLimitsMessage(unsigned int channelParsedLength);
    void onReportingMessage(unsigned int channelParsedLength);
    void onTargetingMessage(unsigned int channelParsedLength);
    void onDutyMessage(unsigned int channelParsedLength);
};

}

#include "LinearActuatorModule.tpp"

#endif

