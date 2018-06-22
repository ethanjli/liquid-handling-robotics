// Messaging

#ifdef LHR_Messaging_Messages
  #include "Messaging/Messages.h"
#endif

#ifdef LHR_Messaging_FirmataIO
  #include "Messaging/FirmataIO.h"
#endif

#ifdef LHR_Messaging_ASCIIIO
  #include "Messaging/ASCIIIO.h"
#endif

#ifndef LHR_Messager
  #if defined(LHR_Messaging_FirmataIO) && !defined(LHR_Messaging_ASCIIIO)
#pragma message("INFO: LiquidHandlingRobotics::Transport defined to use the Firmata-based transport layer.")
#pragma message("INFO: LiquidHandlingRobotics::Messager defined to use the Firmata-based transport layer.")
    #define LHR_Messager
    namespace LiquidHandlingRobotics {
      using Transport = Messaging::FirmataTransport;
      using Messager = Messaging::FirmataMessager;
    }
  #elif defined(LHR_Messaging_ASCIIIO) && !defined(LHR_Messaging_FirmataIO)
#pragma message("INFO: LiquidHandlingRobotics::Transport defined to use the ASCII-based transport layer.")
#pragma message("INFO: LiquidHandlingRobotics::Messager defined to use the ASCII-based transport layer.")
    #define LHR_Messager
    namespace LiquidHandlingRobotics {
      using Transport = HardwareSerial;
      using Messager = Messaging::ASCIIMessager;
    }
  #else
#pragma message("WARNING: LiquidHandlingRobotics::Transport must be defined manually.")
#pragma message("WARNING: LiquidHandlingRobotics::Messager must be defined manually.")
  #endif
#endif

// Protocol

#ifdef LHR_Protocol_Core
  #include "Protocol/Core.h"
  #ifndef LHR_Core
    #ifdef LHR_Messager
#pragma message("INFO: LiquidHandlingRobotics::Core defined to use LiquidHandlingRobotics::Messager.")
      #define LHR_Core
      namespace LiquidHandlingRobotics {
        using Core = Protocol::Core<Messager>;
      }
    #else
#pragma message("WARNING: LiquidHandlingRobotics::Core must be defined manually.")
    #endif
  #endif
#endif

#ifdef LHR_Protocol_Board
  #include "Protocol/Board.h"
  #ifndef LHR_Board
    #ifdef LHR_Messager
#pragma message("INFO: LiquidHandlingRobotics::Board defined to use LiquidHandlingRobotics::Messager.")
      #define LHR_Board
      namespace LiquidHandlingRobotics {
        using Board = Protocol::Board<Messager>;
      }
    #else
#pragma message("WARNING: LiquidHandlingRobotics::Board must be defined manually.")
    #endif
  #endif
#endif

#ifdef LHR_Protocol_AbsoluteLinearActuatorAxis
  #include "Protocol/LinearActuatorAxis.h"
  #define LPC_Control_AbsoluteLinearPosition
  #include <LinearPositionControl.h>
  #ifndef LHR_AbsoluteLinearActuatorAxis
    #ifdef LHR_Messager
#pragma message("INFO: LiquidHandlingRobotics::AbsoluteLinearActuatorAxis defined to use LiquidHandlingRobotics::Messager.")
      #define LHR_AbsoluteLinearActuatorAxis
      namespace LiquidHandlingRobotics {
        using AbsoluteLinearActuatorAxis = Protocol::LinearActuatorAxis<
          LinearPositionControl::Control::AbsoluteLinearActuator, Messager
        >;
      }
    #else
#pragma message("WARNING: LiquidHandlingRobotics::AbsoluteLinearActuatorAxis must be defined manually.")
    #endif
  #endif
#endif

#ifdef LHR_Protocol_CumulativeLinearActuatorAxis
  #include "Protocol/LinearActuatorAxis.h"
  #define LPC_Control_CumulativeLinearPosition
  #include <LinearPositionControl.h>
  #ifndef LHR_CumulativeLinearActuatorAxi
    #ifdef LHR_Messager
#pragma message("INFO: LiquidHandlingRobotics::CumulativeLinearActuatorAxis defined to use LiquidHandlingRobotics::Messager.")
      #define LHR_CumulativeLinearActuatorAxis
      namespace LiquidHandlingRobotics {
        using CumulativeLinearActuatorAxis = Protocol::LinearActuatorAxis<
          LinearPositionControl::Control::CumulativeLinearActuator, Messager
        >;
      }
    #else
#pragma message("WARNING: LiquidHandlingRobotics::CumulativeLinearActuatorAxis must be defined manually.")
    #endif
  #endif
#endif

#ifdef LHR_Protocol_Placeholder
  #include "Protocol/Placeholder.h"
#endif

