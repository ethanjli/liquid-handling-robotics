#include "ASCIISerialIO.h"

namespace LiquidHandlingRobotics {

void waitForSerialHandshake(char handshakeChar, unsigned long waitDelay) {
  while (!Serial) {;}
  while (Serial.available() < 1) {
    Serial.print(handshakeChar);
    delay(waitDelay);
  }
  while (Serial.available() > 0) {
    if (Serial.read() == '\n') break;
  }
  delay(waitDelay);
}

void sendMessage(
    const String &channel, int payload,
    char channelStartDelimiter, char channelEndDelimiter,
    char payloadStartDelimiter, char payloadEndDelimiter
) {
  Serial.print(channelStartDelimiter);
  Serial.print(channel);
  Serial.print(channelEndDelimiter);
  Serial.print(payloadStartDelimiter);
  Serial.print(payload);
  Serial.print(payloadEndDelimiter);
  Serial.println();
}

// MessageParser

MessageParser::MessageParser(
    char channelStartDelimiter, char channelEndDelimiter,
    char payloadStartDelimiter, char payloadEndDelimiter
) :
  channelStartDelimiter(channelStartDelimiter),
  channelEndDelimiter(channelEndDelimiter),
  payloadStartDelimiter(payloadStartDelimiter),
  payloadEndDelimiter(payloadEndDelimiter)
{
}

void MessageParser::setup() {
  channelBuffer[0] = '\0';
  state.setup(State::awaitingChannel);
}

void MessageParser::update() {
  if (state.current() == State::parsedMessage) state.update(State::awaitingChannel);
  while (Serial.available() > 0) {
    char current = Serial.read();
    switch (state.current()) {
      case State::awaitingChannel:
        if (current == channelStartDelimiter) {
          onParsingChannel();
          state.update(State::parsingChannel);
        }
        break;
      case State::parsingChannel:
        if (current == channelEndDelimiter) {
          state.update(State::awaitingPayload);
          onAwaitingPayload();
        } else {
          parseChannel(current);
          state.update(State::parsingChannel, true);
        }
        break;
      case State::awaitingPayload:
        if (current == payloadStartDelimiter) {
          onParsingPayload();
          state.update(State::parsingPayload);
        }
        break;
      case State::parsingPayload:
        if (current == payloadEndDelimiter) {
          onParsedMessage();
          state.update(State::parsedMessage);
          return; // don't parse more messages until the next update() call
        } else {
          parsePayload(current);
          state.update(State::parsingPayload, true);
        }
    }
  }
}

bool MessageParser::isChannel(const char queryChannel[]) {
  return strncmp(queryChannel, channel, kChannelMaxLength + 1) == 0;
}

bool MessageParser::justReceived(const char queryChannel[]) {
  return state.justEntered(State::parsedMessage) && isChannel(queryChannel);
}

void MessageParser::onParsingChannel() {
  channelBufferPosition = 0;
}

void MessageParser::onAwaitingPayload() {
  channelBuffer[channelBufferPosition] = '\0';
  channelBufferPosition = -1;
  strlcpy(channel, channelBuffer, kChannelMaxLength + 1);
}

void MessageParser::onParsingPayload() {
  receivedNumber = 0;
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
      } else {
        Log.error(F("Channel name overflowed, ignoring extra character %c!" CR), current);
      }
    } else if (!isControl(current)) {
      Log.warning(F("Channel name has illegal character %c, ignoring it!" CR), current);
    }
  }
}

void MessageParser::parsePayload(char current) {
  if (current == '-' && state.justEntered(State::parsingPayload)) {
    negative = true;
  } else if (isDigit(current)) {
    receivedNumber *= 10;
    receivedNumber += current - '0';
  } else if (!isControl(current)) {
    Log.warning(F("Payload has illegal character %c, ignoring it!" CR), current);
  }
}

}

