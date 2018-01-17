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
from lhrhost.modules.verticalpositioner import VerticalPositioner

class GuiTargeting(tk.Frame, ConvergedPositionReceiver):
    def __init__(self, vertical_positioner, gui=None):
        super().__init__(gui)
        self.vertical_positioner = vertical_positioner

        self.gui = gui
        self.gui.title('Vertical Positioner')

        self.position_tracking = False
        self.status = tk.StringVar()

        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.create_widgets()

    def start_event_loop(self):
        self.gui.mainloop()

    def quit(self):
        self.gui.destroy()

    # Widgets

    def create_widgets(self):
        self.create_status_widgets()
        self.quit = tk.Button(self, text='Quit', command=self.quit)
        self.quit.pack(side='bottom', fill=tk.X)
        self.create_targeting_widgets()

    def create_status_widgets(self):
        self.status_frame = tk.Frame(self)
        self.status_frame.pack(side='bottom', fill=tk.X)
        self.status_message = tk.Label(
            self.status_frame, textvariable=self.status, width=40
        )
        self.status_message.pack(fill=tk.X)

    def create_targeting_widgets(self):
        self.target_frame = tk.LabelFrame(self, text='Target Position')
        self.target_frame.pack(side='top', fill=tk.BOTH)
        self.track_target = tk.Button(self.target_frame, text='Follow Continuously',
                                      command=self.toggle_position_tracking)
        self.track_target.pack(side='bottom', fill=tk.X)
        self.apply_target = tk.Button(self.target_frame, text='Go and Hold',
                                      command=self.apply_target_position)
        self.apply_target.pack(side='bottom', fill=tk.X)
        self.target_position = tk.Scale(
            self.target_frame, length=300,
            from_=self.vertical_positioner.top_mark,
            to=self.vertical_positioner.bottom_mark,
            resolution=0.01, tickinterval=0.1,
            command=self.on_target_position_change,
        )
        self.target_position.set(self.vertical_positioner.top_mark)
        self.target_position.pack(side='top', fill=tk.Y)

    # Targeting

    def on_converged_position(self, position_unitless, position_converged):
        if not self.position_tracking:
            self.status.set('Reached and holding at {:.2f} {}...'.format(
                position_converged, self.vertical_positioner.physical_unit
            ))

    def apply_target_position(self):
        self.vertical_positioner.set_target_position(
            self.target_position.get(),
            units=self.vertical_positioner.physical_unit
        )
        self.track_target.config(relief=tk.RAISED)
        self.status.set('Moving to the {} {}...'.format(
            self.target_position.get(), self.vertical_positioner.physical_unit
        ))
        self.position_tracking = False

    # Target following

    def toggle_position_tracking(self):
        if self.position_tracking:
            self.position_tracking = False
            self.track_target.config(relief=tk.RAISED)
            self.status.set('No longer following target position.')
            return
        self.position_tracking = True
        self.status.set('Following target position as it is changed...')
        self.track_target.config(relief=tk.SUNKEN)

    def on_target_position_change(self, new_position):
        if self.position_tracking:
            self.vertical_positioner.set_target_position(
                float(new_position),
                units=self.vertical_positioner.physical_unit
            )

def main():
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    translator = ASCIITranslator()
    dispatcher = Dispatcher()
    vertical_positioner = VerticalPositioner()
    gui_root = tk.Tk()
    gui_app = GuiTargeting(vertical_positioner, gui=gui_root)

    monitor.listeners.append(translator)
    translator.message_listeners.append(dispatcher)
    translator.line_listeners.append(monitor)
    dispatcher.receivers[None].append(vertical_positioner)
    vertical_positioner.converged_position_listeners.append(gui_app)
    vertical_positioner.message_listeners.append(translator)

    connection.open()
    monitor.start_thread()
    gui_app.start_event_loop()
    connection.reset()


if __name__ == '__main__':
    main()

