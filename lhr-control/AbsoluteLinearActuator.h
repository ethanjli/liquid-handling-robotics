#ifndef AbsoluteLinearActuator_h
#define AbsoluteLinearActuator_h

#include <AbsoluteLinearPositionControl.h>
#include <ASCIISerialIO.h>

namespace LiquidHandlingRobotics {

struct AbsoluteLinearActuatorParams {
  char actuatorChannelPrefix;

  MotorPort motorPort;
  uint8_t potentiometerPin;
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

//const char kConstantsChannel = 'k';
//const char kLimitsChannel = 'l';
const char kReportingChannel = 'r';
const char kReportingConvergenceChannel = 'c';
const char kReportingStreamingChannel = 's';
const char kTargetingChannel = 't';

class AbsoluteLinearActuator {
  public:
    AbsoluteLinearActuator(
        MessageParser &messageParser, LinearPositionControl::Components::Motors &motors,
        const AbsoluteLinearActuatorParams &params
    );

    MessageParser &messageParser;

    LinearPositionControl::AbsoluteLinearActuator actuator;
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

