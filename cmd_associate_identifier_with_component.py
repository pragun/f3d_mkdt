#Author-Pragun Goyal 
#Description-This add-in contains several useful tools to design Mechanical Keyboards

import adsk.core, adsk.fusion, adsk.cam, traceback
import json, re
from .common_defs import *

handlers = []

identifier_text_ids = ['identifier_text_%d'%(i,) for i in range(number_of_key_style_identifiers)]
component_selection_ids = ['selected_component_%d'%(i,) for i in range(number_of_key_style_identifiers)]
display_text_ids = ['display_text_%d'%(i,) for i in range(number_of_key_style_identifiers)]

def split_into_list_of_identifiers(txt):
    txt_list = txt.split(',')
    txt_list = [i.strip() for i in txt_list]
    txt_list = list(filter(lambda x: x!= '', txt_list))
    return txt_list

class SelectSingleKeyComponentsValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()

    def validate_key_identifier_input(self,input,display = None):
        txt = input.value
        txt_list = split_into_list_of_identifiers(txt)
        valid = True

        for txt_fragment in txt_list:
            valid &= self.validate_key_identifier(txt_fragment)

        if valid == False:
            input.isValueError = True
            if display is not None:
                display.text = 'Invalid Syntax.'

        return valid
    
    def validate_mapping(self,identifier_txt_inputs,selected_component_inputs, display_inputs):
        #Assumes that the identifier string is a valid string
        #A single component can be associated with multiple identifiers
        #Each identifier can only be associated with a single component
        valid_mapping = True
        associated_identifiers = set([])
        for (identifier_txt_input,selected_component_input,display_input) in zip(identifier_txt_inputs,selected_component_inputs,display_inputs):
            identifiers_set = set(split_into_list_of_identifiers(identifier_txt_input.value))
            #print(identifiers_set,associated_identifiers, identifiers_set.intersection(associated_identifiers) )
            if len(identifiers_set.intersection(associated_identifiers)) == 0:
                associated_identifiers = associated_identifiers.union(identifiers_set)
            else:
                identifier_txt_input.isValueError = True
                display_input.text = 'Duplicate Identifier. Identifier has been used before'
                valid_mapping = False
        return valid_mapping

    def validate_key_identifier(self,txt):
        if(re.search('[^\w.]',txt) == None):
            return True
        else:
            return False

    def notify(self, args):
        #print("Validate Handler\n")
        app = adsk.core.Application.get()

        eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs
    
        inputs_valid = True 

        selected_component_inputs = []
        identifier_inputs_for_selected_components = []
        display_inputs_for_selected_components = []

        for i in range(number_of_key_style_identifiers):
            key_style_selected_component = inputs.itemById(component_selection_ids[i])
            key_style_identifier_text_input = inputs.itemById(identifier_text_ids[i])
            display_input = inputs.itemById(display_text_ids[i])

            if (key_style_selected_component.selectionCount > 0):
                if key_style_selected_component.selection(0) is not None:
                    #print("Input Text for id %s: %s"%(identifier_text_ids[i],key_style_identifier_text_input.value))
                    selected_component_inputs.append(key_style_selected_component)
                    identifier_inputs_for_selected_components.append(key_style_identifier_text_input)
                    display_inputs_for_selected_components.append(display_input)
                    selected_entity = key_style_selected_component.selection(0).entity
                    display_input.text = selected_entity.fullPathName
                    inputs_valid &= self.validate_key_identifier_input(key_style_identifier_text_input,display_input)
                    
            else:
                key_style_identifier_text_input.isValueError = False
                display_input.text = ''
        
        if inputs_valid:
            inputs_valid &= self.validate_mapping(identifier_inputs_for_selected_components,selected_component_inputs,display_inputs_for_selected_components)


        eventArgs.areInputsValid = inputs_valid


class SelectSingleKeyComponentsActivateHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("In command activate...")
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        cmd = eventArgs.command
        inputs = cmd.commandInputs
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        ui  = app.userInterface
        
        print("here..")
        associated_key_style_identifiers = []
        attribs = design.findAttributes(attribute_group_name, identifiers_attrib_name)

        num_pre_associated_identifier_txts = 0
        i = 0

        for attrib in attribs:
            identifier_lst = json.loads(attrib.value)
            identifier_txt = ', '.join(identifier_lst)
            print(identifier_txt)

            for identifier in identifier_lst:
                if identifier in associated_key_style_identifiers:
                    raise NameError("Duplicate Attribute found %s"%(identifier,))
                associated_key_style_identifiers.append(identifier)

            key_style_selected_component = inputs.itemById(component_selection_ids[i])
            key_style_identifier_text_input = inputs.itemById(identifier_text_ids[i])
            display_txt_input = inputs.itemById(display_text_ids[i])

            key_style_identifier_text_input.value = identifier_txt
            key_style_selected_component.addSelection(attrib.parent)
            display_txt_input.text = 'Selected Component: %s'%(attrib.parent.fullPathName)
            i += 1

        num_pre_associated_identifier_txts = i

        unassociated_identifiers = set(default_key_style_identifiers) - set(associated_key_style_identifiers)
        #print(unassociated_identifiers)

        key_style_identifier_suggestion_list = list(unassociated_identifiers)

        for i in range(num_pre_associated_identifier_txts,number_of_key_style_identifiers):
            j = i - num_pre_associated_identifier_txts
            txt = ''
            if j < len(key_style_identifier_suggestion_list):
                txt = key_style_identifier_suggestion_list[j]

            key_style_identifier_text_input = inputs.itemById(identifier_text_ids[i])
            key_style_identifier_text_input.value = txt



# Event handler for the commandCreated event.
class SelectSingleKeyComponentsCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
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

        if False:
            list_key_style_identifier_texts = []
            list_key_style_component_selection = []

            associated_key_style_identifiers = []

            attribs = design.findAttributes(attribute_group_name, identifiers_attrib_name)
            print(attribs)
            for attrib in attribs :
                identifier_lst = json.loads(attrib.value)
                print(identifier_lst)
                for identifier in identifier_lst:
                    if identifier in associated_key_style_identifiers:
                        raise NameError("Duplicate Attribute found %s"%(identifier,))
                    associated_key_style_identifiers.append(identifier)

            unassociated_identifiers = set(default_key_style_identifiers) - set(associated_key_style_identifiers)
            print(unassociated_identifiers)

            key_style_identifier_suggestion_list = list(unassociated_identifiers)

        for i in range(number_of_key_style_identifiers):
            txt = ''
            #if i < len(key_style_identifier_suggestion_list):
            #    txt = key_style_identifier_suggestion_list[i]

            key_style_identifier_text = inputs.addStringValueInput(identifier_text_ids[i],'Key Identifier', txt)
            component_selection = inputs.addSelectionInput(component_selection_ids[i],'Component for Keys with above identifier','Select a component to be inserted for the keys identified with this identifier')
            display_txt = inputs.addTextBoxCommandInput(display_text_ids[i],':','',1,True)
            display_txt.isFullWidth = True
            component_selection.addSelectionFilter('Occurrences')
            component_selection.setSelectionLimits(0,1)

        # Connect to the execute event.
        onActivateInputs = SelectSingleKeyComponentsActivateHandler()
        cmd.activate.add(onActivateInputs)
        handlers.append(onActivateInputs)

        onValidateInputs = SelectSingleKeyComponentsValidateInputsHandler()
        cmd.validateInputs.add(onValidateInputs)
        handlers.append(onValidateInputs)

        onExecute = SelectSingleKeyComponentsExecuteHandler()    
        cmd.execute.add(onExecute)
        handlers.append(onExecute)
        


# Event handler for the execute event.
class SelectSingleKeyComponentsExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("In Execute:")
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        inputs = eventArgs.firingEvent.sender.commandInputs

        selected_component_inputs = []
        identifier_inputs_for_selected_components = []

        selected_entities = []

        for i in range(number_of_key_style_identifiers):
            key_style_selected_component = inputs.itemById(component_selection_ids[i])
            key_style_identifier_text_input = inputs.itemById(identifier_text_ids[i])
            #print(key_style_selected_component.selectionCount, key_style_selected_component.id)
            if (key_style_selected_component.selectionCount > 0):
                if key_style_selected_component.selection(0) is not None:
                    selected_entities.append(key_style_selected_component.selection(0).entity)
                    identifier_inputs_for_selected_components.append(key_style_identifier_text_input)

        print("Selected components:",[i.fullPathName for i in selected_entities])

        for (selected_entity,identifier_input) in zip(selected_entities,identifier_inputs_for_selected_components):
            identifiers_json_value = json.dumps(split_into_list_of_identifiers(identifier_input.value))
            print('JSON Value',identifiers_json_value)

            attribute_obj = selected_entity.attributes
            print(attribute_obj)
            try:
                a = attribute_obj.add(attribute_group_name,identifiers_attrib_name,identifiers_json_value)
            except:
                print("Failed trying to add attribute value:%s to component:%s"%(identifiers_json_value,selected_entity.fullPathName))
            print("Added attribute value:%s, to component:%s"%(identifiers_json_value,selected_entity.fullPathName))

        # Code to react to the event.
        app = adsk.core.Application.get()
