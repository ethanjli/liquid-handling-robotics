#ifndef Pipettor_h
#define Pipettor_h

#define LIBCALL_ENABLEINTERRUPT
#include <AbsoluteLinearPositionControl.h>
#include <ASCIISerialIO.h>

namespace LiquidHandlingRobotics {

class Pipettor {
  public:
    Pipettor(
        ChannelParser &channelParser, IntParser &intParser,
        LinearPositionControl::Components::Motors &motors, MotorPort motorPort = M1,
        uint8_t potentiometerPin = A0, int minPosition = 11, int maxPosition = 999,
        double pidKp = 8, double pidKd = 0.1, double pidKi = 0.1, int pidSampleTime = 20,
        bool swapMotorPolarity = false, int feedforward = 7, int brakeThreshold = 80,
        unsigned int convergenceDelay = 100
    );

    ChannelParser &channelParser;
    IntParser &intParser;

    LinearPositionControl::AbsoluteLinearActuator actuator;
    unsigned int convergenceDelay;
    bool reportedConvergence = false;
    bool streamingPosition = false;

    void setup();
    void update();

    bool converged(unsigned int convergenceTime);
    void reportConvergencePosition();
    void reportStreamingPosition();
};

}

#endif

