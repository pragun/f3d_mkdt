# Author-Pragun Goyal 
# Description-This command creates/edits an attribute saved on the 
# main design object containing a JSON object for the Keyboard-Layout
# in the same format as used/specified here http://www.keyboard-layout-editor.com/

from collections import OrderedDict

class KeyParameters(object):
    def __init__(self):
        self.keys = ['rx','ry','r','x','y','w','h']
        for key in self.keys:
            setattr(self,key,0)

        self.w = 1
        self.h = 1

    def reset_for_new_row(self):
        self.y += 1
        self.x = 0
        self.w = 1
        self.h = 1

    def check_add(self,key,i_dict):
        if key in i_dict:
            value = getattr(self,key) + i_dict[key]
            setattr(self,key,value)

    def check_set(self,key,i_dict):
        if key in i_dict:
            setattr(self,key,i_dict[key])

    def process_input(self,i_dict):
        for i in ['rx','ry','r']:
            if i in i_dict:
                self.y = 0
                
        for i in ['x','y']:
            self.check_add(i, i_dict)
                
        for i in ['rx','ry','r','w','h']:
            self.check_set(i,i_dict)
            
    
    def generate_key_here(self,name):
        o_dict = {}
        for key in self.keys:
            o_dict[key] = getattr(self,key)       
        o_dict['id'] = str(name)

        self.x += self.w
        self.w = 1
        self.h = 1
        
        return o_dict
 

def expand_layout_list(rows):
    key_params = KeyParameters()
    keys = []

    for row in rows:
        for item in row:
            if isinstance(item,OrderedDict):
                key_params.process_input(item)
            else:
                keys.append(key_params.generate_key_here(item))

        key_params.reset_for_new_row()
    
    return keys
