#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <FirmataIO.h>
#include <CoreProtocol.h>

using namespace LiquidHandlingRobotics;

// Firmata communications
FirmataTransport transport;
FirmataMessager messager(transport);
makeFirmataTransportResetCallback(transport);

// Shared components
CoreProtocol<FirmataMessager> coreProtocol(messager);

void setup()
{
  coreProtocol.setup();
  transport.setup();
  attachFirmataTransportResetCallback(transport);
  messager.setup();
}

void loop() {
  if (transport.reporting.elapsed()) transport.analogInput.report();
  transport.digitalInput.report();
  while (Firmata.available() && !transport.available()) Firmata.processInput();
  
  messager.update();
  coreProtocol.update();
}
