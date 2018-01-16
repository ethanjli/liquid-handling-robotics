#ifndef ASCIISerialIO_h
#define ASCIISerialIO_h

#include <ArduinoLog.h>

#include <StateVariable.h>

namespace LiquidHandlingRobotics {

namespace States {
  enum class Parsing : uint8_t {
    awaitingChannel,
    parsingChannel,
    awaitingPayload,
    parsingPayload
  };
}

void waitForSerialHandshake(char handshakeChar = '~', unsigned long waitDelay = 200);

void sendMessage(
    const String &channel, int payload,
    char channelStartDelimiter = '<', char channelEndDelimiter = '>',
    char payloadStartDelimiter = '[', char payloadEndDelimiter = ']'
);

const unsigned int kChannelMaxLength = 8;

class ChannelParser {
  public:
    ChannelParser(char startDelimiter = '<', char endDelimiter = '>');

    char channel[kChannelMaxLength + 1];
    bool justUpdated = false;

    void setup();
    void update();

  private:
    char startDelimiter;
    char endDelimiter;

    int bufferPosition = 0;
    char channelBuffer[kChannelMaxLength + 1];

    LinearPositionControl::StateVariable<char> received;
};

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

class MessageParser {
  public:
    MessageParser(
        char channelStartDelimiter = '<', char channelEndDelimiter = '>',
        char payloadStartDelimiter = '[', char payloadEndDelimiter = ']'
    );

    LinearPositionControl::StateVariable<States::Parsing> state;

    // Channel
    char channel[kChannelMaxLength + 1];

    // Payload
    int result;

    void setup();
    void update();

  private:
    char channelStartDelimiter;
    char channelEndDelimiter;
    char payloadStartDelimiter;
    char payloadEndDelimiter;

    // Channel
    int channelBufferPosition = 0;
    char channelBuffer[kChannelMaxLength + 1];

    // Payload
    int receivedNumber;
    bool negative = false;

    LinearPositionControl::StateVariable<char> received;
};

}

#endif

