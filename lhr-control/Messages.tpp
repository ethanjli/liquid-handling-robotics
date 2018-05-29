#ifndef Messages_tpp
#define Messages_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

// MessageSender

template<class Transport>
MessageSender<Transport>::MessageSender(Transport &transport) :
  transport(transport)
{}

template<class Transport>
void MessageSender<Transport>::sendMessage(const String &channel, int payload) {
  sendChannel(channel);
  sendPayload(payload);
}

template<class Transport>
void MessageSender<Transport>::sendMessage(const char *channel, int payload) {
  sendChannel(channel);
  sendPayload(payload);
}

template<class Transport>
void MessageSender<Transport>::sendChannel(const String &channel) {
  transport.print(kChannelStartDelimiter);
  transport.print(channel);
  transport.print(kChannelEndDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendChannel(const char *channel) {
  transport.print(kChannelStartDelimiter);
  transport.print(channel);
  //char *curr = channel;
  //while (curr != nullptr && *curr != '\0') {
  //  transport.print(*curr);
  //  ++curr;
  //}
  transport.print(kChannelEndDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendChannelStart() {
  transport.print(kChannelStartDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendChannelChar(char channelChar) {
  transport.print(channelChar);
}

template<class Transport>
void MessageSender<Transport>::sendChannelEnd() {
  transport.print(kChannelEndDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendPayloadStart() {
  transport.print(kPayloadStartDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendPayloadEnd() {
  transport.print(kPayloadEndDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendPayload(int payload) {
  transport.print(kPayloadStartDelimiter);
  transport.print(payload);
  transport.print(kPayloadEndDelimiter);
  transport.println();
}

// MessageParser

template<class Transport>
MessageParser<Transport>::MessageParser(Transport &transport) :
  transport(transport)
{}

template<class Transport>
void MessageParser<Transport>::setup() {
  if (setupCompleted) return;

  channelBuffer[0] = '\0';
  state.setup(State::awaitingChannel);

  setupCompleted = true;
}

template<class Transport>
void MessageParser<Transport>::update() {
  wdt_reset();
  if (state.current() == State::parsedMessage) state.update(State::awaitingChannel);
  receive();
  wdt_reset();
}

template<class Transport>
void MessageParser<Transport>::receive() {
  while (transport.available() > 0) {
    wdt_reset();
    onChar(transport.read());
  }
}

template<class Transport>
void MessageParser<Transport>::onChar(char current) {
  switch (state.current()) {
    case State::awaitingChannel:
      if (current == kChannelStartDelimiter) {
        onParsingChannel();
        state.update(State::parsingChannel);
      }
      break;
    case State::parsingChannel:
      if (current == kChannelEndDelimiter) {
        state.update(State::awaitingPayload);
        onAwaitingPayload();
      } else if (current == kChannelStartDelimiter) {
        onParsingChannel();
        Log.warning(F("Channel name starting with '%s' was interrupted in the middle by a '%c' character. Resetting channel name!" CR), channelBufferString, current);
      } else {
        parseChannel(current);
        state.update(State::parsingChannel, true);
      }
      break;
    case State::awaitingPayload:
      if (current == kPayloadStartDelimiter) {
        onParsingPayload();
        state.update(State::parsingPayload);
      }
      break;
    case State::parsingPayload:
      if (current == kPayloadEndDelimiter) {
        onParsedMessage();
        state.update(State::parsedMessage);
        return; // don't parse more messages until the next update() call
      } else {
        parsePayload(current);
        state.update(State::parsingPayload, true);
      }
  }
}

template<class Transport>
bool MessageParser<Transport>::isChannel(const char queryChannel[]) const {
  return strncmp(queryChannel, channel, kChannelMaxLength + 1) == 0;
}

template<class Transport>
bool MessageParser<Transport>::justReceived(const char queryChannel[]) const {
  return state.justEntered(State::parsedMessage) && isChannel(queryChannel);
}

template<class Transport>
bool MessageParser<Transport>::justReceived() const {
  return state.justEntered(State::parsedMessage);
}

template<class Transport>
unsigned int MessageParser<Transport>::payloadParsedLength() const {
  return payloadLength;
}

template<class Transport>
unsigned int MessageParser<Transport>::channelParsedLength() const {
  return channelLength;
}

template<class Transport>
void MessageParser<Transport>::onParsingChannel() {
  memset(channelBuffer, '\0', kChannelMaxLength + 1);
  channelLength = 0;
  channelBufferPosition = 0;
}

template<class Transport>
void MessageParser<Transport>::onAwaitingPayload() {
  channelBuffer[channelBufferPosition] = '\0';
  channelBufferPosition = -1;
  strlcpy(channel, channelBuffer, kChannelMaxLength + 1);
}

template<class Transport>
void MessageParser<Transport>::onParsingPayload() {
  receivedNumber = 0;
  payloadLength = 0;
  negative = false;
}

template<class Transport>
void MessageParser<Transport>::onParsedMessage() {
  if (negative) payload = -1 * receivedNumber;
  else payload = receivedNumber;
}

template<class Transport>
void MessageParser<Transport>::parseChannel(char current) {
  if (channelBufferPosition >= 0) {
    if (isAlphaNumeric(current)) {
      if (channelBufferPosition < kChannelMaxLength) {
        channelBuffer[channelBufferPosition] = current;
        ++channelBufferPosition;
        ++channelLength;
      } else {
        Log.error(F("Channel name starting with '%s' is too long. Ignoring extra character '%c'!" CR), channelBufferString, current);
      }
    } else if (!isControl(current)) {
      Log.warning(F("Channel name starting with '%s' has unknown character '%c'. Ignoring it!" CR), channelBufferString, current);
    }
  }
}

template<class Transport>
void MessageParser<Transport>::parsePayload(char current) {
  if (current == '-' && state.justEntered(State::parsingPayload)) {
    negative = true;
    ++payloadLength;
  } else if (isDigit(current)) {
    receivedNumber *= 10;
    receivedNumber += current - '0';
    ++payloadLength;
  } else if (!isControl(current)) {
    Log.warning(F("Payload on channel '%s' has unknown character '%c'. Ignoring it!" CR), channelBufferString, current);
  }
}

// Messager

template<class Transport>
Messager<Transport>::Messager(Transport &transport) :
  parser(transport), sender(transport), transport(transport)
{}

template<class Transport>
void Messager<Transport>::update() {
  parser.update();
}

template<class Transport>
void Messager<Transport>::sendResponse(int payload) {
  sender.sendMessage(parser.channel, payload);
}

}

#endif

