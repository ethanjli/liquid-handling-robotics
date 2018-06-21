#ifndef FirmataIO_tpp
#define FirmataIO_tpp

#include <avr/wdt.h>

#include <elapsedMillis.h>

#include <AnalogWrite.h> // needed for successful compilation

namespace LiquidHandlingRobotics {

namespace FirmataIO {

void resetPinModes() {
  for (uint8_t pin = 0; pin < TOTAL_PINS; ++pin) {
    if (IS_PIN_ANALOG(pin)) {
      Firmata.setPinMode(pin, ANALOG);
    } else if (IS_PIN_DIGITAL(pin)) {
      Firmata.setPinMode(pin, OUTPUT);
    }
  }
}

}

// FirmataMessageListener

bool FirmataMessageListener::handlePinMode(uint8_t pin, int mode) {
  return false;
}

void FirmataMessageListener::handleCapability(uint8_t pin) {
  return false;
}

bool FirmataMessageListener::handleSysex(uint8_t command, uint8_t argc, uint8_t *argv) {
  if (command != FirmataIO::kTranslatorCommand) {
    bufferLength = 0;
    buffer = nullptr;
    bufferPosition = 0;
    receivedEmptyMessage = false;
    return false;
  }

  bufferLength = argc;
  buffer = argv;
  bufferPosition = 0;
  receivedEmptyMessage = bufferLength == 0;
  return true;
}

void FirmataMessageListener::reset() {
  bufferLength = 0;
  buffer = nullptr;
  bufferPosition = 0;
}

uint8_t FirmataMessageListener::available() const {
  if (buffer == nullptr) return 0;
  return bufferLength - bufferPosition;
}

char FirmataMessageListener::read() {
  if (buffer == nullptr) return -1;

  char current = peek();
  ++bufferPosition;
  return current;
}

char FirmataMessageListener::peek() const {
  if (buffer == nullptr) return -1;

  return static_cast<char>(*(buffer + bufferPosition));
}

// FirmataTransport

void FirmataTransport::setup() {
  if (setupCompleted) return;

  Firmata.setFirmwareVersion(
      FIRMATA_FIRMWARE_MAJOR_VERSION, FIRMATA_FIRMWARE_MINOR_VERSION
  );

  state.setup(State::connecting);

  firmataExt.addFeature(digitalInput);
  firmataExt.addFeature(digitalOutput);
  firmataExt.addFeature(analogInput);
  firmataExt.addFeature(analogOutput);
  firmataExt.addFeature(reporting);
  firmataExt.addFeature(messageListener);

  setupCompleted = true;
}

void FirmataTransport::update() {
  wdt_reset();
  if (reporting.elapsed()) analogInput.report();
  wdt_reset();
  digitalInput.report();
  while (Firmata.available()) {
    if (messageListener.available()) break;
    if (messageListener.receivedEmptyMessage && (state.at(State::connecting))) {
      state.update(State::connected);
      break;
    }
    wdt_reset();
    Firmata.processInput();
  }
  wdt_reset();
}

void FirmataTransport::reset() {
  FirmataIO::resetPinModes();
  firmataExt.reset();
}

void FirmataTransport::begin() {
  Firmata.disableBlinkVersion();
  Firmata.begin(FirmataIO::kDataRate);
  Firmata.parse(SYSTEM_RESET);
}

uint8_t FirmataTransport::available() const {
  return messageListener.available();
}

char FirmataTransport::read() {
  return messageListener.read();
}

char FirmataTransport::peek() const {
  return messageListener.peek();
}

size_t FirmataTransport::write(uint8_t nextChar) {
  Firmata.write(nextChar);
}

// MessageSender

template<>
void MessageSender<FirmataTransport>::setup() {}

template<>
void MessageSender<FirmataTransport>::sendMessageStart() {
  transport.write(START_SYSEX);
  transport.write(FirmataIO::kTranslatorCommand);
}

template<>
void MessageSender<FirmataTransport>::sendMessageEnd() {
  transport.write(END_SYSEX);
}

// MessageParser

// Messager

template<>
void Messager<FirmataTransport>::setup() {
  if (setupCompleted) return;

  transport.begin();

  parser.setup();
  sender.setup();

  setupCompleted = true;
}

template<>
void Messager<FirmataTransport>::establishConnection() {
  elapsedMillis timer;

  // Run Firmata as usual, but ignore any special messages received
  while (transport.state.at(FirmataTransport::State::connecting)) transport.update();
  // Send a response
  sender.sendMessageStart();
  sender.sendMessageEnd();
  // Wait a bit longer
  timer = 0;
  while (timer < FirmataIO::kPostHandshakeDelay) wdt_reset();
}

}

#endif

