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

sketch_input_id = 'sketch_input_id'
component_input_id = 'component_input_id'
output_text_id = 'output_text_id'
filter_text_id = 'filter_text_id'
keep_orientation_input_id = 'keep_orientation_id'

handlers = []

class MapComponentOverPointsCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
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
        
        sketch_input = inputs.addSelectionInput(sketch_input_id,'Select Sketch for Input Points','Select Sketch for Input Points')
        component_input = inputs.addSelectionInput(component_input_id,'Select Component for Mapping over Points','Select Component for Mapping over Points')
        filter_text_input = inputs.addTextBoxCommandInput(filter_text_id,"Filter Value",'',5,False)
        output_text_input = inputs.addTextBoxCommandInput(output_text_id,'Command Pre-Output:','',5,True)
        keep_orientation_input = inputs.addBoolValueInput(keep_orientation_input_id,'Keep Current Orientation',True,'',True)
        
        sketch_input.addSelectionFilter('Sketches')
        sketch_input.setSelectionLimits(0,1)
        
        component_input.addSelectionFilter('Occurrences')
        component_input.setSelectionLimits(0,1)
    
        onValidateInputs = MapComponentOverPointsValidateInputsHandler()
        cmd.validateInputs.add(onValidateInputs)
        handlers.append(onValidateInputs)

        onExecute = MapComponentOverPointsExecuteHandler()    
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

# Event handler for the execute event.
class MapComponentOverPointsExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("In Execute:")
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.activeComponent
        occurrences = root.occurrences

        eventArgs = adsk.core.CommandEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        output_text_input = inputs.itemById(output_text_id)
        filter_text_input = inputs.itemById(filter_text_id)
        component_input = inputs.itemById(component_input_id)
        sketch_input = inputs.itemById(sketch_input_id)
        keep_orientation_input = inputs.itemById(keep_orientation_input_id)

        keep_orientation = keep_orientation_input.value

        sketch = sketch_input.selection(0).entity
        x_direction = sketch.xDirection
        y_direction = sketch.yDirection
        z_direction = x_direction.crossProduct(y_direction)

        occurrence = component_input.selection(0).entity
        user_text = filter_text_input.text
        filter_dict = gen_filter_dict(user_text)
        print("filter dict", filter_dict)
        matched_points = get_matching_sketchpoints(sketch,filter_dict)    
        print("Matched %d points in sketch."%(len(matched_points,)))
        component = occurrence.component
        
        for matched_point in matched_points:
            rot_angle = - math.radians(get_rotation_angle_from_sketchpoint_attributes(matched_point))
            # why the minus? 
            # Its becasue the co-ordiniate system used in creating keyboard layouts
            # Y is positive going downwards
            
            placement_3d_matrix = adsk.core.Matrix3D.create()
            if keep_orientation:
                placement_3d_matrix = occurrence.transform.copy()
            
            translate_3d_vector = adsk.core.Vector3D.create(matched_point.geometry.x,matched_point.geometry.y,matched_point.geometry.z)
            placement_3d_matrix.translation = translate_3d_vector

            rotation_matrix = adsk.core.Matrix3D.create()
            rotation_matrix.setToRotation(rot_angle,z_direction,matched_point.geometry)
            placement_3d_matrix.transformBy(rotation_matrix)

            new_occurrence = occurrences.addExistingComponent(component, placement_3d_matrix)

            



def get_rotation_angle_from_sketchpoint_attributes(sketchpoint):
    r = 0
    attrib_dict = create_attrib_dict(attribute_group_name,sketchpoint)
    if 'key_data' in attrib_dict:
        key_data = attrib_dict['key_data']
        if 'r' in key_data:
            r = key_data['r']
    return r


def gen_filter_dict(text):
    return {broadcast_key:create_user_input_dict(text)}

def get_matching_sketchpoints(sketch,filter_dict):
    sketchpoints = sketch.sketchPoints
    matched_points = []
    for i in range(sketchpoints.count):
        pt = sketchpoints.item(i)
        attrib_dict = create_attrib_dict(attribute_group_name,pt)
        if attrib_dict != {} and filter_dict != {}:
            if filter_attrib_match(filter_dict, attrib_dict):
                matched_points.append(pt) 
    return  matched_points

class MapComponentOverPointsValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
        #self.already_loaded_attributes = False
        self.last_validated_user_text = ''
        self.inputs_valid = False
        self.last_selected_component = None
        #self.last_selected_entity = None

    def notify(self, args):
        print("Validate Handler\n")
        app = adsk.core.Application.get()
        eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        #inputs_valid = False
        output_text_input = inputs.itemById(output_text_id)
        filter_text_input = inputs.itemById(filter_text_id)
        component_input = inputs.itemById(component_input_id)
        sketch_input = inputs.itemById(sketch_input_id)
        keep_orientation_input = inputs.itemById(keep_orientation_input_id)

        if component_input.selectionCount > 0:
            component = component_input.selection(0).entity
            if component != self.last_selected_component:
                self.last_selected_component = component
                if hasattr(component,'attributes'):
                    attrib_dict = create_attrib_dict(attribute_group_name, component)
                    if broadcast_key in attrib_dict.keys():
                        filter_text_input.text = hjson.dumps(attrib_dict[broadcast_key])

        if sketch_input.selectionCount > 0 and component_input.selectionCount > 0:
            sketch = sketch_input.selection(0).entity
            component = component_input.selection(0).entity

            user_text = filter_text_input.text
            if user_text != self.last_validated_user_text:
                self.last_validated_user_text = user_text
                try:
                    filter_dict = gen_filter_dict(user_text)
                    output_text_input.text = "Parsed OK\n"
                    matched_points = get_matching_sketchpoints(sketch,filter_dict)    
                    output_text_input.text = "Matched %d points in sketch."%(len(matched_points,))
                    if len(matched_points) > 0:
                        self.inputs_valid = True

                except Exception as e:
                    output_text_input.text = "Error parsing: %s"%(e,)
                    print("Error parsing: %s"%(e,))
                    self.inputs_valid = False
            else:
                self.inputs_valid = self.inputs_valid
        
        else:
            self.inputs_valid = False
            self.last_validated_user_text = ''

        eventArgs.areInputsValid = self.inputs_valid

