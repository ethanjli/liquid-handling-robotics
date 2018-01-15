#ifndef ASCIISerialIO_h
#define ASCIISerialIO_h

#include <StateVariable.h>

namespace LiquidHandlingRobotics {

void waitForSerialHandshake(char handshakeChar = '~', unsigned long waitDelay = 200);

void sendMessage(
    const String &channel, int payload,
    char channelStartDelimiter = '<', char channelEndDelimiter = '>',
    char payloadStartDelimiter = '[', char payloadEndDelimiter = ']'
);

class IntParser {
  public:
    IntParser(char startDelimiter = '[', char endDelimiter = ']');

    LinearPositionControl::StateVariable<int> result;
    bool justUpdated = false;

    void setup();
    void update();

  private:
    char startDelimiter;
    char endDelimiter;

    int receivedNumber;
    bool negative = false;

    LinearPositionControl::StateVariable<char> received;
};

}

#endif

