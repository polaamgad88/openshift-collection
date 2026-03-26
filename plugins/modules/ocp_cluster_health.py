#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests
try:
    from kubernetes import client
    from openshift.dynamic import DynamicClient
    HAS_K8S = True
except ImportError:
    HAS_K8S = False

def get_token(api_url, username, password, verify_ssl):
    """Internal helper to get token if user/pass are provided directly."""
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

def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        api_key=dict(type='str', required=False, no_log=True),
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        verify_ssl=dict(type='bool', default=False)
    )

    module = AnsibleModule(argument_spec=module_args)
    result = dict(changed=False, degraded_operators=[], total_checked=0)

    if not HAS_K8S:
        module.fail_json(msg="Python libraries 'kubernetes' and 'openshift' are required.")

    # --- AUTH LOGIC ---
    token = None
    if module.params['api_key']:
        token = module.params['api_key']
    elif module.params['username'] and module.params['password']:
        token = get_token(module.params['host'], module.params['username'], module.params['password'], module.params['verify_ssl'])
    
    if not token:
        module.fail_json(msg="Authentication failed: Provide either api_key OR username/password.")

    try:
        conf = client.Configuration()
        conf.host = module.params['host']
        conf.verify_ssl = module.params['verify_ssl']
        conf.api_key = {"authorization": f"Bearer {token}"}
        
        dyn_client = DynamicClient(client.ApiClient(conf))
        co_api = dyn_client.resources.get(api_version='v1', kind='ClusterOperator', group='config.openshift.io')
        data = co_api.get().to_dict()

        items = data.get('items', [])
        result['total_checked'] = len(items)
        for item in items:
            name = item.get('metadata', {}).get('name', 'unknown')
            conditions = item.get('status', {}).get('conditions', [])
            for cond in conditions:
                if cond.get('type') == 'Degraded' and cond.get('status') == 'True':
                    result['degraded_operators'].append(name)

        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=f"API Error: {str(e)}")

if __name__ == '__main__':
    run_module()
