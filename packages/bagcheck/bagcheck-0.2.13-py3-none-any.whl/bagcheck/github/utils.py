import requests
import os
import sys
import logging
import yaml
from bagcheck.github.constants import *

cache = {}

def get_local(log: logging.Logger, path: str) -> tuple:
    log.debug(f'Getting local action at path {path}')
    if not path.endswith('.yaml') and not path.endswith('.yml'):
        for extension in ['yaml', 'yml']:
            try_path = f'{path}/action.{extension}'
            if not os.path.exists(try_path):
                log.debug(f'Test local path {try_path} does not exist')
                continue
            if try_path in cache:
                return cache[try_path]['name'], cache[try_path]['doc']
            with open(try_path, 'r', encoding='utf-8') as action_file:
                doc = yaml.safe_load(action_file)
                name = doc['name']
            cache[try_path] = {"name": name, "doc": doc}
            return name, doc
        log.fatal(f'No action file exists in local path {path}')
    if path in cache:
        return cache[path]['name'], cache[path]['doc']
    with open(path, 'r', encoding='utf-8') as action_file:
        doc = yaml.safe_load(action_file)
        name = doc['name']
    cache[path] = {"name": name, "doc": doc}
    return name, doc

def get_remote(log: logging.Logger, path: str) -> tuple:
    if path in cache:
        return cache[path]['name'], cache[path]['doc']
    url, ref = path.split('@')
    url_parts = url.split('/')
    url_path = ''
    org = url_parts[0]
    repo = url_parts[1]
    if len(url_parts) > 2:
        url_path = '/'.join(url_parts[2:])
    token = os.getenv('BAGCHECK_GITHUB_TOKEN', '')
    headers = {}
    if token:
        headers = {'Authorization': f'token {token}'}
    for ref_type in ['tags', 'heads']:
        if url_path.endswith('.yml') or url_path.endswith('.yaml'):
            req = requests.get(f'https://raw.githubusercontent.com/{org}/{repo}/refs/{ref_type}/{ref}/{url_path}', headers=headers)
            if req.status_code == 200:
                break
        else:
            url_path += '/'
            for extension in ['yaml', 'yml']:
                req = requests.get(f'https://raw.githubusercontent.com/{org}/{repo}/refs/{ref_type}/{ref}/{url_path}action.{extension}', headers=headers)
                if req.status_code == 200:
                    break
        if req.status_code == 200:
            break
    if req.status_code > 200:
        log.error(f'Could not get remote: {req.status_code}')
        sys.exit(1)

    contents = req.content.decode('utf-8')
    doc = yaml.safe_load(contents)
    name = doc['name']
    cache[path] = {"name": name, "doc": doc}
    return name, doc

def check_log(log: logging.Logger, message: str, level: str, indent: int) -> None:
    if level == LEVEL_WARN:
        log.warning(f'{" " * indent}{message}', extra={"markup": True})
    elif level == LEVEL_ERROR:
        log.error(f'{" " * indent}{message}', extra={"markup": True})
