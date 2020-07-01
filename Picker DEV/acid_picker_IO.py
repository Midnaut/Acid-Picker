#/--------------------------------------------------------------------------------////
#
#             acid_picker_IO.py 
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
# side script loaded in to habdle file operations, should not be called directly
# 

import os
import maya.cmds as cmds
import json
import webbrowser
import acid_picker

IMG_PATH = os.path.join( os.path.dirname(__file__), "img")
CONFIG_PATH = os.path.join( os.path.dirname(__file__), "config")

def load_data_file(config_file):

    config_file_path = os.path.join(CONFIG_PATH, config_file)

    print("Loading config file: {0}".format(config_file_path))
    
    try:
        with open(config_file_path) as json_file:
            data = json.load(json_file)
        return data
    except ValueError:  
        
        message_string = (
        "Error! Decoding JSON has failed.\n"+
        "Please validate your json and try again."
        )

        acid_picker.create_error_dialog(message_string)

def confirm_new_data_file(advanced = False):

    message_string = ("Warning!\n"+
    "This will overwrite any data in the default_data file if it exists!\n"
    "Are you sure you want to proceed?")

    result = cmds.confirmDialog(title='New Default Config File?',
                                icon = 'warning',
                                message=message_string,
                                button=['Yes', 'No'],
                                defaultButton='Yes',
                                cancelButton='No')
    # EXECUTE button
    if result == 'Yes':
        if advanced:
            create_advanced_example()
        else:
            create_basic_example()

def load_config():
    picker_namespace = cmds.textField('object_namespace', query=True, text= True)
    config_file = cmds.textField('config_file_name', query=True, text= True)

    print("object_namespace:"+ picker_namespace)

    config_file_path = os.path.join(CONFIG_PATH,config_file)

    if os.path.isfile(config_file_path):
        acid_picker.picker_ui(config_file = config_file, picker_namespace = picker_namespace)
    else:

        message_string = (
        "Warning! file : {0} does not exist in the config file path.\n"
        "Please check and try again."
        )

        acid_picker.create_error_dialog(message_string.format(config_file))


def get_basic_data():
    data = {}
    data['left_hand'] = {
        'name': 'Left Hand',
        'groups': [],
        'color' : (0.0, 0.0, 1.0),
        'group_count' : 5,
        'max_members' : 4,
        'control_prefix' : 'L_',
        'control_suffix' : '_CTL',
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

    #overrides example
    data['right_hand'] = {
        'template_set_name': 'left_hand',
        'overrides': ['name','color', 'control_prefix'],
        'name' : "Right Hand",
        'color' : (1.0, 0.0, 0.0),
        'control_prefix' : 'R_',
        'reverse_group_order' : True
    }

    #additional config data
    data['config'] = {
        'set_name' : 'Default Data',
        'set_keys' : ['left_hand', "right_hand"],
        'window_size' : (255,305)
    }

    return data

#used for creating a demo file that the user can modify for purpose
def create_basic_example():
    
    data = get_basic_data()
    
    new_file_path = os.path.join(CONFIG_PATH, 'default_data.json')
    #save out the file in a nice human readable format
    with open(new_file_path, 'w') as outfile:
        json.dump(data, outfile, indent = 4, sort_keys = True)

    print("New file added at {0}".format(new_file_path))

#used for creating a demo file that the user can modify for purpose
def create_advanced_example():
    data = get_basic_data()


    data['config_advanced'] = {
        'super_sets' : []
    }

    data['config_advanced']['super_sets'].append({
        'set_style' : "row",
        'name' : "Hands",
        'set_keys' : ['left_hand', 'right_hand'],
        'row_columns' : 2,
    })

    data['config']['window_size'] = (510,305)

    
    new_file_path = os.path.join(CONFIG_PATH, 'default_data.json')
    #save out the file in a nice human readable format
    with open(new_file_path, 'w') as outfile:
        json.dump(data, outfile, indent = 4, sort_keys = True)

    print("New file added at {0}".format(new_file_path))


