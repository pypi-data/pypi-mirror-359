import jsonpath_ng as jsonpath
import jsonpath_ng.ext as jsonpath_ext

def check_luggage(obj: dict, ignore: dict, test_name: str) -> bool:
    should_skip = False
    for local_disable in ignore:
        jsonpath_key = local_disable['path']
        jsonpath_expression = jsonpath_ext.parse(jsonpath_key)
        if jsonpath_expression.find(obj):
            if test_name in local_disable['tests']:
                should_skip = True
    return should_skip


