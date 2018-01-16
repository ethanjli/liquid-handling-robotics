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
    parsingPayload,
    parsedMessage
  };
}

void waitForSerialHandshake(char handshakeChar = '~', unsigned long waitDelay = 200);

void sendMessage(
    const String &channel, int payload,
    char channelStartDelimiter = '<', char channelEndDelimiter = '>',
    char payloadStartDelimiter = '[', char payloadEndDelimiter = ']'
);

const unsigned int kChannelMaxLength = 8;

class MessageParser {
  public:
    MessageParser(
        char channelStartDelimiter = '<', char channelEndDelimiter = '>',
        char payloadStartDelimiter = '[', char payloadEndDelimiter = ']'
    );

    using State = States::Parsing;

    LinearPositionControl::StateVariable<States::Parsing> state;

    // Channel
    char channel[kChannelMaxLength + 1];

    // Payload
    int payload = 0;

    void setup();
    void update();

    bool isChannel(const char queryChannel[]);
    bool justReceived(const char queryChannel[]);

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

    void onParsingChannel();
    void parseChannel(char current);
    void onAwaitingPayload();
    void onParsingPayload();
    void parsePayload(char current);
    void onParsedMessage();
};

}

#endif

