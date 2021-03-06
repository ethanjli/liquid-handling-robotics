#ifndef LHR_Messaging_FirmataIO_h
#define LHR_Messaging_FirmataIO_h

#include <ConfigurableFirmata.h>
#include <FirmataFeature.h>
#include <DigitalInputFirmata.h>
#include <DigitalOutputFirmata.h>
#include <AnalogInputFirmata.h>
#include <AnalogOutputFirmata.h>
#include <FirmataReporting.h>
#include <FirmataExt.h>

#include <StateVariable.h>

#include "Messages.h"

namespace LiquidHandlingRobotics { namespace Messaging {

namespace FirmataIO {
  const long kDataRate = 57600;
  const char kTranslatorCommand = 0x0F; // sysex command reserved for user-defined commands
  const unsigned int kPreHandshakeDelay = 1000;
  const char kHandshakeChar = '~';
  const unsigned int kHandshakeInitiateInterval = 500;
  const unsigned int kPostHandshakeDelay = 500;

  void resetPinModes();

  namespace States {
    enum class Transport : uint8_t {
      connecting,
      connected
    };
  }
}

class FirmataMessageListener : public FirmataFeature {
  public:
    bool receivedEmptyMessage = false;

    // Implement FirmataFeature
    bool handlePinMode(uint8_t pin, int mode);
    void handleCapability(uint8_t pin);
    bool handleSysex(uint8_t command, uint8_t argc, uint8_t *argv);
    void reset();

    // Implement Stream-like interface
    uint8_t available() const;
    char read();
    char peek() const;

  private:
    char *buffer = nullptr;
    uint8_t bufferLength = 0;
    uint8_t bufferPosition = 0;
};

class FirmataTransport : public Print {
  public:
    using State = FirmataIO::States::Transport;

    FirmataExt firmataExt;
    // Firmata core features
    DigitalInputFirmata digitalInput;
    DigitalOutputFirmata digitalOutput;
    AnalogInputFirmata analogInput;
    AnalogOutputFirmata analogOutput;
    FirmataReporting reporting;
    // Firmata message listener feature
    FirmataMessageListener messageListener;

    LinearPositionControl::SimpleStateVariable<FirmataIO::States::Transport> state;

    void setup();
    void update();
    void reset();

    // Implement Stream-like interface
    void begin();
    uint8_t available() const;
    char read();
    char peek() const;
    virtual size_t write(uint8_t nextChar);

  private:
    bool setupCompleted = false;
};

using FirmataMessageSender = MessageSender<FirmataTransport>;
using FirmataMessageParser = MessageParser<FirmataTransport>;
using FirmataMessager = Messager<FirmataTransport>;

} }

#define LHR_makeFirmataTransportResetCallback(transport) void firmataTransportResetCallback() {transport.reset();}
#define LHR_attachFirmataTransportResetCallback(transport) Firmata.attach(SYSTEM_RESET, firmataTransportResetCallback);

#include "FirmataIO.tpp"

#endif

