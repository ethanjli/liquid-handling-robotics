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
using MessagePayload = int;

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
      ready,
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

    bool onChar(char current);
    void reset();

    bool matches(const char queryString[]) const;
    bool justReceived() const;
    uint8_t parsedLength() const;

  private:
    bool setupCompleted = false;

    uint8_t bufferPosition = 0;
    char buffer[maxLength + 1];
    uint8_t length = 0;

    void parse(char current);
};

template <class Integer = int>
class IntegerParser {
  public:
    IntegerParser(char endDelimiter = '\0');

    using State = States::Parsing::Field;

    LinearPositionControl::StateVariable<State> state;

    char endDelimiter;
    Integer received = 0;

    void setup();

    bool onChar(char current);
    void reset();

    bool justReceived() const;
    uint8_t parsedLength() const;

  private:
    bool setupCompleted = false;

    Integer intermediate;
    bool negative = false;
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

    char (&channel)[kChannelMaxLength + 1] = channelParser.received;
    MessagePayload &payload = payloadParser.received;

    void setup();
    void update();

    void receive();
    bool onChar(char current);

    bool isChannel(const char queryChannel[]) const;
    bool justReceived(const char queryChannel[]) const;
    bool justReceived() const;
    unsigned int payloadParsedLength() const;
    unsigned int channelParsedLength() const;

  private:
    Transport &transport;
    StringParser<kChannelMaxLength> channelParser;
    IntegerParser<MessagePayload> payloadParser;
    bool setupCompleted = false;
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

