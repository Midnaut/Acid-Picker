#******************************************************************************
# author      = luke.l.davenport@gmail.com
#******************************************************************************

import os
import maya.cmds as cmds
import json


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
    
    with open(config_file_path) as json_file:
        data = json.load(json_file)
    return data

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
    data['fingers'] = []

    #add the definitions for the fingers
    data['fingers'].append({
        'name': 'thumb',
        'controls': ['thumb0', 'thumb1', 'thumb2'],
        'control_count': 3
    })
    data['fingers'].append({
        'name': 'index',
        'controls': ['index0', 'index1', 'index2', 'index3'],
        'control_count': 4
    })
    data['fingers'].append({
        'name': 'middle',
        'controls': ['middle0', 'middle1', 'middle2', 'middle3'],
        'control_count': 4
    })
    data['fingers'].append({
        'name': 'ring',
        'controls': ['ring0', 'ring1', 'ring2', 'ring3'],
        'control_count': 4
    })
    data['fingers'].append({
        'name': 'pinkie',
        'controls': ['pinkie0', 'pinkie1', 'pinkie2', 'pinkie3'],
        'control_count': 4
    })

    #additional config data
    data['config'] = {
        'set_name' : 'Left Hand',
        'set_key' : 'fingers',
        'group_count' : 5,
        'max_members' : 4,
        'control_prefix' : 'L_',
        'control_suffix' : '_CTL',
        'color' : (0.0, 0.0, 1.0)
    }
    
    new_file_path = CONFIG_PATH + 'default_data.txt'
    #save out the file in a nice human readable format
    with open(new_file_path, 'w') as outfile:
        json.dump(data, outfile, indent = 4, sort_keys = True)

    print("New file added at {0}".format(new_file_path))


def is_shift_down(*args):
    mods = cmds.getModifiers()
    if (mods & 1) > 0:
        return True
    else:
        return False

#select that is set to add if shift is held down
def modified_select(name):
    if cmds.objExists(name):
        cmds.select(name, add=is_shift_down())
    else:
        print("Warning! Object {0} does not exist, please check your configuration.".format(name))

def dynamic_button_layout(config_file):
    #load in the settings data
    settings_data = load_data_file(config_file)

    #going to make a grid for the hand controls, this is a POC but in future other layouts would be good
    cmds.gridLayout( numberOfColumns=settings_data['config']['group_count'], cellWidthHeight=(50, 50) )

    control_prefix = settings_data['config']['control_prefix']
    control_suffix = settings_data['config']['control_suffix']
    color = settings_data['config']['color']

    #formatting information would ideally be standardised across the auto rigger, still, POC
    template = control_prefix+"{0}"+control_suffix

    #used to fetch the set key
    set_key = settings_data['config']['set_key']
    control_set = settings_data[set_key]

    #add the column headers
    for item in control_set:
        cmds.text(label = item['name'], backgroundColor = COLOR_ORANGE)

    #cast to int from string in the json
    max_group_members = int(settings_data['config']['max_members'])
    #loop over these in such a way to get all the 1st, 2nd...etc  controls up to max

    for i in range(max_group_members):
        #fetch required data for the individual controls
        control_set = settings_data[set_key] #eg "fingers"


        #i know nested for loops are bad but the gridlayout wants it this way
        for group in control_set: #for each finger in the finger set

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
                cmds.text("") #empty label to take up layout slot


    #escape the grid layout 
    cmds.setParent('..')


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
    img = cmds.image(image=IMG_PATH + 'picker_icon.png')
    cmds.text( label='Control Picker', font = 'boldLabelFont')
    cmds.setParent('..')
    
    dynamic_button_layout(config_file)

    cmds.showWindow(window)

def load_config():
    config_file = cmds.textField('config_file_name', query=True, text= True)
    config_file_path = CONFIG_PATH+config_file

    if os.path.isfile(CONFIG_PATH):
            picker_ui(config_file = config_file)
    else:
        print("Warning! file : {0} does not exist, please check and try again.".format(config_file_path))


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



