#ifndef Messages_h
#define Messages_h

#include <ArduinoLog.h>

#include <StateVariable.h>

namespace LiquidHandlingRobotics {

const char kChannelStartDelimiter = '<';
const char kChannelEndDelimiter = '>';
const char kPayloadStartDelimiter = '(';
const char kPayloadEndDelimiter = ')';
const unsigned int kChannelMaxLength = 8;

// Message Sending

template <class Transport>
class MessageSender {
  public:
    MessageSender(); // needs to be implemented by specialization
    MessageSender(Transport &transport);

    void setup(); // needs to be implemented by specialization

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

  private:
    Transport &transport;
    bool setupCompleted = false;
};

// Message Parsing

namespace States {
  namespace Parsing {
    enum class Field : uint8_t {
      parsing,
      parsed
    };

    enum class Message : uint8_t {
      awaitingChannel,
      parsingChannel,
      awaitingPayload,
      parsingPayload,
      parsedMessage
    };
  }
}

template <uint8_t maxLength>
class StringParser {
  public:
    StringParser(char endDelimiter = '\0');

    using State = States::Parsing::Field;

    LinearPositionControl::StateVariable<State> state;

    char endDelimiter;
    char received[maxLength + 1];

    void setup();

    bool matches(const char queryString[]) const;
    bool justReceived() const;
    uint8_t parsedLength() const;

    void onChar(char current);
    void reset();

  private:
    bool setupCompleted = false;

    // Buffer
    uint8_t bufferPosition = 0;
    char buffer[maxLength + 1];
    uint8_t length = 0;

    void parse(char current);
};

template <class Transport>
class MessageParser {
  public:
    MessageParser(); // needs to be implemented by specialization
    MessageParser(Transport &transport);

    using State = States::Parsing::Message;

    LinearPositionControl::StateVariable<State> state;

    // Channel
    char (&channel)[kChannelMaxLength + 1] = channelParser.received;

    // Payload
    int payload = 0;

    void setup();
    void update();

    void receive();

    bool isChannel(const char queryChannel[]) const;
    bool justReceived(const char queryChannel[]) const;
    bool justReceived() const;
    unsigned int payloadParsedLength() const;
    unsigned int channelParsedLength() const;

    void onChar(char current);

  private:
    Transport &transport;
    StringParser<kChannelMaxLength> channelParser;
    bool setupCompleted = false;

    // Payload
    int receivedNumber;
    bool negative = false;
    unsigned int payloadLength = 0;

    void onAwaitingPayload();
    void onParsingPayload();
    void parsePayload(char current);
    void onParsedMessage();
};

// Messaging
template <class Transport>
class Messager {
  public:
    Messager(); // needs to be implemented by specialization
    Messager(Transport &transport);

    MessageParser<Transport> parser;
    MessageSender<Transport> sender;

    void setup(); // needs to be implemented by specialization
    void update();

    void establishConnection(); // needs to be implemented by specialization

    void sendResponse(int payload);

  private:
    Transport &transport;
    bool setupCompleted = false;
};

}

#include "Messages.tpp"

#endif

