#include <ConfigurableFirmata.h>

#include <DigitalInputFirmata.h>
#include <DigitalOutputFirmata.h>
#include <AnalogInputFirmata.h>
#include <AnalogOutputFirmata.h>
#include <AnalogWrite.h>
#include <FirmataReporting.h>
#include <FirmataExt.h>

DigitalInputFirmata digitalInput;
DigitalOutputFirmata digitalOutput;
AnalogInputFirmata analogInput;
AnalogOutputFirmata analogOutput;

FirmataReporting reporting;

FirmataExt firmataExt;

void systemResetCallback()
{
  for (byte i = 0; i < TOTAL_PINS; i++) {
    if (IS_PIN_ANALOG(i)) {
      Firmata.setPinMode(i, ANALOG);
    } else if (IS_PIN_DIGITAL(i)) {
      Firmata.setPinMode(i, OUTPUT);
    }
  }
  firmataExt.reset();
}

void initTransport()
{
  // Uncomment to save a couple of seconds by disabling the startup blink sequence.
  Firmata.disableBlinkVersion();
  Firmata.begin(57600);
}

void initFirmata()
{
  Firmata.setFirmwareVersion(FIRMATA_FIRMWARE_MAJOR_VERSION, FIRMATA_FIRMWARE_MINOR_VERSION);

  firmataExt.addFeature(digitalInput);
  firmataExt.addFeature(digitalOutput);
  firmataExt.addFeature(analogInput);
  firmataExt.addFeature(analogOutput);
  firmataExt.addFeature(reporting);

  Firmata.attach(SYSTEM_RESET, systemResetCallback);
}

void setup()
{
  initFirmata();

  initTransport();

  Firmata.parse(SYSTEM_RESET);
}

void loop() {
  digitalInput.report();

  while (Firmata.available()) Firmata.processInput();

  if (reporting.elapsed()) analogInput.report();
}
