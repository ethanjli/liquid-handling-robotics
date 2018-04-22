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
// Targeting channel
const char kTargetingChannel = 't';

const float kConstantsFixedPointScaling = 100;

template <class LinearActuatorParams>
class LinearActuatorModule {
  public:
    LinearActuatorModule(
        MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
        const LinearActuatorParams &linearActuatorParams
    );

    using LinearActuator = typename LinearActuatorParams::LinearActuator;
    using Smoother = LinearPositionControl::Smoother<typename LinearActuator::Position, int>;

    MessageParser &messageParser;

    LinearActuator actuator;
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
};

}

#include "LinearActuatorModule.tpp"

#endif

