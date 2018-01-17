import tkinter as tk

from lhrhost.serialio.transport import (
    ASCIIConnection, ASCIIMonitor
)
from lhrhost.serialio.dispatch import (
    Message, Dispatcher,
    ASCIITranslator
)
from lhrhost.modules.actuators import (
    AbsoluteLinearActuator, ConvergedPositionReceiver
)
from lhrhost.modules.pipettor import Pipettor
from lhrhost.modules.verticalpositioner import VerticalPositioner

class GuiTargeting(tk.Frame, ConvergedPositionReceiver):
    def __init__(self, pipettor, vertical_positioner, gui=None):
        super().__init__(gui)
        self.modules = {
            'pipettor': pipettor,
            'vertical positioner': vertical_positioner
        }

        self.gui = gui
        self.gui.title('Pipettor + Vertical Positioner')

        self.states = {
            'pipettor': {
                'position_tracking': False
            },
            'vertical positioner': {
                'position_tracking': False
            }
        }
        self.widgets = {
            'pipettor': {},
            'vertical positioner': {}
        }

        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.create_widgets()

    def start_event_loop(self):
        self.gui.mainloop()

    def quit(self):
        self.gui.destroy()

    # Widgets

    def create_widgets(self):
        self.create_targeting_widgets('pipettor')
        self.create_targeting_widgets('vertical positioner')

    def create_targeting_widgets(self, module):
        target_frame = tk.LabelFrame(self, text='Target Position for {}'
                                     .format(module))
        target_frame.pack(side='top', fill=tk.BOTH)
        self.widgets[module]['track_target'] = tk.Button(
            target_frame, text='Follow Continuously',
            command=lambda: self.toggle_position_tracking(module)
        )
        self.widgets[module]['track_target'].pack(side='bottom', fill=tk.X)
        apply_target = tk.Button(
            target_frame, text='Go and Hold',
            command=lambda: self.apply_target_position(module)
        )
        apply_target.pack(side='bottom', fill=tk.X)
        self.widgets[module]['target_position'] = tk.Scale(
            target_frame, length=300,
            from_=self.modules[module].top_limit,
            to=self.modules[module].bottom_limit,
            resolution=0.01, tickinterval=0.1,
            command=lambda x: self.on_target_position_change(x, module),
        )
        self.widgets[module]['target_position'].set(self.modules[module].top_limit)
        self.widgets[module]['target_position'].pack(side='top', fill=tk.Y)

    # Targeting

    def on_converged_position(self, position_unitless, position_converged):
        pass

    def apply_target_position(self, module):
        self.modules[module].set_target_position(
            self.widgets[module]['target_position'].get(),
            units=self.modules[module].physical_unit
        )
        self.widgets[module]['track_target'].config(relief=tk.RAISED)
        self.states[module]['position_tracking'] = False

    # Target following

    def toggle_position_tracking(self, module):
        if self.states[module]['position_tracking']:
            self.states[module]['position_tracking'] = False
            self.widgets[module]['track_target'].config(relief=tk.RAISED)
            return
        self.states[module]['position_tracking'] = True
        self.widgets[module]['track_target'].config(relief=tk.SUNKEN)

    def on_target_position_change(self, new_position, module):
        if self.states[module]['position_tracking']:
            self.modules[module].set_target_position(
                float(new_position),
                units=self.modules[module].physical_unit
            )

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    translator = ASCIITranslator()
    dispatcher = Dispatcher()
    verticalPositioner = VerticalPositioner()
    pipettor = Pipettor()
    gui_root = tk.Tk()
    gui_app = GuiTargeting(pipettor, verticalPositioner, gui=gui_root)

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)

    dispatcher.receivers[None].append(pipettor)
    pipettor.converged_position_listeners.append(gui_app)
    pipettor.message_listeners.append(translator)

    dispatcher.receivers[None].append(verticalPositioner)
    verticalPositioner.converged_position_listeners.append(gui_app)
    verticalPositioner.message_listeners.append(translator)

    connection.open()
    monitor.start_thread()
    gui_app.start_event_loop()
    connection.reset()


if __name__ == '__main__':
    main()

