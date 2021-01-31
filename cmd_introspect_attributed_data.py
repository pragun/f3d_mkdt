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

selection_input_id = 'selection_input_id'
attribute_text_box_id = 'attribute_text_box_id'
info_text_box_id = 'info_text_box_id'
group_name_input_id = 'group_name_box_id'
parse_results_text_box_id = 'parse_results_text_box_id'

handlers = []

class IntrospectEntityCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
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
        
        selection_input = inputs.addSelectionInput(selection_input_id,'Select Entity for Introspection:','Select Entity for Introspection:')
        selection_input.setSelectionLimits(0,1)
        group_name_input = inputs.addStringValueInput(group_name_input_id,"GroupName for Attributes",attribute_group_name)
        info_text_box_input = inputs.addTextBoxCommandInput(info_text_box_id,'Info:','',3,True)
        attribute_text_box_input = inputs.addTextBoxCommandInput(attribute_text_box_id,'Attribute Data','',6,False)
        parse_results_text_box_input = inputs.addTextBoxCommandInput(parse_results_text_box_id,"Parse Results:",'',5,True)
        #selection_input.addSelectionFilter()
    
        onValidateInputs = IntrospectEntityValidateInputsHandler()
        cmd.validateInputs.add(onValidateInputs)
        handlers.append(onValidateInputs)

        onExecute = IntrospectEntityExecuteHandler()    
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

def create_user_input_dict(user_input_text):
    html_escaped_txt = html.unescape(user_input_text)
    return hjson.loads(html_escaped_txt,object_pairs_hook=dict)

def create_attrib_dict(gp_name, selected_entity):
    attributes = selected_entity.attributes
    cnt = attributes.count
    attrib_dict = {}
    for i in range(cnt):
        attrib = attributes.item(i)
        if gp_name == attrib.groupName:
            try:
                attrib_dict[attrib.name] = hjson.loads(attrib.value)
            except Exception as e:
                attrib_dict[attrib.name] = attrib.value

    return attrib_dict

def compare_user_input_attrib_data(user_input_dict,attrib_dict):
    user_input_keys = set(user_input_dict.keys())
    attrib_keys = set(attrib_dict.keys())

    keys_to_be_updated = user_input_keys
    keys_to_be_deleted = attrib_keys - user_input_keys
    keys_unchanged = set([])

    for key in keys_to_be_updated:
        if key in attrib_dict:
            if user_input_dict[key] == attrib_dict[key]:
                keys_unchanged.add(key)

    keys_to_be_updated = keys_to_be_updated - keys_unchanged

    return (keys_unchanged, keys_to_be_updated, keys_to_be_deleted)


# Event handler for the execute event.
class IntrospectEntityExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("In Execute:")
        app = adsk.core.Application.get()
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        selection_input = inputs.itemById(selection_input_id)
        attribute_text_box_input = inputs.itemById(attribute_text_box_id)
        info_text_box_input = inputs.itemById(info_text_box_id)
        group_name_input = inputs.itemById(group_name_input_id)
        parse_results_text_box_input = inputs.itemById(parse_results_text_box_id)

        gp_name = group_name_input.value
        selected_entity = selection_input.selection(0).entity
        user_input_text = attribute_text_box_input.text

        attrib_dict = create_attrib_dict(gp_name, selected_entity)
        user_input_dict = create_user_input_dict(user_input_text)
        (keys_unchanged, keys_to_be_updated, keys_to_be_deleted) = compare_user_input_attrib_data(user_input_dict,attrib_dict)

        print('Keys: %s will be updated\n'%(keys_to_be_updated,))
        print('Keys: %s will be deleted\n'%(keys_to_be_deleted,))
        print('Keys: %s will be left as they are\n'%(keys_unchanged,))

        attributes = selected_entity.attributes

        for key in keys_to_be_updated:
            value = user_input_dict[key]
            keyed_attrib = attributes.itemByName(gp_name,key)
            if keyed_attrib is None:
                attributes.add(gp_name,key,value)

            keyed_attrib.value = value

        for key in keys_to_be_deleted:
            keyed_attrib = attributes.itemByName(gp_name,key)
            if keyed_attrib is None:
                raise Exception("Attribute for name:%s, group_name:%s not found."%(key,gp_name))

            keyed_attrib.deleteMe()

        #parse_results_text_box = inputs.itemById(parse_results_text_box_id)
        #selected_sketch = sketch_input.selection(0).entity


class IntrospectEntityValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
        self.already_loaded_attributes = False
        self.last_validated_user_text = ''
        self.inputs_valid = False
        self.last_selected_entity = None

    def notify(self, args):
        print("Validate Handler\n")
        app = adsk.core.Application.get()
        eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        #inputs_valid = False

        selection_input = inputs.itemById(selection_input_id)
        attribute_text_box_input = inputs.itemById(attribute_text_box_id)
        info_text_box_input = inputs.itemById(info_text_box_id)
        group_name_input = inputs.itemById(group_name_input_id)
        parse_results_text_box_input = inputs.itemById(parse_results_text_box_id)

        gp_name = group_name_input.value

        if selection_input.selectionCount > 0:
            selected_entity = selection_input.selection(0).entity
            if selected_entity != self.last_selected_entity:
                self.last_selected_entity = selected_entity
                self.already_loaded_attributes = False
                self.inputs_valid = False
                self.last_validated_user_text = ''

            cls_type = selected_entity.objectType 
            info_text_box_input.text = "Class Type: %s\n" % (cls_type,)

            if hasattr(selected_entity,'attributes'):
                info_text_box_input.text += 'Supports Attributes.\n'
                info_text_box_input.text += 'Has %d Attributes.\n'%(selected_entity.attributes.count,)
                attrib_dict = create_attrib_dict(gp_name, selected_entity)

                if not self.already_loaded_attributes:    
                    self.last_validated_user_text = hjson.dumps(attrib_dict)
                    attribute_text_box_input.text = self.last_validated_user_text 
                    self.already_loaded_attributes = True
                    self.inputs_valid = False
                    #Inputs are invalid because this means that 
                    #the display is the data just loaded from the model
                    #for the inputs to be valid for execution
                    #the user has to make some changes
                    
                else:
                    user_input_text = attribute_text_box_input.text
                    if user_input_text != self.last_validated_user_text:
                        try:
                            user_input_dict = create_user_input_dict(user_input_text)
                            print(user_input_dict)
                            parse_results_text_box_input.text = 'Parsed OK.\n'
                            self.inputs_valid = True

                            if user_input_dict == attrib_dict:
                                self.inputs_valid = False
                                parse_results_text_box_input.text += 'Same Input as existing attribute data.\n'
                            else:
                                (keys_unchanged, keys_to_be_updated, keys_to_be_deleted) = compare_user_input_attrib_data(user_input_dict,attrib_dict)

                                parse_results_text_box_input.text += 'Keys: %s will be updated\n'%(keys_to_be_updated,)
                                parse_results_text_box_input.text += 'Keys: %s will be deleted\n'%(keys_to_be_deleted,)
                                parse_results_text_box_input.text += 'Keys: %s will be left as they are\n'%(keys_unchanged,)

                        except Exception as e:
                            parse_results_text_box_input.text = "Error parsing: %s"%(e,)
                            print("Error parsing: %s"%(e,))
                            self.inputs_valid = False

                        self.last_validated_user_text = user_input_text

                    else:
                        self.inputs_valid = self.inputs_valid
                        #If there has been no new change to the 
                        #text, the validity of inputs continues
                        #to be the same
            else:
                info_text_box_input.text += 'Does not support Attributes\n'
                self.inputs_valid = False
                #If the selected entity doesn't support attributes,
                #how can the inputs be valid?

        else:
            self.inputs_valid = False
            #Inputs are invalid because no entity is selected

        #eventArgs.areInputsValid = inputs_valid
        eventArgs.areInputsValid = self.inputs_valid
        #prse_results_text_box = inputs.itemById(parse_results_text_box_id)
 
        #if sketch_input.selectionCount > 0 and hjson_parsed_object != None:
        #    eventArgs.areInputsValid = True
