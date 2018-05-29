#ifndef CoreProtocol_h
#define CoreProtocol_h

#include "Messages.h"

namespace LiquidHandlingRobotics {

const uint16_t kVersion[] PROGMEM = {
  0, // Major, position 0
  1, // Minor, position 1
  0  // Patch, position 2
};

enum class WatchdogTimeout : uint8_t {
  to15ms = WDTO_15MS,
  to30ms = WDTO_30MS,
  to60ms = WDTO_60MS,
  to120ms = WDTO_120MS,
  to250ms = WDTO_250MS,
  to500ms = WDTO_500MS,
  to1s = WDTO_1S,
  to2s = WDTO_2S,
  to4s = WDTO_4S,
  to8s = WDTO_8S
};

void hardReset();

const char kResetChannel = 'r';
const char kVersionChannel = 'v';
const char kEchoChannel = 'e';
const char kIOChannel = 'i';
const char kIOReadChannel = 'r';
const char kIOReadAnalogChannel = 'a';
const char kIOReadDigitalChannel = 'd';

const uint8_t kAnalogPinOffset = 14;
const uint8_t kAnalogReadMinPin = 0;
const uint8_t kAnalogReadMaxPin = 5;
const uint8_t kDigitalReadMinPin = 2;
const uint8_t kDigitalReadMaxPin = 13;

template<class Messager>
class CoreProtocol {
  public:
    CoreProtocol(Messager &messager);

    void setup();
    void update();

    void onConnect(WatchdogTimeout timeout = WatchdogTimeout::to2s);

    void sendVersionMessage(char versionPosition);
    void sendAllVersionMessages();

  private:
    Messager &messager;
    bool setupCompleted = false;

    void handleResetCommand();
    void handleVersionCommand();
    void handleEchoCommand();
    void handleIOCommand();
};

}

#include "CoreProtocol.tpp"

#endif

