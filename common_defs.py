from . import hjson
import html
#import adsk.core, adsk.fusion, adsk.cam, traceback
import json, re
from . import hjson
import html
from collections import OrderedDict
import pprint
import math
from .matching_subdictionary import matching_subdictionary

number_of_key_style_identifiers = 10
default_key_style_identifiers = ['1u', '1.25u', '1.5u', '1.75u', '2u', '2.25u', '2.5u', '2.75u', '3u']

attribute_group_name = 'mechKbrdTools'
identifiers_attrib_name = 'key_style'
key_data_attrib_name = 'key_data'

unit_size = 'keyboard_unit_size_definition'
layout = 'keyboard_layout'

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
                attrib_dict[attrib.name] = hjson.loads(attrib.value,object_pairs_hook=dict)
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

def filter_attrib_match(filter,attrib):
    return matching_subdictionary(filter,attrib)