import logging
import jsonpath_ng as jsonpath
import jsonpath_ng.ext as jsonpath_ext
from bagcheck.github.workflow import build_tree
from bagcheck.utils import check_luggage
from bagcheck.github.constants import *

def check(log: logging.Logger, path: str, bagcheck_config: dict, indent: int=4, max_depth: int=-1) -> None:
    local_warn = bagcheck_config['warn']['local']
    global_warn = bagcheck_config['warn']['global']
    local_disable = bagcheck_config['disable']['local']
    global_disable = bagcheck_config['disable']['global']
    ref_regex = bagcheck_config['config']['ref_regex']
    issue_count = 0
    for root in build_tree(log, path, indent=indent, max_depth=max_depth):
        if root.kind in [GH_KIND_JOB, GH_KIND_WORKFLOW]:
            if GH_CHECK_OUTPUT_WIRING in global_disable:
                log.info(f'Skipping outputs check {root.name}')
            else:
                log.info("Performing outputs check...")
                issue_count += root.check_outputs(LEVEL_WARN if GH_CHECK_OUTPUT_WIRING in global_warn else LEVEL_ERROR, local_disable, local_warn, depth=0)

            if GH_CHECK_NEEDS_WIRING in global_disable:
                log.info(f'Skipping needs check {root.name}')
            else:
                log.info("Performing needs check...")
                issue_count += root.check_needs(LEVEL_WARN if GH_CHECK_NEEDS_WIRING in global_warn else LEVEL_ERROR, local_disable, local_warn, {}, depth=0)

            if GH_CHECK_INPUT_WIRING in global_disable:
                log.info(f'Skipping inputs check {root.name}')
            else:
                log.info("Performing inputs check...")
                issue_count += root.check_inputs(LEVEL_WARN if GH_CHECK_INPUT_WIRING in global_warn else LEVEL_ERROR, local_disable, local_warn, {}, depth=0)

            if GH_CHECK_TIMEOUT in global_disable:
                log.info(f'Skipping timeout check {root.name}')
            else:
                log.info("Performing timeout check...")
                issue_count += root.check_timeout(LEVEL_WARN if GH_CHECK_TIMEOUT in global_warn else LEVEL_ERROR, local_disable, local_warn, depth=0)
                
            if GH_CHECK_RUNS_ON in global_disable:
                log.info(f'Skipping run platform check {root.name}')
            else:
                log.info("Performing run platform check...")
                issue_count += root.check_runs_on(LEVEL_WARN if GH_CHECK_RUNS_ON in global_warn else LEVEL_ERROR, local_disable, local_warn, depth=0)

            if GH_CHECK_WORKFLOW_CALLS in global_disable:
                log.info(f'Skipping workflow call argument check {root.name}')
            else:
                log.info("Performing workflow call argument check...")
                issue_count += root.check_workflow_calls(LEVEL_WARN if GH_CHECK_WORKFLOW_CALLS in global_warn else LEVEL_ERROR, local_disable, local_warn, depth=0)

            if GH_CHECK_ACTION_CALLS in global_disable:
                log.info(f'Skipping action call argument check {root.name}')
            else:
                log.info("Performing action call argument check...")
                issue_count += root.check_action_calls(LEVEL_WARN if GH_CHECK_ACTION_CALLS in global_warn else LEVEL_ERROR, local_disable, local_warn, depth=0)

            if GH_CHECK_REF in global_disable:
                log.info(f'Skipping external action/workflow version check {root.name}')
            else:
                log.info("Performing external action/workflow version check...")
                issue_count += root.check_refs(LEVEL_WARN if GH_CHECK_REF in global_warn else LEVEL_ERROR, local_disable, local_warn, ref_regex, depth=0)

    # Print out success or failure
    if issue_count == 0:
        log.info("No issues found")
        exit(0)
    elif issue_count == 1:
        log.error('Found 1 issue')
    else:
        log.error(f"Found {issue_count} issues")
        exit(1)

