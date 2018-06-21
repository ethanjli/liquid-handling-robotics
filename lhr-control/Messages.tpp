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
void MessageSender<Transport>::sendMessage(const char *channel, int payload) {
  sendChannel(channel);
  sendPayload(payload);
}

template<class Transport>
void MessageSender<Transport>::sendChannel(const char *channel) {
  sendChannelStart();
  transport.print(channel);
  /*
  char *curr = channel;
  while (curr != nullptr && *curr != '\0') {
    transport.write(*curr); // or sendChannelChar(*curr) for generalizability
    ++curr;
  }
  */
  sendChannelEnd();
}

template<class Transport>
void MessageSender<Transport>::sendChannelStart() {
  sendMessageStart();
  transport.write(kChannelStartDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendChannelChar(char channelChar) {
  if (isAlphaNumeric(channelChar)) transport.write(channelChar);
}

template<class Transport>
void MessageSender<Transport>::sendChannelEnd() {
  transport.write(kChannelEndDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendPayloadStart() {
  transport.write(kPayloadStartDelimiter);
}

template<class Transport>
void MessageSender<Transport>::sendPayloadEnd() {
  transport.write(kPayloadEndDelimiter);
  sendMessageEnd();
}

template<class Transport>
void MessageSender<Transport>::sendPayload(int payload) {
  sendPayloadStart();
  transport.print(payload);
  sendPayloadEnd();
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
  state.setup(State::ready);

  setupCompleted = true;
}

template<uint8_t maxLength>
bool StringParser<maxLength>::onChar(char current) {
  if (current == endDelimiter) {
    state.update(State::parsed);
    bufferPosition = 0;
    strlcpy(received, buffer, maxLength + 1);
    buffer[0] = '\0';
    return false;
  } else {
    if (state.at(State::ready)) state.update(State::parsing);
    parse(current);
    state.update(State::parsing, true);
    return true;
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
    Log.warning(F("Ignoring unknown char '%c' in string!" CR), current);
  }
}

// IntegerParser

template<class Integer>
IntegerParser<Integer>::IntegerParser(char endDelimiter) :
  endDelimiter(endDelimiter)
{}

template<class Integer>
void IntegerParser<Integer>::setup() {
  if (setupCompleted) return;

  state.setup(State::ready);

  setupCompleted = true;
}

template<class Integer>
bool IntegerParser<Integer>::onChar(char current) {
  if (current == endDelimiter) {
    state.update(State::parsed);
    received = intermediate;
    if (negative) received *= -1;
    intermediate = 0;
    negative = false;
    return false;
  } else {
    if (state.at(State::ready)) state.update(State::parsing);
    parse(current);
    state.update(State::parsing, true);
    return true;
  }
}

template<class Integer>
void IntegerParser<Integer>::reset() {
  intermediate = 0;
  negative = false;
  length = 0;
  state.update(State::parsing);
}

template<class Integer>
bool IntegerParser<Integer>::justReceived() const {
  return state.justEntered(State::parsed);
}

template<class Integer>
void IntegerParser<Integer>::parse(char current) {
  if ((current == '-') && state.justEntered(State::parsing)) {
    negative = true;
    ++length;
  } else if (isDigit(current)) {
    intermediate *= 10;
    intermediate += current - '0';
    if (intermediate < 0) Log.warning(F("Integer overflowed to '%d'!" CR), intermediate);
    ++length;
  } else if (!isControl(current)) {
    Log.warning(F("Ignoring unknown char '%c' in integer!" CR), current);
  }
}

// MessageParser

template<class Transport>
MessageParser<Transport>::MessageParser(Transport &transport) :
  transport(transport),
  channelParser(kChannelEndDelimiter),
  payloadParser(kPayloadEndDelimiter),
  channelParsedLength(channelParser.parsedLength),
  payloadParsedLength(payloadParser.parsedLength)
{}

template<class Transport>
void MessageParser<Transport>::setup() {
  if (setupCompleted) return;

  channelParser.setup();
  payloadParser.setup();
  state.setup(State::awaitingChannel);

  setupCompleted = true;
}

template<class Transport>
void MessageParser<Transport>::update() {
  wdt_reset();
  if (state.at(State::parsedMessage)) state.update(State::awaitingChannel);
  receive();
  wdt_reset();
}

template<class Transport>
void MessageParser<Transport>::receive() {
  while (transport.available() > 0 && onChar(transport.read())) wdt_reset();
}

template<class Transport>
bool MessageParser<Transport>::onChar(char current) {
  switch (state.current) {
    case State::awaitingChannel:
      if (current == kChannelStartDelimiter) {
        channelParser.reset();
        state.update(State::parsingChannel);
      }
      return true;
    case State::parsingChannel:
      if (current == kChannelStartDelimiter) {
        channelParser.reset();
        Log.warning(F("Channel name interrupted by start delimiter, resetting!" CR));
      } else {
        channelParser.onChar(current);
        if (channelParser.justReceived()) state.update(State::awaitingPayload);
        else state.update(State::parsingChannel, true);
      }
      return true;
    case State::awaitingPayload:
      if (current == kPayloadStartDelimiter) {
        payloadParser.reset();
        state.update(State::parsingPayload);
      }
      return true;
    case State::parsingPayload:
      if (current == kPayloadStartDelimiter) {
        payloadParser.reset();
        Log.warning(F("Payload interrupted by start delimiter, resetting!" CR));
      } else {
        payloadParser.onChar(current);
        if (payloadParser.justReceived()) {
          state.update(State::parsedMessage);
          return false; // signal the caller not to parse more messages
        } else {
          state.update(State::parsingPayload, true);
        }
      }
      return true;
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
bool MessageParser<Transport>::receivedPayload() const {
  return payloadParser.parsedLength > 0;
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

