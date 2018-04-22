#include "ASCIISerialIO.h"

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

void hardReset() {
  wdt_enable(WDTO_15MS);
  while (true); // Hang to force the AVR watchdog timer to reset the Arduino
}

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
  sendChannel(channel, channelStartDelimiter, channelEndDelimiter);
  sendPayload(payload, payloadStartDelimiter, payloadEndDelimiter);
}
void sendChannel(
    const String &channel, char channelStartDelimiter, char channelEndDelimiter
) {
  Serial.print(channelStartDelimiter);
  Serial.print(channel);
  Serial.print(channelEndDelimiter);
}
void sendChannelStart(char channelStartDelimiter) {
  Serial.print(channelStartDelimiter);
}
void sendChannelChar(char channelChar) {
  Serial.print(channelChar);
}
void sendChannelEnd(char channelEndDelimiter) {
  Serial.print(channelEndDelimiter);
}
void sendPayload(
    int payload, char payloadStartDelimiter, char payloadEndDelimiter
) {
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
        } else if (current == channelStartDelimiter) {
          onParsingChannel();
          Log.warning(F("Channel name starting with '%s' was interrupted in the middle by a '%c' character. Resetting channel name!" CR), channelBufferString, current);
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

bool MessageParser::justReceived() {
  return state.justEntered(State::parsedMessage);
}

void MessageParser::onParsingChannel() {
  memset(channelBuffer, '\0', kChannelMaxLength + 1);
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
  } else if (isDigit(current)) {
    receivedNumber *= 10;
    receivedNumber += current - '0';
  } else if (!isControl(current)) {
    Log.warning(F("Payload on channel '%s' has unknown character '%c'. Ignoring it!" CR), channelBufferString, current);
  }
}

}

