def format_triggers(triggers: dict = None) -> list:
    out = []
    for kind, args in triggers.items():
        if kind == "branch_protection_rule":
            for arg in args['types']:
                out.append(f'- Branch protection rule [magenta]{arg}[/magenta]')
        if kind == "check_run":
            for arg in args['types']:
                out.append(f'- Check run [magenta]{arg}[/magenta]')
        if kind == "check_suite":
            for arg in args['types']:
                out.append(f'- Check suite [magenta]{arg}[/magenta]')
        if kind == "create":
            out.append(f'- Branch or tag created')
        if kind == "delete":
            out.append(f'- Branch or tag deleted')
        if kind == 'deployment':
            out.append(f'- Deployment created')
        if kind == 'deployment_status':
            out.append(f'- Deployment status provided by third party')
        if kind == "discussion":
            for arg in args['types']:
                out.append(f'- Discussion [magenta]{arg}[/magenta]')
        # discussion_comment
        # fork
        # gollum
        # issue_comment
        # issues
        # label
        # merge_group
        # milestone
        # page_build
        # public
        if kind == "pull_request":
            for arg in args['types']:
                out.append(f'- Pull request [magenta]{arg}[/magenta]')
        # pull_request_comment
        # pull_request_review
        # pull_request_review_comment
        # pull_request_target
        if kind == "push":
            if 'branches' in args:
                for arg in args['branches']:
                    out.append(f'- Push to [magenta]{arg}[/magenta] branch(s)')
            if 'branches-ignore' in args:
                for arg in args['branches-ignore']:
                    out.append(f'- Ignoring branch(es) [magenta]{arg}[/magenta]')
            if 'tags' in args:
                for arg in args['tags']:
                    out.append(f'- Push to [magenta]{arg}[/magenta] tag(s)')
            if 'tags-ignore' in args:
                for arg in args['tags-ignore']:
                    out.append(f'- Ignoring tag(s) [magenta]{arg}[/magenta]')
            if 'paths' in args:
                for arg in args['paths']:
                    out.append(f'- Push to [magenta]{arg}[/magenta] path(s)')
            if 'paths-ignore' in args:
                for arg in args['paths-ignore']:
                    out.append(f'- Ignoring path(s) [magenta]{arg}[/magenta]')
        # registry_package
        if kind == "release":
            for arg in args['types']:
                out.append(f'- Release [magenta]{arg}[/magenta]')
        # repository_dispatch
        # schedule
        # status
        # watch
        if kind == 'workflow_call':
            out.append(f'- Workflow called by another workflow')
        if kind == 'workflow_dispatch':
            out.append(f'- Workflow triggered manually')
        if kind == 'workflow_run':
            for arg in args['types']:
                out.append(f'- Workflow run [magenta]{arg}[/magenta]')
    return out
