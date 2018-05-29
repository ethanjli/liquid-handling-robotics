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

// StringParser

template<uint8_t maxLength>
StringParser<maxLength>::StringParser(char endDelimiter) :
  endDelimiter(endDelimiter)
{}

template<uint8_t maxLength>
void StringParser<maxLength>::setup() {
  if (setupCompleted) return;

  memset(buffer, '\0', maxLength + 1);
  state.setup(State::parsing);

  setupCompleted = true;
}

template<uint8_t maxLength>
void StringParser<maxLength>::onChar(char current) {
  if (current == endDelimiter) {
    state.update(State::parsed);
    bufferPosition = 0;
    strlcpy(received, buffer, maxLength + 1);
    buffer[0] = '\0';
  } else {
    parse(current);
    state.update(State::parsing, true);
  }
}

template<uint8_t maxLength>
void StringParser<maxLength>::reset() {
  memset(buffer, '\0', maxLength + 1);
  length = 0;
  bufferPosition = 0;
  state.update(State::parsing);
}

template<uint8_t maxLength>
bool StringParser<maxLength>::matches(const char queryString[]) const {
  return strncmp(queryString, received, maxLength + 1) == 0;
}

template<uint8_t maxLength>
bool StringParser<maxLength>::justReceived() const {
  return state.justEntered(State::parsed);
}

template<uint8_t maxLength>
uint8_t StringParser<maxLength>::parsedLength() const {
  return length;
}

template<uint8_t maxLength>
void StringParser<maxLength>::parse(char current) {
  if (isAlphaNumeric(current)) {
    if (bufferPosition < maxLength) {
      buffer[bufferPosition] = current;
      ++bufferPosition;
      ++length;
    } else {
      Log.warning(F("Ignoring char '%c' beyond max string length!" CR), current);
    }
  } else if (!isControl(current)) {
    Log.warning(F("Ignoring unknown char '%c'!" CR), current);
  }
}

// MessageParser

template<class Transport>
MessageParser<Transport>::MessageParser(Transport &transport) :
  transport(transport), channelParser(kChannelEndDelimiter)
{}

template<class Transport>
void MessageParser<Transport>::setup() {
  if (setupCompleted) return;

  channelParser.setup();
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
        channelParser.reset();
        state.update(State::parsingChannel);
      }
      break;
    case State::parsingChannel:
      if (current == kChannelStartDelimiter) {
        channelParser.reset();
        Log.warning(F("Channel name interrupted by start delimiter, resetting!" CR));
      } else {
        channelParser.onChar(current);
        if (channelParser.justReceived()) state.update(State::awaitingPayload);
        else state.update(State::parsingChannel, true);
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
  return channelParser.matches(queryChannel);
}

template<class Transport>
bool MessageParser<Transport>::justReceived(const char queryChannel[]) const {
  return state.justEntered(State::parsedMessage) && channelParser.matches(queryChannel);
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
  return channelParser.parsedLength();
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
void MessageParser<Transport>::parsePayload(char current) {
  if (current == '-' && state.justEntered(State::parsingPayload)) {
    negative = true;
    ++payloadLength;
  } else if (isDigit(current)) {
    receivedNumber *= 10;
    receivedNumber += current - '0';
    ++payloadLength;
  } else if (!isControl(current)) {
    Log.warning(F("Payload on channel '%s' has unknown character '%c'. Ignoring it!" CR), channel, current);
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

