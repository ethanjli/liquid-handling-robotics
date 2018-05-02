#ifndef ASCIISerialIO_h
#define ASCIISerialIO_h

#include <ArduinoLog.h>

#include <StateVariable.h>

namespace LiquidHandlingRobotics {

const uint16_t kVersion[] PROGMEM = {
  0, // Major
  1, // Minor
  0  // Patch
};

void waitForSerialHandshake(char handshakeChar = '~', unsigned long waitDelay = 500);

// Message RX/TX

const char kChannelStartDelimiter = '<';
const char kChannelEndDelimiter = '>';
const char kPayloadStartDelimiter = '(';
const char kPayloadEndDelimiter = ')';

void sendMessage(const String &channel, int payload);
void sendMessage(const char *channel, int payload);
void sendChannelStart();
void sendChannelChar(char channelChar);
void sendChannelEnd();
void sendChannel(const String &channel);
void sendChannel(const char *channel);
void sendPayloadStart();
void sendPayloadEnd();
void sendPayload(int payload);

class MessageParser;

// General Protocol Functionalities

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

void handleResetCommand(MessageParser &messageParser);
void hardReset();
void handleVersionCommand(MessageParser &messageParser);
void sendVersionMessage(char versionPosition);
void sendAllVersionMessages();
void handleEchoCommand(MessageParser &messageParser);
void handleIOCommand(MessageParser &messageParser);

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
    unsigned int channelParsedLength() const;

    void sendResponse(int payload);

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
    unsigned int channelLength = 0;

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

