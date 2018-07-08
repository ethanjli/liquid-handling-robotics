#ifndef LHR_Messaging_Messages_h
#define LHR_Messaging_Messages_h

#include <ArduinoLog.h>

#include <StateVariable.h>

namespace LiquidHandlingRobotics { namespace Messaging {

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

    void sendMessage(const char *channel, int payload);
    void sendMessageStart(); // needs to be implemented by specialization
    void sendChannel(const char *channel);
    void sendChannelStart();
    void sendChannelChar(char channelChar);
    void sendChannelEnd();
    void sendPayload(int payload);
    void sendPayloadStart();
    void sendPayloadEnd();
    void sendMessageEnd(); // needs to be implemented by specialization

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
    StringParser(bool (*charValidityPredicate)(int), char endDelimiter = '\0');

    using State = States::Parsing::Field;

    LinearPositionControl::StateVariable<State> state;

    char endDelimiter;
    char received[maxLength + 1];

    void setup();

    const bool (*isValidChar)(int);
    bool onChar(char current);
    void reset();

    bool matches(const char queryString[]) const;
    bool justReceived() const;
    const uint8_t &parsedLength = length;

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
    const uint8_t &parsedLength = length;

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
    bool receivedPayload() const;

  private:
    Transport &transport;
    StringParser<kChannelMaxLength> channelParser;
    IntegerParser<MessagePayload> payloadParser;
    bool setupCompleted = false;

  public:
    const uint8_t &channelParsedLength;
    const uint8_t &payloadParsedLength;
};

// Messaging
template <class Transport>
class Messager {
  public:
    using Parser = MessageParser<Transport>;
    using Sender = MessageSender<Transport>;

    Messager(); // needs to be implemented by specialization
    Messager(Transport &transport);

    Parser parser;
    Sender sender;

    void setup(); // needs to be implemented by specialization
    void update();

    void establishConnection(); // needs to be implemented by specialization

    void sendResponse(int payload);

  private:
    Transport &transport;
    bool setupCompleted = false;
};

} }

#include "Messages.tpp"

#endif

