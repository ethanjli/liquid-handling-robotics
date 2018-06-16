#ifndef CoreProtocol_h
#define CoreProtocol_h

#include "Messages.h"

namespace LiquidHandlingRobotics {

const uint16_t kVersion[] PROGMEM = {
  1, // Major, position 0
  0, // Minor, position 1
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
    typename Messager::Parser &parser;
    typename Messager::Sender &sender;
    bool setupCompleted = false;
    int echoValue = 0;

    void handleResetCommand();
    void handleVersionCommand();
    void handleEchoCommand();
};

}

#include "CoreProtocol.tpp"

#endif

