# Author-Pragun Goyal 
# Description-This command creates/edits an attribute saved on the 
# main design object containing a JSON object for the Keyboard-Layout
# in the same format as used/specified here http://www.keyboard-layout-editor.com/

import adsk.core, adsk.fusion, adsk.cam, traceback
import json, re
from .common_defs import *
from . import hjson
import html
from collections import OrderedDict
from .keyboard_layout import expand_layout_list
import pprint
import math

# Event handler for the commandCreated event.

layout_text_box_id = 'layout_text_box_id'
unit_size_id = 'unit_size_id'
validate = 'validate_button_id'
parse_results_text_box_id = 'parse_results_text_box_id'
sketch_input_id = 'sketch_plane_selection_id'
use_construction_lines_id ='use_construction_lines_id'

handlers = []

def check_high_level_structure(layout_input):
    #Expectations for input: 
    #1. A List of Lists
    r = 0
    if not isinstance(layout_input,list):
        raise ValueError("Expected a list for the layout input.")
    for row in layout_input:
        r = r+1
        if not isinstance(row, list):
            raise ValueError("Expected a list of lists for the layout input.\nRow:%d"%(r,))
        i = 0
        for item in row:
            i = i+1
            if not (isinstance(item, OrderedDict) or isinstance(item, str)):
                raise ValueError("Expected either a string or a dictionary value.\nRow:%d,Item:%s"%(r,item))



def parse_layout_input(input_text, parse_results_text_box=None):
    def put_parse_msg(msg):
        print(msg)
        if parse_results_text_box is not None:
            parse_results_text_box.text = msg

    input_lines = str.split(input_text,'\n')
    #print(input_lines)

    input_text_except_last_line = ''
    if len(input_lines) > 0:
        input_text_except_last_line = '\n'.join(input_lines[0:-1])
    #print(input_text_except_last_line)

    input_text_except_last_line.strip()

    hjson_parsed_object = None
    
    if input_text_except_last_line != '':
        try:
            hjson_parsed_object = hjson.loads(input_text)
            check_high_level_structure(hjson_parsed_object)
            put_parse_msg('Parsed OK')
            #print('Parsed as:',hjson_parsed_object)
        except Exception as e:
            print("Couldn't parse as a hjson object, will try to parse as a list next..")
            print(e)
            input_text = '['+input_text+']'
            try:
                hjson_parsed_object = hjson.loads(input_text)
                check_high_level_structure(hjson_parsed_object)
                put_parse_msg('Parsed OK as list')
                #print('Parsed as:',hjson_parsed_object)
            except Exception as e:
                put_parse_msg('Exception Parsing as list: %s'%(e,))
                print(e)

    return hjson_parsed_object


class EditKeyboardLayoutCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)

        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command
        
        ui  = app.userInterface
        #ui.messageBox('In command create event handler.')
        print("Create Event Handler\n")

         # Get the CommandInputs collection to create new command inputs.            
        inputs = cmd.commandInputs
        default_u_size = adsk.core.ValueInput.createByString('19.05mm')
        unit_size_box_input  = inputs.addDistanceValueCommandInput(unit_size_id, 'Size of 1u', default_u_size)
        layout_text_box_input = inputs.addTextBoxCommandInput(layout_text_box_id,'Keyboard Layout \n(as used at http://www.keyboard-layout-editor.com/)','',15,False)
        parse_results_text_box = inputs.addTextBoxCommandInput(parse_results_text_box_id,'Parse Results:', '', 3, True)
        sketch_input = inputs.addSelectionInput(sketch_input_id,'Select Sketch to Add Generated Keyboard Layout Onto', 'Select a sketch to create a keyboard layout sketch into')
        construction_lines_input = inputs.addBoolValueInput(use_construction_lines_id,"Use Construction Lines in Sketch\n(better performance)",True,'',True)

        sketch_input.addSelectionFilter('Sketches')
        sketch_input.setSelectionLimits(0,1)


        # Connect to the execute event.
        #onActivateInputs = SelectSingleKeyComponentsActivateHandler()
        #cmd.activate.add(onActivateInputs)
        #handlers.append(onActivateInputs)

        onValidateInputs = EditKeyboardLayoutValidateInputsHandler()
        cmd.validateInputs.add(onValidateInputs)
        handlers.append(onValidateInputs)

        onExecute = EditKeyboardLayoutExecuteHandler()    
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

# Event handler for the execute event.
class EditKeyboardLayoutExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("In Execute:")
        app = adsk.core.Application.get()
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        parse_results_text_box = inputs.itemById(parse_results_text_box_id)
        layout_input_text = inputs.itemById(layout_text_box_id)
        unit_size_input = inputs.itemById(unit_size_id)
        sketch_input = inputs.itemById(sketch_input_id)
        use_construction_lines_input = inputs.itemById(use_construction_lines_id)
        use_construction_lines = use_construction_lines_input.value

        input_text = html.unescape(layout_input_text.text)
        
        unit_value = unit_size_input.value

        selected_sketch = sketch_input.selection(0).entity

        print(selected_sketch)
        parsed_layout = parse_layout_input(input_text)
        print('Parsed Layout: \n',parsed_layout)
        expanded_layout = expand_layout_list(parsed_layout)
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(expanded_layout)

        sketchPoints = selected_sketch.sketchPoints
        lines = selected_sketch.sketchCurves.sketchLines;

        for item in expanded_layout:
            angle_rad = math.radians(item['r'])
            x = unit_value * (item['rx'] + (item['x']*math.cos(angle_rad) - item['y']*math.sin(angle_rad)))
            y = unit_value * (item['ry'] + (item['y']*math.cos(angle_rad) + item['x']*math.sin(angle_rad)))

            corner_x = x
            corner_y = y

            corner_point = adsk.core.Point3D.create(x, -y, 0)
            del_x = item['w']*math.cos(angle_rad)
            del_y = item['w']*math.sin(angle_rad)

            x = x + (unit_value*del_x)
            y = y + (unit_value*del_y)

            adjacent_top_point = adsk.core.Point3D.create(x, -y, 0)

            del_x = -item['h']*math.sin(angle_rad)
            del_y = item['h']*math.cos(angle_rad)
            x = x + (unit_value*del_x)
            y = y + (unit_value*del_y)
            lower_diagonal_point = adsk.core.Point3D.create(x, -y, 0)

            center_x = (corner_x + x )/2.0
            center_y = (corner_y + y )/2.0

            center_point = adsk.core.Point3D.create(center_x,-center_y,0)
            center_sketch_point = sketchPoints.add(center_point)

            center_sketch_point.attributes.add(attribute_group_name , key_data_attrib_name, json.dumps(item))

            recLines = lines.addThreePointRectangle( corner_point,
                                adjacent_top_point,
                                lower_diagonal_point)

            

            if use_construction_lines:
                for k in range(recLines.count):
                    recLines.item(k).isConstruction = True



class EditKeyboardLayoutValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("Validate Handler\n")
        app = adsk.core.Application.get()
        eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        eventArgs.areInputsValid = False

        inputs_valid = True 
        parse_results_text_box = inputs.itemById(parse_results_text_box_id)
        layout_input_text = inputs.itemById(layout_text_box_id)
        sketch_input = inputs.itemById(sketch_input_id)
        input_text = html.unescape(layout_input_text.text)
        hjson_parsed_object = parse_layout_input(input_text,parse_results_text_box=parse_results_text_box)
 
        if sketch_input.selectionCount > 0 and hjson_parsed_object != None:
            eventArgs.areInputsValid = True
