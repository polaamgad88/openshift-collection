#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests
import re
try:
    from kubernetes import client
    from openshift.dynamic import DynamicClient
    HAS_K8S = True
except ImportError:
    HAS_K8S = False

DOCUMENTATION = r'''
---
module: ocp_worker_node_resource_info
short_description: Professional OpenShift Node Resource Analytics
description:
    - Provides a high-level, human-readable report of worker node memory commitment.
    - Calculates Requests vs Allocatable capacity.
options:
    host: {type: str, required: true}
    username: {type: str}
    password: {type: str, no_log: true}
    api_key: {type: str, no_log: true}
    verify_ssl: {type: bool, default: false}
    target_role: {type: str, default: worker}
'''

def get_token(api_url, username, password, verify_ssl):
    oauth_url = api_url.replace("api.", "oauth-openshift.apps.").replace(":6443", "")
    token_url = f"{oauth_url}/oauth/authorize?client_id=openshift-challenging-client&response_type=token"
    headers = {'X-CSRF-Token': '1'}
    try:
        res = requests.get(token_url, auth=(username, password), headers=headers, verify=verify_ssl, allow_redirects=False)
        if res.status_code == 302 and 'Location' in res.headers:
            return res.headers['Location'].split('access_token=')[1].split('&')[0]
        return None
    except Exception:
        return None

def parse_mem_to_gb(mem_val):
    if not mem_val: return 0
    mem_str = str(mem_val)
    try:
        numeric_match = re.search(r'^([0-9.]+)', mem_str)
        if not numeric_match: return 0
        number = float(numeric_match.group(1))
        unit = mem_str.lower()
        if "gi" in unit: return number
        if "mi" in unit: return number / 1024
        if "ki" in unit: return number / (1024**2)
        return number / (1024**3)
    except (ValueError, TypeError): return 0

def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        api_key=dict(type='str', required=False, no_log=True),
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        verify_ssl=dict(type='bool', default=False),
        target_role=dict(type='str', default='worker')
    )

    module = AnsibleModule(argument_spec=module_args)
    # result['worker_analysis'] is now a dict for better programmatic access
    result = dict(changed=False, worker_analysis={}, report_lines=[], summary={})

    if not HAS_K8S:
        module.fail_json(msg="Python libraries 'kubernetes' and 'openshift' are required.")

    token = module.params.get('api_key')
    if not token and module.params.get('username'):
        token = get_token(module.params['host'], module.params['username'], module.params['password'], module.params['verify_ssl'])

    if not token:
        module.fail_json(msg="Auth failed")

    try:
        conf = client.Configuration()
        conf.host = module.params['host']
        conf.verify_ssl = module.params['verify_ssl']
        conf.api_key = {"authorization": f"Bearer {token}"}
        
        dyn_client = DynamicClient(client.ApiClient(conf))
        v1_node = dyn_client.resources.get(api_version='v1', kind='Node')
        v1_pod = dyn_client.resources.get(api_version='v1', kind='Pod')
        
        nodes = v1_node.get().items
        role_label = f"node-role.kubernetes.io/{module.params['target_role']}"

        # Header for the human-readable report
        report = []
        header = "{:<35} | {:<6} | {:<10} | {:<10} | {:<12}".format(
            "NODE NAME", "PODS", "ALLOC(GB)", "USED(GB)", "COMMITMENT"
        )
        report.append("-" * 85)
        report.append(header)
        report.append("-" * 85)

        total_pods = 0

        for node in nodes:
            labels = node.metadata.get('labels', {}) or {}
            is_target = False
            if module.params['target_role'] == 'all':
                is_target = True
            else:
                for key in labels.keys():
                    if module.params['target_role'] in key:
                        is_target = True
                        break
            
            if not is_target: continue

            node_name = node.metadata.name
            allocatable_gb = parse_mem_to_gb(node.status.get('allocatable', {}).get('memory', '0'))
            
            node_pods = v1_pod.get(field_selector=f"spec.nodeName={node_name}").items
            node_req_gb = 0
            pod_count = 0

            for p in node_pods:
                if p.status.phase not in ['Running', 'Pending']: continue
                pod_count += 1
                containers = p.spec.get('containers', [])
                for c in containers:
                    res = c.get('resources', {})
                    reqs = res.get('requests', {}) or {}
                    lims = res.get('limits', {}) or {}
                    val = parse_mem_to_gb(reqs.get('memory')) if reqs.get('memory') else parse_mem_to_gb(lims.get('memory'))
                    node_req_gb += val

            total_pods += pod_count
            usage_pct = (node_req_gb / allocatable_gb * 100) if allocatable_gb > 0 else 0
            status = "HEALTHY" if usage_pct < 90 else "HIGH LOAD"

            # Add to programmatic dict
            result['worker_analysis'][node_name] = {
                "pods": pod_count,
                "allocatable_gb": round(allocatable_gb, 2),
                "requested_gb": round(node_req_gb, 2),
                "usage_pct": round(usage_pct, 2),
                "status": status
            }

            # Add to human-readable report list
            row = "{:<35} | {:<6} | {:<10} | {:<10} | {:<12} ({})".format(
                node_name, pod_count, round(allocatable_gb, 2), round(node_req_gb, 2), 
                str(round(usage_pct, 2)) + "%", status
            )
            report.append(row)

        report.append("-" * 85)
        result['report_lines'] = report
        result['summary'] = {"nodes": len(result['worker_analysis']), "pods": total_pods}

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    run_module()
