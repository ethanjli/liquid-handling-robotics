#define DISABLE_LOGGING

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
  messager.establishConnection();
  coreProtocol.onConnect();
}

void loop() {
  transport.update();
  messager.update();
  coreProtocol.update();
}
