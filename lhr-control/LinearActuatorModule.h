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

    using Smoother = LinearPositionControl::Smoother<typename LinearActuator::Position, int>;
    using State = States::LinearActuatorControlMode;

    MessageParser &messageParser;

    LinearActuator actuator;
    LinearPositionControl::StateVariable<State> state;
    Smoother smoother;

    unsigned int convergenceDelay;
    bool reportedConvergence = false;
    bool reportingConvergencePosition = true;

    unsigned int stallTimeout;
    bool reportedStallTimeout = false;
    bool reportingStallTimeoutPosition = true;

    int streamingPositionReportInterval = 0;

    const char moduleChannel = '\0';

    void setup();
    void update();

    bool converged(unsigned int convergenceTime) const;
    bool stalled(unsigned int stallTime) const;

    void reportPosition(char reportingChannel);

  private:
    int streamingPositionClock = 0;
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

