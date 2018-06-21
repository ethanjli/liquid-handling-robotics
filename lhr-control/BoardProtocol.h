#ifndef BoardProtocol_h
#define BoardProtocol_h

#include <Components/LED.h>

#include "Messages.h"

namespace LiquidHandlingRobotics {

namespace Channels {
  namespace BoardProtocol {
    const char kIO = 'i';
    namespace IO {
      const char kAnalog = 'a';
      const char kDigital = 'd';
    }
    const char kBuiltinLED = 'l';
    namespace BuiltinLED {
      const char kBlink = 'b';
      namespace Blink {
        const char kHighInterval = 'h';
        const char kLowInterval = 'l';
        const char kPeriods = 'p';
        const char kNotify = 'n';
      }
    }
  }
}

const uint8_t kAnalogPinOffset = 14;
const uint8_t kAnalogReadMinPin = 0;
const uint8_t kAnalogReadMaxPin = 3;
const uint8_t kDigitalReadMinPin = 2;
const uint8_t kDigitalReadMaxPin = 13;

template<class Messager>
class BoardProtocol {
  public:
    using LED = LinearPositionControl::Components::SimpleLED;

    BoardProtocol(Messager &messager);

    LED led;

    void setup();
    void update();

    void onConnect();

  private:
    Messager &messager;
    typename Messager::Parser &parser;
    typename Messager::Sender &sender;
    bool setupCompleted = false;
    bool reportBlinkUpdates = false;
    LED::State previousLEDState = LED::State::off;
    bool reportedBlinkEnd = false;

    void handleIOCommand();
    void handleBuiltinLEDCommand();
    void handleBuiltinLEDBlinkCommand();

    void sendBuiltinLEDState();
    void sendBuiltinLEDBlinkState();
    void sendBuiltinLEDBlinkPeriods();
};

}

#include "BoardProtocol.tpp"

#endif

