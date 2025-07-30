import os
import requests
import sys
import yaml
import logging
from bagcheck.github.constants import *
from bagcheck.github.utils import *
from rich.console import Console
from bagcheck.utils import check_luggage

console = Console()

def build_tree(log: logging.Logger, path: str, indent: int=4, max_depth: int=-1):
    if not os.path.exists(path):
        log.fatal(f"File does not exist: {path}")
        exit(1)
    with open(path, 'r', encoding='utf-8') as gh_file:
        docs = yaml.load_all(gh_file, yaml.FullLoader)
    
        for doc in docs:
            if 'jobs' in doc:
                with console.status(f"[bold green]Gathering workflow `{doc['name']}`...") as status:
                    root = Workflow(log, doc=doc, indent=indent, max_depth=max_depth)
                console.print(f'[bold green]Done!')
            else:
                with console.status(f"[bold green]Gathering action `{doc['name']}`...") as status:
                    root = Action(log, doc=doc, indent=indent, max_depth=max_depth)
                console.print(f'[bold green]Done!')

            yield root

class Workflow:
    def __init__(self, log: logging.Logger, ident: str="", path: str="", doc: dict=None, args: dict=None, indent: int=4, max_depth: int=-1):
        log.debug(f'Loading workflow {path}')
        log.debug(args)
        log.debug(doc)
        self.log = log
        self.indent = indent
        self.max_depth = max_depth

        if not doc:
            doc = {}
        if not args:
            args = {}
        self.kind = GH_KIND_WORKFLOW
        self.path = path
        self.with_args = args
        if doc:
            log.debug('Getting workflow from provided doc')
            self.doc = doc
            self.name = doc['name']
        else:
            log.debug(f'Getting workflow from path {path}')
            self.path = path
            if self.path.startswith('./'):
                self.name, self.doc = get_local(log, path)
            else:
                self.name, self.doc = get_remote(log, path)
        self.ident = ident
        if not ident:
            self.ident = self.name.lower().replace(" ", '_')
        self.triggers = self.doc.get(True, {}).get('workflow_call', self.doc.get(True, {}).get('workflow_dispatch', {}))
        if not self.triggers:
            self.triggers = {}
        self.inputs = self.triggers.get('inputs', {})
        self.secret_args = self.triggers.get('secrets', {})
        self.outputs = self.triggers.get('outputs', {})
        
        self.if_statement = ''

        self.children = self.__load_children__()
        self.output_refs = self.__get_output_refs__()
        self.needs_refs = self.__get_need_refs__()
        self.input_refs = self.__get_input_refs__()

        self.doc['name'] = self.name

    def __get_output_refs__(self) -> list:
        outputs = []

        for output, val in self.outputs.items():
            for key, val in re.findall(GH_JOB_OUTPUTS_PATTERN, val['value']):
                outputs.append((key, val))
        return list(set(outputs))
    
    def __get_need_refs__(self) -> list:
        return []
    
    def __get_input_refs__(self) -> list:
        return []
    
    def __load_children__(self) -> list:
        out = []
        for job_id, job in self.doc.get('jobs', {}).items():
            out.append(Job(self.log, job_id, job, indent=self.indent, max_depth=self.max_depth))
        return out

    def get_summary(self) -> dict:
        children = []
        for child in self.children:
            children.append(child.get_summary())
        return {'name': self.name, 'kind': self.kind, 'children': children, 'triggers': self.triggers}

    def get_outputs(self) -> list:
        return list(self.outputs.keys())

    def check_outputs(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking workflow [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        check_map = {}
        for key, val in self.output_refs:
            if not key in check_map:
                check_map[key] = [val]
                continue
            check_map[key].append(val)
        for child in self.children:
            for k, v in child.output_refs:
                if not k in check_map:
                    check_map[k] = [v]
                    continue
                check_map[k].append(v)
        for k, v in check_map.items():
            check_map[k] = list(set(v))
        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_OUTPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_OUTPUT_WIRING):
                    local_level = LEVEL_WARN
                if child.ident in check_map:
                    for item in check_map[child.ident]:
                        if not item in child.outputs:
                            check_log(self.log, f'[cyan]{child.ident}[/cyan] does not output `{item}`', local_level, self.indent)
                            issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_outputs(local_level, ignore, warn, depth=depth+1)
        
        return issue_count
    
    def check_needs(self, level: str, ignore: dict, warn: dict, available_outputs: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking workflow [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        available_outputs = {}

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                available_outputs[child.ident] = list(child.outputs.keys())
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_NEEDS_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_NEEDS_WIRING):
                    local_level = LEVEL_WARN
                issue_count += child.check_needs(local_level, ignore, warn, available_outputs, depth=depth+1)
        
        return issue_count
    
    def check_inputs(self, level: str, ignore: dict, warn: dict, parent_inputs: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking workflow [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_INPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_INPUT_WIRING):
                    local_level = LEVEL_WARN
                for ip in child.input_refs:
                    if not ip in self.inputs:
                        check_log(self.log, f'[cyan]{child.ident}[/cyan] input `{ip}` is not present', local_level, self.indent*depth)
                        issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_inputs(local_level, ignore, warn, self.inputs, depth=depth+1)
        
        return issue_count
    
    def check_timeout(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking workflow [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if check_luggage(self.doc, ignore, GH_CHECK_TIMEOUT):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_TIMEOUT):
                    local_level = LEVEL_WARN
                issue_count += child.check_timeout(local_level, ignore, warn, depth=depth+1)

        return issue_count
    
    def check_runs_on(self, level, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking workflow [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if check_luggage(self.doc, ignore, GH_CHECK_RUNS_ON):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_RUNS_ON):
                    local_level = LEVEL_WARN
                issue_count += child.check_runs_on(local_level, ignore, warn, depth=depth+1)

        return issue_count

    def check_workflow_calls(self, level, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking workflow [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if check_luggage(self.doc, ignore, GH_CHECK_WORKFLOW_CALLS):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_WORKFLOW_CALLS):
                    local_level = LEVEL_WARN
                issue_count += child.check_workflow_calls(local_level, ignore, warn, depth=depth+1)

        return issue_count
    
    def check_action_calls(self, level, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking workflow [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if check_luggage(self.doc, ignore, GH_CHECK_ACTION_CALLS):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_ACTION_CALLS):
                    local_level = LEVEL_WARN
                issue_count += child.check_action_calls(local_level,  ignore, warn, depth=depth+1)

        return issue_count
    
    def check_input_calls(self, level, indent, ignore: dict, warn: dict, depth: int=0) -> int:
        return 0
    
    def check_refs(self, level: str, ignore: dict, warn: dict, ref_regex: str, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking step [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_REF):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_REF):
                    local_level = LEVEL_WARN
                issue_count += child.check_refs(local_level, ignore, warn, ref_regex, depth)
        
        return issue_count

class Job:
    def __init__(self, log: logging.Logger, ident: str, doc: dict, indent: int=4, max_depth: int=-1):
        log.debug(f'Loading job {ident}')
        log.debug(doc)
        self.log = log
        self.indent = indent
        self.max_depth = max_depth

        self.kind = GH_KIND_JOB
        self.doc = doc
        self.ident = ident
        self.name = doc.get('name', ident)
        self.runs_on = doc.get('runs-on', '')
        self.timeout = doc.get('timeout-minutes', '')
        self.uses = doc.get('uses', '')
        self.secret_args = doc.get('secrets', {})
        self.with_args = doc.get('with', {})
        self.if_statement = doc.get('if', "")
        self.outputs = doc.get('outputs', {})
        self.needs = doc.get('needs', [])
        
        self.children = self.__load_children__()
        self.output_refs = self.__get_output_refs__()
        self.needs_refs = self.__get_need_refs__()
        self.input_refs = self.__get_input_refs__()

        self.doc['id'] = ident
        self.doc['name'] = self.name

    def __get_output_refs__(self) -> list:
        outputs = []

        for key, val in re.findall(GH_STEP_OUTPUTS_PATTERN, self.if_statement):
            outputs.append((key, val))
        for output, val in self.outputs.items():
            for key, val in re.findall(GH_STEP_OUTPUTS_PATTERN, val):
                outputs.append((key, val))
        return list(set(outputs))
    
    def __get_need_refs__(self) -> list:
        needs = []

        for need, val in self.outputs.items():
            for key, val in re.findall(GH_NEEDS_PATTERN, val):
                needs.append((key, val))
        for arg, val in self.with_args.items():
            for k, v in re.findall(GH_NEEDS_PATTERN, str(val)):
                needs.append((k, str(v)))
        if self.secret_args != 'inherit':
            for arg, val in self.secret_args.items():
                for k, v in re.findall(GH_NEEDS_PATTERN, str(val)):
                    needs.append((k, v))

        return list(set(needs))
    
    def __get_input_refs__(self) -> list:
        inputs = []

        for input, val in self.outputs.items():
            for key in re.findall(GH_INPUTS_PATTERN, val):
                inputs.append(key)
        for arg, val in self.with_args.items():
            for k in re.findall(GH_INPUTS_PATTERN, str(val)):
                inputs.append(k)
        if self.secret_args != 'inherit':
            for arg, val in self.secret_args.items():
                for k in re.findall(GH_INPUTS_PATTERN, str(val)):
                    inputs.append(k)

        return list(set(inputs))   

    def __load_children__(self) -> list:
        if self.uses:
            return [Workflow(self.log, ident=self.ident, path=self.uses, args=self.with_args, indent=self.indent, max_depth=self.max_depth)]
        out = []
        for idx, step in enumerate(self.doc.get('steps', [])):
            out.append(Step(self.log, idx, step, indent=self.indent, max_depth=self.max_depth))
        return out

    def get_summary(self) -> dict:
        children = []
        for child in self.children:
            children.append(child.get_summary())
        return {'name': self.name, 'kind': self.kind, 'children': children, 'triggers': {}}
    
    def get_outputs(self) -> list:
        outputs = list(self.outputs.keys())
        if self.children:
            if self.children[0].kind == GH_KIND_WORKFLOW:
                outputs += self.children[0].get_outputs()
        return outputs
    
    def check_outputs(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        check_map = {}
        for key, val in self.output_refs:
            if not key in check_map:
                check_map[key] = [val]
                continue
            check_map[key].append(val)
        for child in self.children:
            for k, v in child.output_refs:
                if not k in check_map:
                    check_map[k] = [v]
                    continue
                check_map[k].append(v)
        for k, v in check_map.items():
            check_map[k] = list(set(v))
        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_OUTPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_OUTPUT_WIRING):
                    local_level = LEVEL_WARN
                if child.ident in check_map:
                    for item in check_map[child.ident]:
                        if not item in child.outputs:
                            check_log(self.log, f'[cyan]{child.ident}[/cyan] does not output `{item}`', local_level, self.indent * (depth + 1))
                            issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_outputs(local_level, ignore, warn, depth=depth+1)
        
        return issue_count
    
    def check_needs(self, level: str, ignore: dict, warn: dict, available_outputs: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_NEEDS_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_NEEDS_WIRING):
                    local_level = LEVEL_WARN
                for j, v in child.needs_refs:
                    if not j in self.needs:
                        check_log(self.log, f'[cyan]{child.ident}[/cyan] does not define a needed job `{j}`', local_level, self.indent * depth)
                        issue_count += int(local_level == LEVEL_ERROR)
                        continue
                    if not v in available_outputs[j]:
                        check_log(self.log, f'[cyan]{child.ident}[/cyan] needed job `{j}` does not output value `{v}`', local_level, self.indent * depth)
                        issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_needs(local_level, ignore, warn, {}, depth=depth+1)
        
        return issue_count

    def check_inputs(self, level: str, ignore: dict, warn: dict, parent_inputs: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_INPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_INPUT_WIRING):
                    local_level = LEVEL_WARN
                for ip in child.input_refs:
                    if not ip in parent_inputs:
                        check_log(self.log, f'[cyan]{child.ident}[/cyan] input `{ip}` is not present', local_level, self.indent * (depth + 1))
                        issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_inputs(local_level, ignore, warn, parent_inputs, depth=depth+1)
        
        return issue_count
    
    def check_timeout(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        if self.timeout:
            return 0
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if child.kind != GH_KIND_WORKFLOW:
                    check_log(self.log, f'Job [cyan]{self.ident}[/cyan] has no `timeout-minutes` field set', level, self.indent * (depth + 1))
                    return int(level == LEVEL_ERROR)
                if check_luggage(self.doc, ignore, GH_CHECK_TIMEOUT):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_TIMEOUT):
                    local_level = LEVEL_WARN
                issue_count += child.check_timeout(local_level, ignore, warn, depth=depth+1)

        return issue_count
    
    def check_runs_on(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        if self.runs_on:
            return 0
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if child.kind != GH_KIND_WORKFLOW:
                    check_log(self.log, f'Job [cyan]{self.ident}[/cyan] has no `runs-on` field set', level, self.indent * (depth + 1))
                    return int(level == LEVEL_ERROR)
                if check_luggage(self.doc, ignore, GH_CHECK_RUNS_ON):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_RUNS_ON):
                    local_level = LEVEL_WARN
                issue_count += child.check_runs_on(local_level, ignore, warn, depth=depth+1)
        return issue_count
    
    def check_workflow_calls(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if child.kind == GH_KIND_WORKFLOW:
                    local_level = level
                    if check_luggage(self.doc, ignore, GH_CHECK_WORKFLOW_CALLS):
                        self.log.debug(f'Skipping {child.name}')
                        continue
                    if check_luggage(self.doc, warn, GH_CHECK_WORKFLOW_CALLS):
                        local_level = LEVEL_WARN
                    for field, args in child.inputs.items():
                        if args.get('required', False) and not field in self.with_args:
                            check_log(self.log, f'Job [cyan]{self.ident}[/cyan] is missing required workflow argument `{field}`', local_level, self.indent * (depth + 1))
                            issue_count += int(local_level == LEVEL_ERROR)
                    if self.secret_args == 'inherit':
                        continue
                    for field, args in child.secret_args.items():
                        if self.secret_args != 'inherit' and args.get('required', False) and not field in self.secret_args:
                            check_log(self.log, f'Job [cyan]{self.ident}[/cyan] is missing required workflow secret `{field}`', local_level, self.indent * (depth + 1))
                            issue_count += int(local_level == LEVEL_ERROR)

                    issue_count += child.check_runs_on(local_level, ignore, warn, depth=depth+1)
            
        return issue_count
    
    def check_action_calls(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if check_luggage(self.doc, ignore, GH_CHECK_ACTION_CALLS):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_ACTION_CALLS):
                    local_level = LEVEL_WARN
                issue_count += child.check_action_calls(local_level, ignore, warn, depth=depth+1)

        return issue_count
    
    def check_refs(self, level: str, ignore: dict, warn: dict, ref_regex: str, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking job [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_REF):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_REF):
                    local_level = LEVEL_WARN
                if self.uses and "@" in self.uses:
                    ref = self.uses.split('@')[1]
                    if not re.match(ref_regex, ref):
                        check_log(self.log, f'Job [cyan]{self.ident}[/cyan] references an invalid ref `{ref}`', local_level, self.indent * (depth + 1))
                        issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_refs(local_level, ignore, warn, ref_regex, depth=depth+1)
        
        return issue_count

class Step:
    def __init__(self, log: logging.Logger, idx: int=0, doc: dict=None, indent: int=4, max_depth: int=-1):
        log.debug(f'loading step {idx}')
        log.debug(doc)
        self.log = log
        self.indent = indent
        self.max_depth = max_depth

        if not doc:
            doc = {}
        self.kind = GH_KIND_STEP
        self.doc = doc
        self.name = doc.get('name', doc.get('id', f'<step {idx}>'))
        self.ident = doc.get('id', self.name.lower().replace(' ', '_'))
        self.if_statement = doc.get('if', "")
        self.run = doc.get('run', "")
        self.uses = doc.get('uses', '')
        self.with_args = doc.get('with', {})
        self.secret_args = doc.get('secrets', {})
        self.uses = doc.get('uses', '')
        self.outputs = []
        for key in re.findall(f'echo "(\S*)=.*"\s*>>\s*\$GITHUB_OUTPUT', self.run):
            self.outputs.append(key)

        self.children = self.__load_children__()
        self.output_refs = self.__get_output_refs__()
        self.needs_refs = self.__get_need_refs__()
        self.input_refs = self.__get_input_refs__()
        
        self.doc['id'] = self.ident
        self.doc['name'] = self.name
    
    def __get_output_refs__(self) -> list:
        outputs = []

        for key, val in re.findall(GH_STEP_OUTPUTS_PATTERN, self.if_statement):
            outputs.append((key, val))
        for key, val in re.findall(GH_STEP_OUTPUTS_PATTERN, self.run):
            outputs.append((key, val))
        for arg, val in self.with_args.items():
            for k, v in re.findall(GH_STEP_OUTPUTS_PATTERN, str(val)):
                outputs.append((k, str(v)))
        if self.secret_args != 'inherit':
            for arg, val in self.secret_args.items():
                for k, v in re.findall(GH_STEP_OUTPUTS_PATTERN, str(val)):
                    outputs.append((k, v))
        for child in self.children:
            for key in child.outputs:
                self.outputs.append(key)
        for key in re.findall(GH_RUN_OUTPUTS_PATTERN, self.run):
            self.outputs.append(key)

        return list(set(outputs))
    
    def __get_need_refs__(self) -> list:
        needs = []

        for key, val in re.findall(GH_NEEDS_PATTERN, self.if_statement):
            needs.append((key, val))
        for key, val in re.findall(GH_NEEDS_PATTERN, self.run):
            needs.append((key, val))
        for arg, val in self.with_args.items():
            for k, v in re.findall(GH_NEEDS_PATTERN, str(val)):
                needs.append((k, str(v)))
        if self.secret_args != 'inherit':
            for arg, val in self.secret_args.items():
                for k, v in re.findall(GH_NEEDS_PATTERN, str(val)):
                    needs.append((k, v))
        return list(set(needs))
    
    def __get_input_refs__(self) -> list:
        inputs = []

        for key in re.findall(GH_INPUTS_PATTERN, self.if_statement):
            inputs.append(key)
        for key in re.findall(GH_INPUTS_PATTERN, self.run):
            inputs.append(key)
        for arg, val in self.with_args.items():
            for k in re.findall(GH_INPUTS_PATTERN, str(val)):
                inputs.append(k)
        if self.secret_args != 'inherit':
            for arg, val in self.secret_args.items():
                for k in re.findall(GH_INPUTS_PATTERN, str(val)):
                    inputs.append(k)
        return list(set(inputs))
    
    def __load_children__(self) -> list:
        if self.uses:
            return [Action(self.log, path=self.uses, args=self.with_args, secret_with_args=self.secret_args, name=self.name, ident=self.ident, indent=self.indent, max_depth=self.max_depth)]
        return []

    def get_summary(self) -> dict:
        children = []
        for child in self.children:
            children.append(child.get_summary())
        return {'name': self.name, 'kind': self.kind, 'children': children, 'triggers': {}}
    
    def check_outputs(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking step [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        check_map = {}
        for key, val in self.output_refs:
            if not key in check_map:
                check_map[key] = [val]
                continue
            check_map[key].append(val)
        for child in self.children:
            for k, v in child.output_refs:
                if not k in check_map:
                    check_map[k] = [v]
                    continue
                check_map[k].append(v)
        for k, v in check_map.items():
            check_map[k] = list(set(v))
        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_OUTPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_OUTPUT_WIRING):
                    local_level = LEVEL_WARN
                if child.ident in check_map:
                    for item in check_map[child.ident]:
                        if not item in child.outputs:
                            check_log(self.log, f'[cyan]{child.ident}[/cyan] does not output `{item}`', local_level, self.indent * (depth + 1))
                            issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_outputs(local_level, ignore, warn, depth=depth+1)
        
        return issue_count
    
    def check_needs(self, level: str, ignore: dict, warn: dict, available_outputs: dict, depth: int=0) -> int:
        return 0
    
    def check_inputs(self, level: str, ignore: dict, warn: dict, parent_inputs: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking step [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_INPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_INPUT_WIRING):
                    local_level = LEVEL_WARN
                issue_count += child.check_inputs(local_level, ignore, warn, parent_inputs, depth=depth+1)
        
        return issue_count
    
    def check_action_calls(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking step [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if child.kind == GH_KIND_ACTION:
                    local_level = level
                    if check_luggage(self.doc, ignore, GH_CHECK_ACTION_CALLS):
                        self.log.debug(f'Skipping {child.name}')
                        continue
                    if check_luggage(self.doc, warn, GH_CHECK_ACTION_CALLS):
                        local_level = LEVEL_WARN
                    

                    issue_count += child.check_action_calls(local_level, ignore, warn, depth=depth+1)
            
        return issue_count

    def check_refs(self, level: str, ignore: dict, warn: dict, ref_regex: str, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking step [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_REF):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_REF):
                    local_level = LEVEL_WARN
                issue_count += child.check_refs(local_level, ignore, warn, ref_regex, depth=depth+1)
        
        return issue_count

class Action:
    def __init__(self, log: logging.Logger, path: str="", doc: dict=None, args: dict=None, secret_with_args: dict=None, name: str='', ident: str='', if_statement: str='', indent: int=4, max_depth: int=-1):
        log.debug(f'loading action {path}')
        log.debug(args)
        log.debug(doc)
        self.log = log
        self.indent = indent
        self.max_depth = max_depth

        if not doc:
            doc = {}
        if not args:
            args = {}
        if not secret_with_args:
            secret_with_args = {}
        self.kind = GH_KIND_ACTION
        self.path = path
        self.with_args = args
        self.secret_with_args = secret_with_args
        if doc:
            log.debug('Getting action from provided doc')
            self.doc = doc
            self.name = doc['name']
        else:
            log.debug(f'Getting action from path {path}')
            self.path = path
            if self.path.startswith('./'):
                self.name, self.doc = get_local(log, path)
            else:
                self.name, self.doc = get_remote(log, path)
        self.ident = doc.get('id', self.name.replace(' ', '_'))
        if name:
            self.name = name
        if ident:
            self.ident = ident
        self.inputs = self.doc.get('inputs', {})
        self.outputs = self.doc.get('outputs', {})
        self.secret_args = self.doc.get('secrets', {})
        self.if_statement = if_statement

        self.children = self.__load_children__()
        self.output_refs = self.__get_output_refs__()
        self.needs_refs = self.__get_need_refs__()
        self.input_refs = self.__get_input_refs__()

        self.doc['name'] = self.name

    def __get_output_refs__(self) -> list:
        outputs = []

        for key, val in self.outputs.items():
            for key, val in re.findall(GH_STEP_OUTPUTS_PATTERN, val.get('value', '')):
                outputs.append((key, val))
        return list(set(outputs))

    def __get_need_refs__(self) -> list:
        return []
    
    def __get_input_refs__(self) -> list:
        return []
    
    def __load_children__(self) -> list:
        if not 'runs' in self.doc:
            self.log.warning(f"Action {self.ident} located at {self.path} is invalid, missing 'runs' field")
            return []
        out = []
        for idx, step in enumerate(self.doc['runs'].get('steps', [])):
            if 'uses' in step:
                out.append(Action(self.log, path=step['uses'], args=step.get('with', {}), secret_with_args=step.get('secrets', {}), name=step.get('name', ''), ident=step.get('id', ''), indent=self.indent, max_depth=self.max_depth))
                continue
            out.append(Step(self.log, idx, step, indent=self.indent, max_depth=self.max_depth))
        return out

    def get_summary(self) -> dict:
        children = []
        for child in self.children:
            children.append(child.get_summary())
        return {'name': self.name, 'kind': self.kind, 'children': children, 'triggers': {}}

    def check_outputs(self, level: str, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking action [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        check_map = {}
        for key, val in self.output_refs:
            if not key in check_map:
                check_map[key] = [val]
                continue
            check_map[key].append(val)
        for child in self.children:
            for k, v in child.output_refs:
                if not k in check_map:
                    check_map[k] = [v]
                    continue
                check_map[k].append(v)
        for k, v in check_map.items():
            check_map[k] = list(set(v))
        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_OUTPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_OUTPUT_WIRING):
                    local_level = LEVEL_WARN
                issue_count += child.check_outputs(local_level, ignore, warn, depth=depth+1)
                if child.ident in check_map:
                    for item in check_map[child.ident]:
                        if not item in child.outputs:
                            check_log(self.log, f'[cyan]{child.ident}[/cyan] does not output `{item}`', local_level, self.indent * (depth + 1))
                            issue_count += int(local_level == LEVEL_ERROR)
        
        return issue_count
    
    def check_needs(self, level: str, ignore: dict, warn: dict, available_outputs: dict, depth: int=0) -> int:
        return 0
    
    def check_inputs(self, level: str, ignore: dict, warn: dict, parent_inputs: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking action [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_INPUT_WIRING):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_INPUT_WIRING):
                    local_level = LEVEL_WARN
                issue_count += child.check_inputs(local_level, ignore, warn, parent_inputs, depth=depth+1)
                for ip in child.input_refs:
                    if not ip in self.inputs:
                        check_log(self.log, f'[cyan]{child.ident}[/cyan] input `{ip}` is not present', local_level, self.indent * (depth + 1))
                        issue_count += int(local_level == LEVEL_ERROR)
        
        return issue_count

    def check_action_calls(self, level, ignore: dict, warn: dict, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking action [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                if check_luggage(self.doc, ignore, GH_CHECK_ACTION_CALLS):
                    self.log.debug(f'Skipping {child.name}')
                    continue
                local_level = level
                if check_luggage(self.doc, warn, GH_CHECK_ACTION_CALLS):
                    local_level = LEVEL_WARN
                for field, args in self.inputs.items():
                    if args.get('required', False) and not field in self.with_args:
                        check_log(self.log, f'Action [cyan]{self.ident}[/cyan] is missing required argument `{field}`', local_level, self.indent * (depth + 1))
                        issue_count += int(local_level == LEVEL_ERROR)
                if self.secret_with_args == 'inherit':
                    continue
                for field, args in self.secret_args.items():
                    if args.get('required', False) and not field in self.secret_with_args:
                        check_log(self.log, f'Action [cyan]{self.ident}[/cyan] is missing required secret `{field}`', local_level, self.indent * (depth + 1))
                        issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_action_calls(local_level, ignore, warn, depth=depth+1)

        return issue_count

    def check_refs(self, level: str, ignore: dict, warn: dict, ref_regex: str, depth: int=0) -> int:
        self.log.debug(f'{" " * self.indent * depth}Checking action [cyan]{self.ident}[/cyan]...', extra={"markup": True})
        issue_count = 0

        if self.max_depth == -1 or depth < self.max_depth:
            for child in self.children:
                local_level = level
                if check_luggage(self.doc, ignore, GH_CHECK_REF):
                    self.log.debug(f'Skipping {child.ident}')
                    continue
                if check_luggage(self.doc, warn, GH_CHECK_REF):
                    local_level = LEVEL_WARN
                if self.path and "@" in self.path:
                    ref = self.path.split('@')[1]
                    if not re.match(ref_regex, ref):
                        check_log(self.log, f'Action [cyan]{self.ident}[/cyan] references an invalid ref `{ref}`', local_level, self.indent * (depth + 1))
                        issue_count += int(local_level == LEVEL_ERROR)
                issue_count += child.check_refs(local_level, ignore, warn, ref_regex, depth=depth+1)
        
        return issue_count
