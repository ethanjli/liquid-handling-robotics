#ifndef LinearActuatorModule_h
#define LinearActuatorModule_h

#include <ASCIISerialIO.h>

#include "LinearActuator.h"

namespace LiquidHandlingRobotics {

//const char kConstantsChannel = 'k';
//const char kLimitsChannel = 'l';
const char kReportingChannel = 'r';
const char kReportingConvergenceChannel = 'c';
const char kReportingStreamingChannel = 's';
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
    bool streamingPosition = false;

    void setup();
    void update();

    bool converged(unsigned int convergenceTime);
    void reportConvergencePosition();
    void reportStreamingPosition();

  private:
    //char constantsChannels[4] = {' ', kConstantsChannel, ' ', '\0'};
    //char limitsChannels[5] = {' ', kLimitsChannel, ' ', ' ', '\0'};
    char reportingConvergenceChannel[4] = {' ', kReportingChannel, kReportingConvergenceChannel, '\0'};
    char reportingStreamingChannel[4] = {' ', kReportingChannel, kReportingStreamingChannel, '\0'};
    char targetingChannel[3] = {' ', kTargetingChannel, '\0'};
};

}

#include "LinearActuatorModule.tpp"

#endif

