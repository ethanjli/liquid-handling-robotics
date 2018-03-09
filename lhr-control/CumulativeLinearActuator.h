#ifndef CumulativeLinearActuator_h
#define CumulativeLinearActuator_h

#include <CumulativeLinearPositionControl.h>
#include <ASCIISerialIO.h>

#include "LinearActuator.h"

namespace LiquidHandlingRobotics {

struct CumulativeLinearActuatorParams {
  char actuatorChannelPrefix;

  MotorPort motorPort;
  int minPosition;
  int maxPosition;

  double pidKp;
  double pidKd;
  double pidKi;
  int pidSampleTime;

  int feedforward;
  int brakeLowerThreshold;
  int brakeUpperThreshold;

  bool swapMotorPolarity;
  int convergenceDelay;

  int minDuty;
  int maxDuty;
};

class CumulativeLinearActuator {
  public:
    CumulativeLinearActuator(
        MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
        const CumulativeLinearActuatorParams &params
    );

    MessageParser &messageParser;

    LinearPositionControl::CumulativeLinearActuator actuator;
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

#endif

