import filecmp
import shutil
import os
from Tkinter import *

def get_original_file(service):
    if service == 'nova':
        return '/etc/nova/api-paste.ini'
    elif service == 'glance':
        return '/etc/glance/glance-api-paste.ini'
    elif service == 'neutron':
        return '/etc/neutron/api-paste.ini'
    else:
        raise Exception('[get_original_file]: Service not supported!!')

def get_new_file(service):
    return './' + service + '-paste.ini'

def get_old_file(service):
    return './' + service + '-paste-old.ini'

def is_aem_enabled(service):
    if filecmp.cmp(get_original_file(service), get_new_file(service)) == True:
        return True
    elif filecmp.cmp(get_original_file(service), get_old_file(service)) == True:
        return False
    else:
        raise Exception('Original api-paste.ini file not recognized!!')

def toggle_aem(service, enable):
    if enable == True:
        shutil.copyfile(get_new_file(service), get_original_file(service))
    else:
        shutil.copyfile(get_old_file(service), get_original_file(service))

def restart_service(service):
    if service == 'nova':
        output = os.popen('sudo service nova-api restart')
    elif service == 'glance':
        output = os.popen('sudo service glance-api restart')
    elif service == 'neutron':
        output = os.popen('sudo service neutron-server restart')
    else:
        raise Exception('[restart_service]: Service not supported!!')
    res = output.read()
    print res
    setText(res)

# toggle_aem('nova', False)
# res = is_aem_enabled('nova')
# print res
# restart_service('nova')

#####################################################################################################################

buttonStatus = {}

def sel_nova():
    service = 'nova'
    res = str(globals()[service + 'Var'].get())
    selection = "You selected the option: " + res
    setText(selection)
    if res == 'enable':
        res_bool = True
    else:
        res_bool = False
    handleRadioButton(service, res_bool)

def sel_glance():
    service = 'glance'
    res = str(globals()[service + 'Var'].get())
    selection = "You selected the option: " + res
    setText(selection)
    if res == 'enable':
        res_bool = True
    else:
        res_bool = False
    handleRadioButton(service, res_bool)

def sel_neutron():
    service = 'neutron'
    res = str(globals()[service + 'Var'].get())
    selection = "You selected the option: " + res
    setText(selection)
    if res == 'enable':
        res_bool = True
    else:
        res_bool = False
    handleRadioButton(service, res_bool)

def handleRadioButton(service, enable):
    print (service, enable)
    toggle_aem(service, enable)
    restart_service(service)

def handleButton_nova():
    restart_service('nova')

def handleButton_glance():
    restart_service('glance')

def handleButton_neutron():
    restart_service('neutron')

def setRadioButton(service, enable):
    if enable:
        globals()[service + 'Var'].set('enable')
    else:
        globals()[service + 'Var'].set('disable')

def setDefaultRadioButtons():
    setRadioButton('nova', is_aem_enabled('nova'))
    setRadioButton('glance', is_aem_enabled('glance'))
    setRadioButton('neutron', is_aem_enabled('neutron'))

    # setRadioButton('nova', True)
    # setRadioButton('glance', False)
    # setRadioButton('neutron', False)

def setText(str):
    label.config(text = str)

root = Tk()
root.geometry('300x400+10+10')

novaVar = StringVar()
glanceVar = StringVar()
neutronVar = StringVar()

setDefaultRadioButtons()

labelframe_nova = LabelFrame(root, text="nova")
labelframe_nova.pack(fill="both", expand="yes")
labelframe_glance = LabelFrame(root, text="glance")
labelframe_glance.pack(fill="both", expand="yes")
labelframe_neutron = LabelFrame(root, text="neutron")
labelframe_neutron.pack(fill="both", expand="yes")

Radiobutton(labelframe_nova, text="Nova's AEM [ON]", variable=novaVar, value='enable', command=sel_nova).pack()
Radiobutton(labelframe_nova, text="Nova's AEM [OFF]", variable=novaVar, value='disable', command=sel_nova).pack()
Button(labelframe_nova, text ="Restart nova-api", command = handleButton_nova).pack()

Radiobutton(labelframe_glance, text="Glance's AEM [ON]", variable=glanceVar, value='enable', command=sel_glance).pack()
Radiobutton(labelframe_glance, text="Glance's AEM [OFF]", variable=glanceVar, value='disable', command=sel_glance).pack()
Button(labelframe_glance, text ="Restart glance-api", command = handleButton_glance).pack()

Radiobutton(labelframe_neutron, text="Neutron's AEM [ON]", variable=neutronVar, value='enable', command=sel_neutron).pack()
Radiobutton(labelframe_neutron, text="Neutron's AEM [OFF]", variable=neutronVar, value='disable', command=sel_neutron).pack()
Button(labelframe_neutron, text ="Restart neutron-server", command = handleButton_neutron).pack()


label = Label(root)
label.pack()
root.title("API Paste Change (APC)")
root.mainloop()