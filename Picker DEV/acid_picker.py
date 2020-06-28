#/--------------------------------------------------------------------------------////
#
#             acid_picker.py 
#             version 0.1, last modified 28-06-2020
#             Copyright (C) 2020 Luke Davenport
#             Email: luke.l.davenport@gmail.com
#             Website: www.davenportcreations.com
#             Repo: https://github.com/Midnaut/Acid-Picker
#             License: [MIT] https://choosealicense.com/licenses/mit/
#
#/--------------------------------------------------------------------------------////
#                  I N S T A L L A T I O N:
#
# this script will do its best to generate thee required assets it needs but you should
# download the entire picker folder and add its path to the userSetup. 
# Then, inside either a shelf button or script window you should call:
# acid_picker.config_loader_ui()
#
#                         U S A G E:
#
# the loader UI will search for a default data file to configure the window,
# if you dont have or have a corrupted data file, create new data file will give you
# a clean template.
#
# with a config loaded, you will be presented with a grid of buttons, clicking on a button
# will select the associated control assuming you have named and configured the picker
# correctly. 
#
# click : replace selection with object
# shift + click: will add object to selection.
# 



import os
import maya.cmds as cmds
import json
import webbrowser


IMG_PATH = os.path.dirname(__file__) + "/img/"
CONFIG_PATH = os.path.dirname(__file__) + "/config/"
COLOR_DARK_GRAY = (0.15,0.15,0.15)
COLOR_ORANGE = (0.87, 0.51, 0.01)


def init_picker():
    #load in via JSON the controls to target
    pass

def load_data_file(config_file):

    config_file_path = CONFIG_PATH+config_file

    print("Loading config file: {0}".format(config_file_path))
    
    try:
        with open(config_file_path) as json_file:
            data = json.load(json_file)
        return data
    except ValueError:  
        create_error_dialog("Decoding JSON has failed.\nPlease validate your json and try again.".format(config_file))


def confirm_new_data_file():
    result = cmds.confirmDialog(title='New Default Config File?',
                                message='''Warning! This will overwrite any data in the default_data file if it exists!

                                Are you sure you want to proceed?''',
                                button=['Yes', 'No'],
                                defaultButton='Yes',
                                cancelButton='No')
    # EXECUTE button
    if result == 'Yes':
        create_default_data_file()

#used for creating a demo file that the user can modify for purpose
def create_default_data_file():
    data = {}
    data['left_hand'] = {
        'name': 'Left Hand',
        'groups': [],
        'color' : (0.0, 0.0, 1.0),
        'group_count' : 5,
        'max_members' : 4,
        'control_prefix' : 'L_',
        'control_suffix' : '_CTL'
    }

    #add the definitions for the fingers
    data['left_hand']['groups'].append({
        'name': 'thumb',
        'controls': ['thumb0', 'thumb1', 'thumb2'],
        'control_count': 3
    })
    data['left_hand']['groups'].append({
        'name': 'index',
        'controls': ['index0', 'index1', 'index2', 'index3'],
        'control_count': 4
    })
    data['left_hand']['groups'].append({
        'name': 'middle',
        'controls': ['middle0', 'middle1', 'middle2', 'middle3'],
        'control_count': 4
    })
    data['left_hand']['groups'].append({
        'name': 'ring',
        'controls': ['ring0', 'ring1', 'ring2', 'ring3'],
        'control_count': 4
    })
    data['left_hand']['groups'].append({
        'name': 'pinkie',
        'controls': ['pinkie0', 'pinkie1', 'pinkie2', 'pinkie3'],
        'control_count': 4
    })

    #additional config data
    data['config'] = {
        'set_name' : 'Default Data',
        'set_keys' : ['left_hand'],
    }
    
    new_file_path = CONFIG_PATH + 'default_data.txt'
    #save out the file in a nice human readable format
    with open(new_file_path, 'w') as outfile:
        json.dump(data, outfile, indent = 4, sort_keys = True)

    print("New file added at {0}".format(new_file_path))


def is_shift_down(*args):
    mods = cmds.getModifiers()
    #bitwise 1 to get if shift down
    if (mods & 1) > 0:
        return True
    else:
        return False

def is_control_down(*args):
    mods = cmds.getModifiers()
    #bitwise 4 to get if control down
    if (mods & 4) > 0:
        return True
    else:
        return False

#select that is set to add if shift is held down
def modified_select(name):
    if cmds.objExists(name):
        #add to selection
        if is_shift_down():
            cmds.select(name, add=True)
        #remove from selection
        elif is_control_down():
            cmds.select(name, deselect = True)
        #non modified behavior
        else:
            cmds.select(name)
    else:
        print("Warning! Object {0} does not exist, please check your configuration.".format(name))

def create_error_dialog(message_text):
    result = cmds.confirmDialog(title='ERROR',
                                message=message_text,
                                button=['OKAY', 'HELP'],
                                defaultButton='OKAY')

    if result == "HELP":
        webbrowser.open("https://github.com/Midnaut/Acid-Picker")

def dynamic_button_layout(config_file):
    #load in the settings data
    settings_data = load_data_file(config_file)

    #for each key in set keys make a new tab, named after the name
    set_keys = settings_data['config']['set_keys']
    
    #make our layout objects
    form = cmds.formLayout()
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    #set padding
    cmds.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )

    tab_name_list = []
    tab_content_list = []

    for key in set_keys:
        #get the display name for the tab
        tab_name = settings_data[key]['name']
        tab_name_list.append(tab_name)

        #this created the content in the form of a grid layout
        content = add_control_grid(settings_data, key)
        tab_content_list.append(content)

    #make the tuple how maya wants it
    tab_label_tuple = tuple((content,name) for content, name in zip(tab_content_list, tab_name_list))

    print(tab_label_tuple)
    #add the contents
    cmds.tabLayout( tabs, edit=True, tabLabel=tab_label_tuple)

    #escape the layout
    cmds.setParent('..')

def add_control_grid(settings_data, set_key):
    #used to fetch the control set
    control_set = settings_data[set_key]

    #going to make a grid for the hand controls, this is a POC but in future other layouts would be good
    grid = cmds.gridLayout( numberOfColumns=control_set['group_count'], cellWidthHeight=(50, 50) )

    control_prefix = control_set['control_prefix']
    control_suffix = control_set['control_suffix']
    color = control_set['color']

    #formatting information would ideally be standardised across the auto rigger, still, POC
    template = control_prefix+"{0}"+control_suffix

    #add the column headers
    for item in control_set['groups']:
        cmds.text(label = item['name'], backgroundColor = COLOR_ORANGE)

    #cast to int from string in the json
    max_group_members = int(control_set['max_members'])

    for i in range(max_group_members):
        #fetch required data for the individual controls
        control_set = settings_data[set_key] #eg "Left Hand"

        #i know nested for loops are bad but the gridlayout wants it this way
        for group in control_set['groups']: #for each finger in the left hand set

            #get how many controls are in this group
            control_count = int(group['control_count'])
            controls = group['controls']

            if i < control_count:
                control_name = template.format(controls[i])
                #make the button command, holding shift will let you add to the selection
                command_text = "acid_picker.modified_select(name = '{0}')".format(control_name)
                #make the button
                cmds.button(label = controls[i], backgroundColor = color, command = command_text)

            else:
                cmds.separator(style='none') #take up layout slot


    #escape the grid layout 
    cmds.setParent('..')
    #return this grid layout so it can be made into a tab
    return grid


def picker_ui(config_file = "default_data.txt"):
    #**************************************************************************
    # CLOSE if exists (avoid duplicates)
    ui_title = 'control_picker'

    if cmds.window(ui_title, exists=True):
        print('CLOSE duplicate window')
        cmds.deleteUI(ui_title)
    #**************************************************************************

    #technically could load in setting first to set size based on the loaded profile
    window = cmds.window(title="Control Picker", widthHeight=(350, 350))

    cmds.columnLayout(adjustableColumn=True)

    #header bar
    cmds.rowLayout(numberOfColumns = 2, adjustableColumn = 2, backgroundColor = COLOR_DARK_GRAY)
    img = cmds.image(image=IMG_PATH + 'picker_icon_small.png')
    cmds.text( label='Control Picker', font = 'boldLabelFont')
    cmds.setParent('..')
    
    dynamic_button_layout(config_file)

    cmds.showWindow(window)

def load_config():
    config_file = cmds.textField('config_file_name', query=True, text= True)
    config_file_path = CONFIG_PATH+config_file

    if os.path.isfile(config_file_path):
        picker_ui(config_file = config_file)
    else:
        create_error_dialog("Warning! file : {0} does not exist in the config file path.\nPlease check and try again.".format(config_file))


def config_loader_ui():
    #**************************************************************************
    # CLOSE if exists (avoid duplicates)
    ui_title = 'config_loader'

    if cmds.window(ui_title, exists=True):
        print('CLOSE duplicate window')
        cmds.deleteUI(ui_title)
    #**************************************************************************

    window = cmds.window(title="config_loader", widthHeight=(350, 50))

    cmds.columnLayout(adjustableColumn=True)

    cmds.button(label="create default settings",
                width=350, command="acid_picker.confirm_new_data_file()",
                backgroundColor = COLOR_ORANGE)

    cmds.rowLayout(numberOfColumns = 3, adjustableColumn = 2)
    cmds.text(label = "File Name")
    cmds.textField('config_file_name', text= "default_data.txt")
    cmds.button(label = "Load",
                command= "acid_picker.load_config()",
                backgroundColor = COLOR_ORANGE)
    

    cmds.showWindow(window)



