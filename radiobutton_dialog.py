#!/usr/bin/env python

# example radiobuttons.py

#import pygtk
#pygtk.require('2.0')
import gtk

class RadioButtons:
    def callback(self, widget, data=None):
        pass
        #print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])


    def get_selected_ind(self):
        for i, rb in enumerate(self.radio_buttons):
            curbool = rb.get_active()
            if curbool:
                return i
            

    def close_application(self, widget, data=None, *args):
        self.canceled = False
        if data == 0:
            self.canceled = True
        gtk.main_quit()
        return data

    def __init__(self, labels=['radio 1','radio 2'], \
                 accelkeys=['1','2']):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        #self.window.connect("delete_event", self.close_application)

        self.window.set_title("radio buttons")
        self.window.set_border_width(0)

        self.ag = gtk.AccelGroup()
        self.window.add_accel_group(self.ag)

        box1 = gtk.VBox(False, 0)
        self.window.add(box1)
        box1.show()

        box2 = gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()

        self.radio_buttons = []
        prev_button = None
        for label, key in zip(labels, accelkeys):
            button = gtk.RadioButton(prev_button, label)
            button.connect("toggled", self.callback, label)
            button.show()
            button.add_accelerator("clicked", self.ag, ord(key), \
                                   #gtk.gdk.SHIFT_MASK, \
                                   0, \
                                   accel_flags=gtk.ACCEL_VISIBLE)
            mylabel = gtk.Label(key)
            mylabel.show()
            hbox = gtk.HBox(False, 5)
            hbox.show()
            hbox.pack_start(mylabel, False)
            hbox.pack_start(button, False)
            self.radio_buttons.append(button)
            box2.pack_start(hbox, False)
            prev_button = button
            
        ## button1.show()
        ## self.radio_buttons.append(button1)

        ## button2 = gtk.RadioButton(button1, "radio button2")
        ## button2.connect("toggled", self.callback, "radio button 2")
        ## button2.set_active(True)
        ## box2.pack_start(button2, True, True, 0)
        ## button2.show()
        ## self.radio_buttons.append(button2)

        ## button3 = gtk.RadioButton(button2, "radio button3")
        ## button3.connect("toggled", self.callback, "radio button 3")
        ## box2.pack_start(button3, True, True, 0)
        ## button3.show()
        ## self.radio_buttons.append(button3)

        separator = gtk.HSeparator()
        box1.pack_start(separator, False, True, 0)
        separator.show()

        box2 = gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, False, True, 0)
        box2.show()

        self.go_button = gtk.Button("Go")
        sep1 = gtk.HSeparator()
        hbox = gtk.HBox(True, 5)
        self.cancel_button = gtk.Button('Cancel')
        self.go_button.show()
        self.cancel_button.show()
        hbox.show()

        self.cancel_button.connect_object("clicked", self.close_application, self.cancel_button,
                                          0)
        self.go_button.connect_object("clicked", self.close_application, self.go_button,
                                      1)

        self.go_button.add_accelerator("clicked", self.ag, ord('g'), \
                                       #gtk.gdk.SHIFT_MASK, \
                                       0, \
                                       accel_flags=gtk.ACCEL_VISIBLE)

        self.cancel_button.add_accelerator("clicked", self.ag, ord('q'), \
                                           0, \
                                           accel_flags=gtk.ACCEL_VISIBLE)

        self.cancel_button.add_accelerator("clicked", self.ag, ord('c'), \
                                           0, 0)
        hbox.pack_start(self.cancel_button, False)
        hbox.pack_start(self.go_button, False)

        
        box2.pack_start(hbox, False)
        self.go_button.set_flags(gtk.CAN_DEFAULT)
        self.go_button.grab_default()
        self.go_button.show()
        self.window.show()


    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()
