#ifndef LinearActuatorModule_h
#define LinearActuatorModule_h

#include <elapsedMillis.h>

#include <Smoothing.h>
#include <LinearActuator.h>

#include "Messages.h"

namespace LiquidHandlingRobotics {

namespace Channels {
  namespace LinearActuatorProtocol {
    const char kPosition = 'p';
    namespace Position {
      // This includes Notify channels
    }
    const char kSmoothedPosition = 's';
    namespace SmoothedPosition {
      const char kSnapMultiplier = 's';
      const char kRangeLow = 'l';
      const char kRangeHigh = 'h';
      const char kActivityThreshold = 't';
      // This includes Notify channels
    }
    const char kMotor = 'm';
    namespace Motor {
      const char kStallProtectorTimeout = 's';
      const char kTimerTimeout = 't';
      const char kPolarity = 'p';
    }
    const char kFeedbackController = 'f';
    namespace FeedbackController {
      const char kConvergenceTimeout = 'c';
      const char kLimits = 'l';
      namespace Limits {
        // This includes kPosition
        namespace Position {
          // This includes kLow/kHigh
        }
        // This includes kMotor
        namespace Motor {
          const char kForwards = 'f';
          namespace Forwards {
            // This includes kLow/kHigh
          }
          const char kBackwards = 'b';
          namespace Backwards {
            // This includes kLow/kHigh
          }
        }
        // These are not channels at this level, but shared names of other child channels
        const char kLow = 'l';
        const char kHigh = 'h';
      }
      const char kPID = 'p';
      namespace PID {
        const char kKp = 'p';
        const char kKd = 'd';
        const char kKi = 'i';
        const char kSampleInterval = 's';
      }
    }
    // These are not channels at this level, but shared names of other child channels
    const char kNotify = 'n';
    namespace Notify {
      const char kInterval = 'i';
      const char kChangeOnly = 'c';
      const char kNumber = 'n';
    }
  }
}

const float kConstantsFixedPointScaling = 100;

float fixedPointToFloat(int fixedPointNum);
float floatToFixedPoint(float floatNum);

namespace States {
  enum class NotifierMode : uint8_t {
    silent = 0, iterationIntervals = 1, timeIntervals = 2
  };
}

template <class Messager, class SignalType>
class Notifier {
  public:
    Notifier(
        Messager &messager, const SignalType &signalValue,
        char axisChannel, char signalChannel
    );

    using State = States::NotifierMode;

    State state = State::silent;
    bool changeOnly = true;
    int number = -1;
    unsigned int interval = 1;

    void update();

    void notifyIterationIntervals(unsigned int interval);
    void notifyTimeIntervals(unsigned int interval);
    void notify();
    void notifyNumber();
    void notifyState();

  private:
    Messager &messager;
    typename Messager::Parser &parser;
    typename Messager::Sender &sender;

    const SignalType &signalValue;
    SignalType prevSignalValue = 0;

    const char axisChannel = '\0';
    const char signalChannel = '\0';

    unsigned int iteration = 0;
    elapsedMillis timer;

    void onReceivedMessage();
};

namespace States {
  enum class LinearActuatorMode : int8_t {
    directMotorDutyIdle = 0, directMotorDutyControl = 1, positionFeedbackControl = 2,
    stallTimeoutStopped = -1, convergenceTimeoutStopped = -2, timerTimeoutStopped = -3
  };
}

template <class LinearActuator, class Messager>
class LinearActuatorModule {
  public:
    LinearActuatorModule(
        Messager &messager,
        LinearPositionControl::Components::Motors &motors,
        char axisChannel,
        MotorPort motorPort, uint8_t sensorId,
        int minPosition, int maxPosition,
        int minDuty, int maxDuty,
        double pidKp, double pidKd, double pidKi, int pidSampleTime,
        int feedforward,
        int brakeLowerThreshold, int brakeUpperThreshold,
        bool swapMotorPolarity,
        int convergenceTimeout, int stallTimeout, int timerTimeout,
        float smootherSnapMultiplier, int smootherMax,
        bool smootherEnableSleep, float smootherActivityThreshold
    );

    using Position = typename LinearActuator::Position;
    using Smoother = LinearPositionControl::Smoother<Position, int>;
    using State = States::LinearActuatorMode;

    LinearActuator actuator;
    LinearPositionControl::StateVariable<State> state;
    Smoother smoother;

    // Parameters
    unsigned int convergenceTimeout;
    unsigned int stallTimeout;
    unsigned int timerTimeout = 0;

    void setup();
    void update();

    // Stopping conditions
    bool converged() const;
    bool stalled() const;
    bool timed() const;

    void reportPosition(char reportingChannel);

    void startPositionFeedbackControl(Position setpoint);
    void startDirectMotorDutyControl(int duty);
    void endControl(State nextState);

    // State notifiers
    void notifyState();
    void notifyPosition();
    void notifySmoothedPosition();
    void notifyMotor();
    void notifyFeedbackControllerSetpoint();

  private:
    Messager &messager;
    typename Messager::Parser &parser;
    typename Messager::Sender &sender;

    bool setupCompleted = false;

    const char axisChannel = '\0';

    Notifier<Messager, Position> positionNotifier;
    Notifier<Messager, int> smoothedPositionNotifier;
    Notifier<Messager, int> motorDutyNotifier;

    void onReceivedMessage(unsigned int channelParsedLength);
    void onPositionMessage(unsigned int channelParsedLength);
    void onSmoothedPositionMessage(unsigned int channelParsedLength);
    void onMotorMessage(unsigned int channelParsedLength);
    void onFeedbackControllerMessage(unsigned int channelParsedLength);
    void onFeedbackControllerLimitsMessage(unsigned int channelParsedLength);
    void onFeedbackControllerPIDMessage(unsigned int channelParsedLength);
};

}

#include "LinearActuatorModule.tpp"

#endif

