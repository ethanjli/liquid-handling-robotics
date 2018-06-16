#ifndef BoardProtocol_h
#define BoardProtocol_h

#include <LED.h>

#include "Messages.h"

namespace LiquidHandlingRobotics {

const char kIOChannel = 'i';
const char kIOAnalogChannel = 'a';
const char kIODigitalChannel = 'd';
const char kBuiltinLEDChannel = 'l';
const char kBuiltinLEDBlinkChannel = 'b';
const char kBuiltinLEDBlinkHighIntervalChannel = 'h';
const char kBuiltinLEDBlinkLowIntervalChannel = 'l';
const char kBuiltinLEDBlinkPeriodsChannel = 'p';
const char kBuiltinLEDBlinkNotifyChannel = 'n';

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

