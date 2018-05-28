#include "Messages.h"

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

// Message TX

void sendMessage(const String &channel, int payload) {
  sendChannel(channel);
  sendPayload(payload);
}
void sendMessage(const char *channel, int payload) {
  sendChannel(channel);
  sendPayload(payload);
}
void sendChannel(const String &channel) {
  Serial.print(kChannelStartDelimiter);
  Serial.print(channel);
  Serial.print(kChannelEndDelimiter);
}
void sendChannel(const char *channel) {
  Serial.print(kChannelStartDelimiter);
  Serial.print(channel);
  //char *curr = channel;
  //while (curr != nullptr && *curr != '\0') {
  //  if (*curr != 0x7f) Serial.print(*curr);
  //  ++curr;
  //}
  Serial.print(kChannelEndDelimiter);
}
void sendChannelStart() {
  Serial.print(kChannelStartDelimiter);
}
void sendChannelChar(char channelChar) {
  Serial.print(channelChar);
  //if (channelChar != 0x7f) Serial.print(channelChar);
}
void sendChannelEnd() {
  Serial.print(kChannelEndDelimiter);
}
void sendPayloadStart() {
  Serial.print(kPayloadStartDelimiter);
}
void sendPayloadEnd() {
  Serial.print(kPayloadEndDelimiter);
}
void sendPayload(int payload) {
  Serial.print(kPayloadStartDelimiter);
  Serial.print(payload);
  Serial.print(kPayloadEndDelimiter);
  Serial.println();
}

// MessageParser

void MessageParser::setup() {
  channelBuffer[0] = '\0';
  state.setup(State::awaitingChannel);
}

void MessageParser::update() {
  if (state.current() == State::parsedMessage) state.update(State::awaitingChannel);
  while (Serial.available() > 0) onChar(Serial.read());
}

void MessageParser::onChar(char current) {
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

bool MessageParser::isChannel(const char queryChannel[]) const {
  return strncmp(queryChannel, channel, kChannelMaxLength + 1) == 0;
}

bool MessageParser::justReceived(const char queryChannel[]) const {
  return state.justEntered(State::parsedMessage) && isChannel(queryChannel);
}

bool MessageParser::justReceived() const {
  return state.justEntered(State::parsedMessage);
}

unsigned int MessageParser::payloadParsedLength() const {
  return payloadLength;
}

unsigned int MessageParser::channelParsedLength() const {
  return channelLength;
}

void MessageParser::sendResponse(int payload) {
  sendMessage(channel, payload);
}

void MessageParser::onParsingChannel() {
  memset(channelBuffer, '\0', kChannelMaxLength + 1);
  channelLength = 0;
  channelBufferPosition = 0;
}

void MessageParser::onAwaitingPayload() {
  channelBuffer[channelBufferPosition] = '\0';
  channelBufferPosition = -1;
  strlcpy(channel, channelBuffer, kChannelMaxLength + 1);
}

void MessageParser::onParsingPayload() {
  receivedNumber = 0;
  payloadLength = 0;
  negative = false;
}

void MessageParser::onParsedMessage() {
  if (negative) payload = -1 * receivedNumber;
  else payload = receivedNumber;
}

void MessageParser::parseChannel(char current) {
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

void MessageParser::parsePayload(char current) {
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

}

