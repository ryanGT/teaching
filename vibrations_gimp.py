import radiobutton_dialog

#import pygtk
#pygtk.require('2.0')
import gtk

def get_path_for_mass_spring_damper_sketch():
    mygui = radiobutton_dialog.RadioButtons()
    mygui.main()
    if mygui.canceled:
        print('Canceled!!!')
        return None
    print(str(mygui.radio_buttons))
    mybools = []
    for rb in mygui.radio_buttons:
        curbool = rb.get_active()
        mybools.append(curbool)

    print(str(mybools))

    return mybools


    
