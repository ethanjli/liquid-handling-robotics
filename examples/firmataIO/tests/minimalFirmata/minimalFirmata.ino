#define DISABLE_LOGGING

#define LHR_Messaging_FirmataIO
#include <LiquidHandlingRobotics.h>
#include <StandardLiquidHandlingRobot.h>

using namespace LiquidHandlingRobotics;
using Transport = LiquidHandlingRobotics::Messaging::FirmataTransport;

Transport transport;

void setup()
{
  transport.setup();
  transport.begin();
}

void loop() {
  transport.update();
}
