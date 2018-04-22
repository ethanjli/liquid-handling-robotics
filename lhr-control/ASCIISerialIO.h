#ifndef ASCIISerialIO_h
#define ASCIISerialIO_h

#include <ArduinoLog.h>

#include <StateVariable.h>

namespace LiquidHandlingRobotics {

const uint16_t kVersion[] PROGMEM = {
  0, // Patch
  1, // Minor
  0  // Major
};

void waitForSerialHandshake(char handshakeChar = '~', unsigned long waitDelay = 200);

// Message RX/TX

const char kChannelStartDelimiter = '<';
const char kChannelEndDelimiter = '>';
const char kPayloadStartDelimiter = '[';
const char kPayloadEndDelimiter = ']';

void sendMessage(const String &channel, int payload);
void sendChannelStart();
void sendChannelChar(char channelChar);
void sendChannelEnd();
void sendChannel(const String &channel);
void sendPayloadStart();
void sendPayloadEnd();
void sendPayload(int payload);

class MessageParser;

// General Protocol Functionalities

const char kResetChannel = 'r';
const char kVersionChannel = 'v';

void handleResetCommand(MessageParser &messageParser);
void hardReset();
void handleVersionCommand(MessageParser &messageParser);
void sendVersionMessage(char versionPosition);

// Message Parsing

namespace States {
  enum class Parsing : uint8_t {
    awaitingChannel,
    parsingChannel,
    awaitingPayload,
    parsingPayload,
    parsedMessage
  };
}

const unsigned int kChannelMaxLength = 8;

class MessageParser {
  public:
    using State = States::Parsing;

    LinearPositionControl::StateVariable<States::Parsing> state;

    // Channel
    char channel[kChannelMaxLength + 1];

    // Payload
    int payload = 0;

    void setup();
    void update();

    bool isChannel(const char queryChannel[]) const;
    bool justReceived(const char queryChannel[]) const;
    bool justReceived() const;
    unsigned int payloadParsedLength() const;

    void sendResponse(int payload, unsigned int channelLength = 0);

  private:
    char channelStartDelimiter;
    char channelEndDelimiter;
    char payloadStartDelimiter;
    char payloadEndDelimiter;

    // Channel
    int channelBufferPosition = 0;
    char channelBuffer[kChannelMaxLength + 1];
    char *channelBufferString = channelBuffer;

    // Payload
    int receivedNumber;
    bool negative = false;
    unsigned int payloadLength = 0;

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

