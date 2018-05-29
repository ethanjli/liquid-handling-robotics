#ifndef Messages_h
#define Messages_h

#include <ArduinoLog.h>

#include <StateVariable.h>

namespace LiquidHandlingRobotics {

const char kChannelStartDelimiter = '<';
const char kChannelEndDelimiter = '>';
const char kPayloadStartDelimiter = '(';
const char kPayloadEndDelimiter = ')';

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
  enum class Parsing : uint8_t {
    awaitingChannel,
    parsingChannel,
    awaitingPayload,
    parsingPayload,
    parsedMessage
  };
}

const unsigned int kChannelMaxLength = 8;

template <class Transport>
class MessageParser {
  public:
    MessageParser(); // needs to be implemented by specialization
    MessageParser(Transport &transport);

    using State = States::Parsing;

    LinearPositionControl::StateVariable<States::Parsing> state;

    // Channel
    char channel[kChannelMaxLength + 1];

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
    bool setupCompleted = false;

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

