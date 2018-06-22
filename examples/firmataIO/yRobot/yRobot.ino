#define DISABLE_LOGGING

#define LHR_Messaging_FirmataIO
#define LHR_Protocol_Core
#define LHR_Protocol_AbsoluteLinearActuatorAxis
#define LHR_Protocol_CumulativeLinearActuatorAxis
#include <LiquidHandlingRobotics.h>

//#define LHR_Standard_pipettorAxis
//#define LHR_Standard_zAxis
#define LHR_Standard_yAxis
//#define LHR_Standard_xAxis
#include <StandardLiquidHandlingRobot.h>

LHR_instantiateMessaging(transport, messager);
LHR_instantiateBasics(core, board);
LHR_instantiateAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator, messager, motors);

void setup()
{
  LHR_setupMessaging(transport, messager, core);
  LHR_setupBasics(core, board);
  LHR_setupAxes(pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator);
  LHR_connect(transport, messager, core, board, pipettorAxis, zAxis, yAxis, yAxisCalibrator, xAxis, xAxisCalibrator);
}

void loop() {
  LHR_updateMessaging(transport, messager);
  LHR_updateBasics(core, board);
  LHR_updateAxes(pipettorAxis, zAxis, yAxis, xAxis);
}
