def matching_subdictionary(subdict,superdict):
    if not (isinstance(subdict,dict) and isinstance(superdict,dict)):
        return False
    sub_keys = set(subdict.keys())
    sup_keys = set(superdict.keys())

    if len(sub_keys-sup_keys) > 0:
        return False
    
    retval = True
    for key in sub_keys:
        if isinstance(subdict[key],dict):
            retval &=  matching_subdictionary(subdict[key],superdict[key])
        else:
            retval &= subdict[key] == superdict[key]
    return retval

if __name__ == '__main__':
    a = {
        'm':1,
        'n':2,
        'j':{
            'k':1,
            'l':2,
            'p':3
        }
    }

    t = [
        {
        'm':1,
        'j':{
            'k':1,
            'l':2,
            }
        },

        {
        'm':2,
        'j':{
            'k':1,
            'l':2,
            }
        },

        {
        'm':1,
        'j':{
            'k':1,
            }
        },

        {
        'm':1,
        'j':{
            'k':2,
            }
        },
    ]

    for i in range(len(t)):
        print(t[i])
        print(matching_subdictionary(t[i],a))