#ifndef LinearActuatorModule_h
#define LinearActuatorModule_h

#include <ASCIISerialIO.h>

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
const char kReportingConvergenceChannel = 'c';
const char kReportingStreamingChannel = 's';
// Targeting channel
const char kTargetingChannel = 't';

template <class LinearActuatorParams>
class LinearActuatorModule {
  public:
    LinearActuatorModule(
        MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
        const LinearActuatorParams &linearActuatorParams
    );

    MessageParser &messageParser;

    typename LinearActuatorParams::LinearActuator actuator;
    unsigned int convergenceDelay;
    bool reportedConvergence = false;
    bool reportingConvergencePosition = false;
    bool reportingStreamingPosition = false;
    const char moduleChannel = '\0';

    void setup();
    void update();

    bool converged(unsigned int convergenceTime);
    void reportConvergencePosition();
    void reportStreamingPosition();

  private:
    void onReceivedMessage();
    void onConstantsMessage();
    void onLimitsMessage();
    void onReportingMessage();
    void onTargetingMessage();
};

}

#include "LinearActuatorModule.tpp"

#endif

