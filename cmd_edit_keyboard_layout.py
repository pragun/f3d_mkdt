# Author-Pragun Goyal 
# Description-This command creates/edits an attribute saved on the 
# main design object containing a JSON object for the Keyboard-Layout
# in the same format as used/specified here http://www.keyboard-layout-editor.com/

import adsk.core, adsk.fusion, adsk.cam, traceback
import json, re
from .common_defs import *
from . import hjson
import html
# Event handler for the commandCreated event.

layout_text_box_id = 'layout_text_box_id'
unit_size_id = 'unit_size_id'
validate = 'validate_button_id'

handlers = []

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

class EditKeyboardLayoutValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        print("Validate Handler\n")
        app = adsk.core.Application.get()
        eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        inputs_valid = True 

        layout_input_text = inputs.itemById(layout_text_box_id)
        input_text = html.unescape(layout_input_text.text)
        input_lines = str.split(input_text,'\n')
        print(input_lines)

        input_text_except_last_line = ''
        if len(input_lines) > 0:
            input_text_except_last_line = '\n'.join(input_lines[0:-1])
        print(input_text_except_last_line)

        input_text_except_last_line.strip()
        if input_text_except_last_line != '':
            try:
                a = hjson.loads(input_text)
                print('Im here')
                print(a)
            except Exception as e:
                print('Or Im here')
                print(e)

        eventArgs.areInputsValid = inputs_valid
