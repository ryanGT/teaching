import radiobutton_dialog

#import pygtk
#pygtk.require('2.0')
import gtk
import rwkos, os

def get_path_for_mass_spring_damper_sketch():
    labels = ['undamped free', \
              'damped free', \
              'damped forced', \
              'two DOF']

    keys = ['1','2','3','4']
    
    filenames = ['undamped_free_vibration_mass_spring.jpg', \
                 'damped_free_vibration_mass_spring_damper.jpg', \
                 'forced_damped_vibration.jpg', \
                 'two_dof_free.jpg']

    mygui = radiobutton_dialog.RadioButtons(labels, keys)
    mygui.main()
    if mygui.canceled:
        print('Canceled!!!')
        return None
    ind = mygui.get_selected_ind()
    drawing_dir = rwkos.FindFullPath('siue/classes/452/2011/tikz_drawings')
    fullpath = os.path.join(drawing_dir, filenames[ind])
    return fullpath


if __name__ == '__main__':
    fullpath = get_path_for_mass_spring_damper_sketch()
    print('fullpath = ' + str(fullpath))
    
