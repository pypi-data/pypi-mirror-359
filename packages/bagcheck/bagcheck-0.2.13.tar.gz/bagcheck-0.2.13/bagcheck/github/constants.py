import re

GH_KIND_ACTION = "action"
GH_KIND_WORKFLOW = "workflow"
GH_KIND_STEP = "step"
GH_KIND_JOB = "job"

GH_CHECK_TIMEOUT = "github-check-timeout"
GH_CHECK_RUNS_ON = "github-check-runs-on"
GH_CHECK_WORKFLOW_CALLS = "github-check-workflow-calls"
GH_CHECK_ACTION_CALLS = "github-check-action-calls"
GH_CHECK_OUTPUT_WIRING = "github-check-output-wiring"
GH_CHECK_NEEDS_WIRING = "github-check-needs-wiring"
GH_CHECK_INPUT_WIRING = "github-check-input-wiring"
GH_CHECK_REF = "github-check-ref"

LEVEL_WARN = 'warn'
LEVEL_ERROR = 'error'

GH_INPUTS_PATTERN = re.compile("[\s({]inputs\.([^)}\s]*)")
GH_SECRETS_PATTERN = re.compile("[\s({]secrets\.([^)}\s]*)")
GH_JOB_OUTPUTS_PATTERN = re.compile("[\s({]jobs\.(\S*)\.outputs\.([^)}\s]*)")
GH_STEP_OUTPUTS_PATTERN = re.compile("[\s({]steps\.(\S*)\.outputs\.([^)}\s]*)")
GH_RUN_OUTPUTS_PATTERN = re.compile('echo ["\'](\S*)=.*["\']\s*>>\s*"?\$GITHUB_OUTPUT"?')
GH_NEEDS_PATTERN = re.compile("[\s({]needs\.(\S*)\.outputs\.([^)}\s]*)")
