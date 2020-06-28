# Acid-Picker

Acid picker is a Maya tool for customizable control picking.

## Installation

Download the repo and then direct add to your userSetup.py

```python
import sys

sys.path.append(Path to folder) 
import acid_picker

```

## Usage

Inside a shelf button or the script execution window

```python
acid_picker.config_loader_ui()
```

This will present the config loader
![Config Loader](https://imgur.com/smSO4QI.ong)

If you dont have the default data, you can generate it, loading the default data will present you with the picker window from the file.
![Picker](https://imgur.com/8cfl3Ef.png)

Clicking on a button will replace selection with the object, shift click will add to selection instead.

### Config File

![Config file](https://imgur.com/5bmMO5M.png)
The config file is used to determine what will be diaplayed inside the window.

when loaded, in the order described inside the file, the buttons will be loaded in and arranged in a gird based off of the groups inside the set.

A Set defines the totality of the controls : in this case, Fingers
A group inside the set will provide a comlumn inside the grid : in this case, the individual finger controls

In the order that the group is defined, it will be made a column inside the grid. as you can see the thumb has less members and the grid will accomadate for that as needed.

The most important part of the config file is your naming convention. I personally use SidePrefix_Name_TypeSuffix. The tool constructs the name of the controls to be selected by using the config Prefix + group item name + config Suffix. you can make those blank strings if you dont use that strategy of naming and just the the group names. The advantage of this is inside the provided left hand and right hand data files. through very minor changes to thew config the color, side and order of the controls can be mirrored.

group count and max members are needed again for correct layout, this will provide the width and height of the grid respectively, while this could be fetched from the file itself, the idea the tool to be as performant as possible and offloading this to config file instead of the multiple for loops required for this would be an unwanted hit, feel free to tinker with this is you like!


## License
[MIT](https://choosealicense.com/licenses/mit/)
