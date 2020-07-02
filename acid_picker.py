#/--------------------------------------------------------------------------------////
#
#             acid_picker.py 
#             version 0.1, last modified 02-07-2020
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
# click : replace selection with object.
# shift + click : add object to selection.
# control + click : remove oject from selection.
# 

import os
import maya.cmds as cmds
import copy
import acid_picker_IO
import maya.mel as mel


COLOR_DARK_GRAY = (0.15,0.15,0.15)
COLOR_ORANGE = (0.87, 0.51, 0.01)


def handle_set_overrides(settings_data, set_key):
    
    control_set = settings_data[set_key]
    
    #check for template key
    if "template_set_name" in control_set:
        #fetch template set
        template_set_name = control_set['template_set_name']
        template_set = settings_data[template_set_name]
        keys_to_override = control_set['overrides']

        #copy template set, so we dont override the original
        output_control_set = copy.copy(template_set)

        #override keys
        for key in keys_to_override:
            output_control_set[key] = control_set[key]

        #reverse the group order?
        if 'reverse_group_order' in control_set:
            reverse_group_order = control_set['reverse_group_order']

            #always actually check the key first
            if reverse_group_order:
                output_control_set['groups'] = reverse_group_list(output_control_set)

        #return overriden template
        return output_control_set

    else:
        #return the fetched set
        return control_set

def reverse_group_list(control_set):
    control_list = control_set['groups']
    updated_list = []

    for control in reversed(control_list):
        updated_list.append(control)

    return updated_list

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

        message_string = (
            "Warning! Object {0} does not exist\n"+
            "Please check your configuration."
            )

        print(message_string.format(name))

def create_error_dialog(message_text):
    result = cmds.confirmDialog(title='ERROR',
                                message=message_text,
                                icon = 'critical',
                                button=['OKAY', 'HELP'],
                                defaultButton='OKAY')

    if result == "HELP":
        webbrowser.open("https://github.com/Midnaut/Acid-Picker")

def dynamic_button_layout(settings_data, picker_namespace):
    #for each key in set keys make a new tab, named after the name
    set_keys = settings_data['config']['set_keys']
    
    #make our layout objects
    form = cmds.formLayout()
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    #set padding
    cmds.formLayout(form, edit=True, 
                    attachForm=(
                        (tabs, 'top', 0),
                        (tabs, 'left', 0),
                        (tabs, 'bottom', 0),
                        (tabs, 'right', 0)
                        )
                    )

    tab_name_list = []
    tab_content_list = []

    #check for super tabs or regular tabs
    use_super_sets = False

    #check if using super set style tabs
    if ('config_advanced' in settings_data and 
        'super_sets' in settings_data['config_advanced']):
        use_super_sets = True 

    if use_super_sets:
        add_super_set_tabs(settings_data,set_keys,
                    tab_name_list,tab_content_list,
                    picker_namespace)
    else:
        add_set_tabs(settings_data,set_keys,
                    tab_name_list,tab_content_list,
                    picker_namespace)

    #make the tuple how maya wants it
    tab_label_tuple = tuple((content,name) for content, name in 
        zip(tab_content_list, tab_name_list))

    #add the contents
    cmds.tabLayout( tabs, edit=True, tabLabel=tab_label_tuple)

    #escape the layout
    cmds.setParent('..')

def add_set_tabs(settings_data, set_keys, tab_name_list,
                tab_content_list, picker_namespace):
    for key in set_keys:
       #get  the control set, with overrides applied
       control_set = handle_set_overrides(settings_data, key)

       #get the display name for the tab
       tab_name = control_set['name']
       tab_name_list.append(tab_name)

       #this created the content in the form of a grid layout
       content = add_control_grid(control_set, picker_namespace)
       tab_content_list.append(content)

def add_super_set_tabs(settings_data, set_keys, tab_name_list,
                        tab_content_list, picker_namespace):
    
    #fetch the super sets we will make the tabs out of
    super_set_list = settings_data["config_advanced"]['super_sets']

    for super_set in super_set_list:
        #fetch the subsets and size of the grid, also name
        sub_sets = super_set['set_keys']
        tab_name = super_set['name'] 
        set_style = super_set['set_style'] 

        #set up the style of the content
        if set_style == "grid":
            grid_columns = super_set['grid_columns']
            cell_size = super_set['grid_cell_size']
            #greate the parent grid layout, the sub layours will live in
            content = cmds.gridLayout( numberOfColumns=grid_columns,
                                cellWidthHeight=cell_size )

        elif set_style == "row":
            row_columns = int(super_set["row_columns"])
            content = cmds.rowLayout(numberOfColumns = row_columns)
        
        else:
            #error, no valid super set style
            message_string = (
            "Warning! Super Set : {0} does not contain a valid set_style.\n"
            "Please check and try again."
            )
            create_error_dialog(message_string.format(tab_name))

        for set_key in sub_sets: 
            #get  the control set, with overrides applied
            control_set = handle_set_overrides(settings_data, set_key)
            add_control_grid(control_set, picker_namespace)

        #escape the gird layout
        cmds.setParent('..')
        #update the tab names
        tab_name_list.append(tab_name)
        tab_content_list.append(content)




def add_control_grid(control_set, picker_namespace):
    #going to make a grid for the controls, POC, but in future other layouts possible
    grid = cmds.gridLayout( numberOfColumns=control_set['group_count'],
                            cellWidthHeight=(50, 50) )

    control_prefix = control_set['control_prefix']
    control_suffix = control_set['control_suffix']
    color = control_set['color']

    namespace_prefix = ""
    #generate namespace prefix if needed
    if picker_namespace != "":
        namespace_prefix = "{0}:".format(picker_namespace)

    #formatting information would ideally be standardised across the auto rigger
    template = control_prefix+"{0}"+control_suffix

    group_list = control_set['groups']

    #add the column headers, this will use up the iterator, will need to make a new one
    #bit messy, but used because you cant reuse an iterator again in the grid loop
    for item in group_list:
        if item['name'] != "_EMPTY_":
            cmds.text(label = item['name'], backgroundColor = COLOR_ORANGE)
        else:
            cmds.separator(style='none')

    #cast to int from string in the json
    max_group_members = int(control_set['max_members'])

    for nr in range(max_group_members):
        #i know nested for loops are bad but the gridlayout wants it this way

        for group in group_list: #for each finger in the hand set
            #get how many controls are in this group
            control_count = int(group['control_count'])
            controls = group['controls']

            #catch empties and exceeded total control counts
            if nr < control_count and controls[nr] != "_EMPTY_":
                control_name = template.format(controls[nr])
                #make the button command, holding shift will let you add to the selection
                command_text = "acid_picker.modified_select(name = '{0}{1}')"
                #make the button
                cmds.button(label = controls[nr], 
                            backgroundColor = color,
                            command = command_text.format(namespace_prefix, control_name))
            else:
                cmds.separator(style='none') #take up layout slot


    #escape the grid layout 
    cmds.setParent('..')
    #return this grid layout so it can be made into a tab
    return grid




def picker_ui(config_file = "default_data.json", picker_namespace = ""):
    #**************************************************************************
    #Close duplicates
    ui_title = 'acid_picker_main_window'

    if cmds.window(ui_title, exists=True):
        print('CLOSE duplicate window')
        cmds.deleteUI(ui_title)
    #**************************************************************************
    
    #load in the settings data
    settings_data = acid_picker_IO.load_data_file(config_file)
    window_size = settings_data['config']['window_size']

    window = cmds.window(ui_title, title="Control Picker", widthHeight=window_size)

    cmds.columnLayout(adjustableColumn=True)

    #header bar
    cmds.rowLayout(numberOfColumns = 2, adjustableColumn = 2, backgroundColor = COLOR_DARK_GRAY)
    img = cmds.image(image=os.path.join(acid_picker_IO.IMG_PATH, 'picker_icon_small.png'))
    cmds.text( label='Control Picker', font = 'boldLabelFont')
    cmds.setParent('..')
    
    dynamic_button_layout(settings_data, picker_namespace)

    cmds.showWindow(window)


def config_loader_ui():
    #**************************************************************************
    # CLOSE if exists (avoid duplicates)
    ui_title = 'acid_picker_config_loader'

    if cmds.window(ui_title, exists=True):
        print('CLOSE duplicate window')
        cmds.deleteUI(ui_title)
    #**************************************************************************

    window = cmds.window(ui_title, title="Config Loader", widthHeight=(400, 80))

    column_name = "all_content"

    cmds.columnLayout(column_name, adjustableColumn=True)
    
    #for addressing the controls across files
    row_title = "example_row"
    cmds.rowLayout(row_title, 
                numberOfColumns = 3)

    cmds.text(label = "Examples", width = 75)
    cmds.button(label="Basic",
                command="acid_picker_IO.confirm_new_data_file()",
                backgroundColor = COLOR_ORANGE)
    cmds.button(label="Advanced",
                command="acid_picker_IO.confirm_new_data_file(advanced=True)",
                backgroundColor = COLOR_ORANGE)
    cmds.setParent("..")


    row_title = "namespace_row"
    cmds.rowLayout(row_title, 
                numberOfColumns = 3, 
                adjustableColumn = 2)

    cmds.text(label = "Namespace", width = 75)
    cmds.textField('object_namespace')
    cmds.button(label = "Namespaces",
                width = 102,
                command= "mel.eval('NamespaceEditor')",
                backgroundColor = COLOR_ORANGE)
    cmds.setParent('..')


    row_title = "file_open_row"
    cmds.rowLayout(row_title, 
                numberOfColumns = 4,
                adjustableColumn = 2)

    cmds.text(label = "File Name", width = 75)
    cmds.textField('config_file_name')
    cmds.button(label = "Browse",
                command= "acid_picker_IO.browse_files()",
                backgroundColor = COLOR_ORANGE)
    cmds.button(label = "Load",
                command= "acid_picker_IO.load_config()",
                backgroundColor = COLOR_ORANGE)
    cmds.setParent('..')

    cmds.showWindow(window)



