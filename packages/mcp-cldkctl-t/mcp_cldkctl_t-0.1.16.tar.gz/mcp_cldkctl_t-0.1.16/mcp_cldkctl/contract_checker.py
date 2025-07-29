import os
import re
import ast

# Paths (relative to this script)
PY_TOOL_MAP = os.path.join(os.path.dirname(__file__), 'tool_param_map.py')
GO_ROUTES = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ai-cldkctl/config/routes/routes.go'))

def parse_python_tool_map(path):
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    # Use ast to safely evaluate the TOOL_PARAM_MAP dict
    tree = ast.parse(source, filename=path)
    tool_map = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'TOOL_PARAM_MAP':
                    tool_map = ast.literal_eval(node.value)
    # Build endpoint-method map
    py_endpoints = {}
    for tool, meta in tool_map.items():
        endpoint = meta['endpoint']
        method = meta['method'].upper()
        py_endpoints[(endpoint, method)] = {
            'tool': tool,
            'required_params': [p['name'] for p in meta.get('required_params', [])],
            'optional_params': [p['name'] for p in meta.get('optional_params', [])],
        }
    return py_endpoints

def parse_go_routes(path):
    with open(path, 'r', encoding='utf-8') as f:
        go = f.read()
    # Find all Route assignments: Name = Route{ Method: "...", Endpoint: "..." }
    route_re = re.compile(r'([A-Za-z0-9_]+)\s*=\s*Route\s*{\s*Method:\s*"([A-Z]+)",\s*Endpoint:\s*"([^"]+)"', re.MULTILINE)
    go_endpoints = {}
    for match in route_re.finditer(go):
        name, method, endpoint = match.groups()
        go_endpoints[(endpoint, method)] = name
    # Also handle Endpoint: "/core/pods" + KubeCoreURI, etc.
    # Find KubeCoreURI, etc. definitions
    const_re = re.compile(r'([A-Za-z0-9_]+)\s*=\s*"([^"]+)"')
    consts = dict(const_re.findall(go))
    # Find Route assignments with concatenation
    concat_re = re.compile(r'([A-Za-z0-9_]+)\s*=\s*Route\s*{\s*Method:\s*"([A-Z]+)",\s*Endpoint:\s*"([^"]+)"\s*\+\s*([A-Za-z0-9_]+)', re.MULTILINE)
    for match in concat_re.finditer(go):
        name, method, endpoint, const = match.groups()
        full_endpoint = endpoint + consts.get(const, '')
        go_endpoints[(full_endpoint, method)] = name
    return go_endpoints

def main():
    py_endpoints = parse_python_tool_map(PY_TOOL_MAP)
    go_endpoints = parse_go_routes(GO_ROUTES)

    py_set = set(py_endpoints.keys())
    go_set = set(go_endpoints.keys())

    print('--- Endpoints in Python but NOT in Go (phantom tools):')
    for ep in sorted(py_set - go_set):
        print(f'  {ep[1]} {ep[0]} (tool: {py_endpoints[ep]["tool"]})')

    print('\n--- Endpoints in Go but NOT in Python (missing tools):')
    for ep in sorted(go_set - py_set):
        print(f'  {ep[1]} {ep[0]} (Go route: {go_endpoints[ep]})')

    print('\n--- Endpoints present in BOTH:')
    for ep in sorted(py_set & go_set):
        py_params = set(py_endpoints[ep]['required_params'])
        # We can't get Go params easily, so just print Python ones
        print(f'  {ep[1]} {ep[0]} (tool: {py_endpoints[ep]["tool"]})')
        print(f'    Python required params: {sorted(py_params)}')

if __name__ == '__main__':
    main() 