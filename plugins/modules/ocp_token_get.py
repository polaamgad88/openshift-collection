#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = r'''
---
module: ocp_token_get
short_description: Retrieve an OpenShift OAuth token using credentials
description:
    - This module authenticates against the OpenShift OAuth server using a username and password.
    - It returns a temporary session token (Bearer token) that can be used by other modules.
options:
    host:
        description: The OpenShift API URL (e.g., https://api.cluster.example.com:6443).
        type: str
        required: true
    username:
        description: OpenShift username for authentication.
        type: str
        required: true
    password:
        description: OpenShift password for authentication.
        type: str
        required: true
        no_log: true
    verify_ssl:
        description: Whether to verify the SSL certificate of the OAuth server.
        type: bool
        default: false
author:
    - Adel Amgad Messiha (aamgad@redhat.com)
'''

EXAMPLES = r'''
- name: Get a temporary OCP token
  polaamgad88.openshift_day2.ocp_token_get:
    host: "https://api.mycluster.com:6443"
    username: "admin"
    password: "password123"
    verify_ssl: false
  register: auth_token

- name: Use the token in another task
  debug:
    msg: "My token is {{ auth_token.ocp_token }}"
'''

RETURN = r'''
ocp_token:
    description: The retrieved OpenShift authentication token.
    returned: success
    type: str
    sample: "sha256~vX8..."
'''

def get_token(oauth_url, username, password, verify_ssl):
    token_url = f"{oauth_url}/oauth/authorize?client_id=openshift-challenging-client&response_type=token"
    headers = {'X-CSRF-Token': '1'} 
    try:
        response = requests.get(token_url, auth=(username, password), headers=headers, verify=verify_ssl, allow_redirects=False)
        if response.status_code == 302 and 'Location' in response.headers:
            location = response.headers['Location']
            return location.split('access_token=')[1].split('&')[0]
        return None
    except Exception:
        return None

def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        verify_ssl=dict(type='bool', default=False)
    )
    module = AnsibleModule(argument_spec=module_args)
    
    # Convert API URL to OAuth URL
    oauth_url = module.params['host'].replace("api.", "oauth-openshift.apps.").replace(":6443", "")
    
    token = get_token(oauth_url, module.params['username'], module.params['password'], module.params['verify_ssl'])

    if token:
        module.exit_json(changed=True, ocp_token=token)
    else:
        module.fail_json(msg="Failed to authenticate and retrieve token")

if __name__ == '__main__':
    run_module()
