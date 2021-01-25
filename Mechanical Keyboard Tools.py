#Author-Pragun Goyal 
#Description-This add-in contains several useful tools to design Mechanical Keyboards

import adsk.core, adsk.fusion, adsk.cam, traceback
import json, re 
from .cmd_associate_identifier_with_component import *
from .cmd_edit_keyboard_layout import *

handlers = []

tbPanel = None

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        workSpace = ui.workspaces.itemById('FusionSolidEnvironment')
        tbPanels = workSpace.toolbarPanels
        
        global tbPanel
        tbPanel = tbPanels.itemById('mechKbrdTools')
        if tbPanel:
            tbPanel.deleteMe()
        tbPanel = tbPanels.add('mechKbrdTools', 'MechKbrd Tools', 'Mechanical Keyboard', False)
        
        #Empty panel can't be displayed. Add a command to the panel
        cmdDef1 = ui.commandDefinitions.itemById('select_single_key_components')
        cmdDef2 = ui.commandDefinitions.itemById('edit_keyboard_layout')
        if cmdDef1:
            cmdDef1.deleteMe()

        if cmdDef2:
            cmdDef2.deleteMe()
        
        cmdDef1 = ui.commandDefinitions.addButtonDefinition('select_single_key_components', 'Select Components for Single Key', 'Associate components in the documen with Key-Identifiers')
        cmdDef2 = ui.commandDefinitions.addButtonDefinition('edit_keyboard_layout', 'Edit Keyboard Layout', 'Edit Keyboard Layout')

        # Connect to the command created event.
        associate_identifier_with_key_cmd_created = SelectSingleKeyComponentsCreatedEventHandler()
        cmdDef1.commandCreated.add(associate_identifier_with_key_cmd_created)
        handlers.append(associate_identifier_with_key_cmd_created)

        edit_keyboard_layout_cmd_created = EditKeyboardLayoutCreatedEventHandler()
        cmdDef2.commandCreated.add(edit_keyboard_layout_cmd_created)
        handlers.append(edit_keyboard_layout_cmd_created)
        
        tbPanel.controls.addCommand(cmdDef1)
        tbPanel.controls.addCommand(cmdDef2)

        ui.messageBox('Mechanical Keyboard Design Tools Add-In Started')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        if tbPanel:
            tbPanel.deleteMe()
        
        ui.messageBox('Stop addin')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

