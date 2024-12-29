from jsonpath_ng import parse
from typing import Any


class ListEvaluator:
    def __init__(self, spec: dict):
        self.includes = spec.get('includes', [])
        self.excludes = spec.get('excludes', [])
        self.max_length = spec.get('max_length')
        self.path = spec.get('path')

    def __call__(self, value: Any) -> dict:
        # Extract the list using jsonpath if path is specified
        if self.path:
            try:
                jsonpath_expr = parse(self.path)
                matches = jsonpath_expr.find(value)
                if not matches:
                    return {
                        'score': 0,
                        'metadata': {'error': f'Path {self.path} not found'},
                    }
                target_list = matches[0].value
            except Exception as e:
                return {'score': 0, 'metadata': {'error': f'Invalid path: {str(e)}'}}
        else:
            target_list = value

        if not isinstance(target_list, (list, tuple)):
            return {'score': 0, 'metadata': {'error': 'Value is not a list'}}

        failures = []

        # Check includes
        for item in self.includes:
            if item not in target_list:
                failures.append(f'Missing required item: {item}')

        # Check excludes
        for item in self.excludes:
            if item in target_list:
                failures.append(f'Found excluded item: {item}')

        # Check max length
        if self.max_length is not None and len(target_list) > self.max_length:
            failures.append(
                f'List length {len(target_list)} exceeds maximum {self.max_length}'
            )

        score = 1.0 if not failures else 0.0
        return {
            'score': score,
            'metadata': {
                'failures': failures,
                'actual_length': len(target_list),
                'actual_items': target_list
            }
        }
