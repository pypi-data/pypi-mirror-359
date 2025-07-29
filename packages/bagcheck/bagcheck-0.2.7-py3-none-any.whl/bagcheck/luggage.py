import os
import yaml

def load_bagcheck_file() -> dict:
    global disable_global
    global disable_local

    home_dir = os.path.expanduser('~')

    bagcheck_config = {
        'config': {
            "ref_regex": "v[0-9](\.[0-9]){0,2}"
        },
        'disable': {
            'global': [],
            'local': []
        },
        'warn': {
            'global': [],
            'local': []
        }
    }

    global_bagcheck_config = {}
    if os.path.exists(f'{home_dir}/.bagcheck'):
        with open(f'{home_dir}/.bagcheck') as bagcheck_file:
            global_bagcheck_config = yaml.safe_load(bagcheck_file)
        
    local_bagcheck_config = {}
    if os.path.exists(f'.bagcheck'):
        with open(f'.bagcheck') as bagcheck_file:
            local_bagcheck_config = yaml.safe_load(bagcheck_file)

    for key, val in global_bagcheck_config.get('config', {}):
        bagcheck_config[key] = val
    for key, val in local_bagcheck_config.get('config', {}):
        bagcheck_config[key] = val

    keys = ['disable', 'warn']

    for key in keys:
        if key in global_bagcheck_config:
            if 'global' in global_bagcheck_config[key]:
                bagcheck_config[key]['global'] = global_bagcheck_config[key]['global']
            if 'local' in global_bagcheck_config[key]:
                bagcheck_config[key]['local'] = global_bagcheck_config[key]['local']

        if key in local_bagcheck_config:
            if 'global' in local_bagcheck_config[key]:
                bagcheck_config[key]['global'] += local_bagcheck_config[key]['global']
                bagcheck_config[key]['global'] = list(set(bagcheck_config[key]['global']))
            if 'local' in local_bagcheck_config[key]:
                for local_ignore in local_bagcheck_config[key]['local']:
                    path_exists = False
                    for idx, current_local_ignore in enumerate(bagcheck_config[key]['local']):
                        if local_ignore['path'] == current_local_ignore['path']:
                            bagcheck_config[key]['local'][idx]['tests'] += local_ignore['test']
                            bagcheck_config[key]['local'][idx]['tests'] = list(set(bagcheck_config[key]['local'][idx]['tests']))
                            path_exists = True
                            break
                    if not path_exists:
                        bagcheck_config[key]['local'].append(local_ignore)

    return bagcheck_config
