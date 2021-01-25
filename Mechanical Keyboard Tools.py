#Author-Pragun Goyal 
#Description-This add-in contains several useful tools to design Mechanical Keyboards

import adsk.core, adsk.fusion, adsk.cam, traceback
import json, re 
from .cmd_associate_identifier_with_component import *

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
        
        # Empty panel can't be displayed. Add a command to the panel
        cmdDef = ui.commandDefinitions.itemById('select_single_key_components')
        if cmdDef:
            cmdDef.deleteMe()
        
        cmdDef = ui.commandDefinitions.addButtonDefinition('select_single_key_components', 'Select Components for Single Key', 'Demo for new command')

        # Connect to the command created event.
        sampleCommandCreated = SelectSingleKeyComponentsCreatedEventHandler()
        cmdDef.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)
        
        tbPanel.controls.addCommand(cmdDef)

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

