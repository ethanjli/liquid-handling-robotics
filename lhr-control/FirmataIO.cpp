#include "FirmataIO.h"

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

// FirmataTranslator

bool FirmataTranslator::handlePinMode(uint8_t pin, int mode) {
  return false;
}

void FirmataTranslator::handleCapability(uint8_t pin) {
  return false;
}

bool FirmataTranslator::handleSysex(uint8_t command, uint8_t argc, uint8_t *argv) {
  if (command != FirmataIO::kTranslatorCommand) {
    bufferLength = 0;
    buffer = nullptr;
    bufferPosition = 0;
    return false;
  }

  bufferLength = argc;
  buffer = argv;
  bufferPosition = 0;
  return true;
}

void FirmataTranslator::reset() {
  bufferLength = 0;
  buffer = nullptr;
  bufferPosition = 0;
}

uint8_t FirmataTranslator::available() const {
  if (buffer == nullptr) return 0;
  return bufferLength - bufferPosition;
}

char FirmataTranslator::read() {
  if (buffer == nullptr) return -1;

  char current = peek();
  ++bufferPosition;
  return current;
}

char FirmataTranslator::peek() const {
  if (buffer == nullptr) return -1;

  return static_cast<char>(*(buffer + bufferPosition));
}

// FirmataTransport

void FirmataTransport::setup() {
  if (setupCompleted) return;

  Firmata.setFirmwareVersion(
      FIRMATA_FIRMWARE_MAJOR_VERSION, FIRMATA_FIRMWARE_MINOR_VERSION
  );

  firmataExt.addFeature(digitalInput);
  firmataExt.addFeature(digitalOutput);
  firmataExt.addFeature(analogInput);
  firmataExt.addFeature(analogOutput);
  firmataExt.addFeature(reporting);
  firmataExt.addFeature(firmataTranslator);

  setupCompleted = true;
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
  return firmataTranslator.available();
}

char FirmataTransport::read() {
  return firmataTranslator.read();
}

char FirmataTransport::peek() const {
  return firmataTranslator.peek();
}

// MessageSender

template<>
void MessageSender<FirmataTransport>::setup() {}

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
}

}

