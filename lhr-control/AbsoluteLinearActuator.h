#ifndef AbsoluteLinearActuator_h
#define AbsoluteLinearActuator_h

#define LIBCALL_ENABLEINTERRUPT
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
  int brakeThreshold;

  bool swapMotorPolarity;
  int convergenceDelay;
};

const char kThresholdChannel = 't';
const char kConvergenceChannel = 'c';
const char kStreamingChannel = 's';

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
    char thresholdChannel[3] = {' ', kThresholdChannel, '\0'};
    char convergenceChannel[3] = {' ', kConvergenceChannel, '\0'};
    char streamingChannel[3] = {' ', kStreamingChannel, '\0'};

};

}

#endif

