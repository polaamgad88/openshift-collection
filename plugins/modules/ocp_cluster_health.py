#!/usr/bin/python

# In Ansible modules, this is almost always /usr/bin/python.

from ansible.module_utils.basic import AnsibleModule
import json
import os

def run_module():
    """
    Main function for the Ansible module logic.
    """

    # 1. Define the Module Arguments (Inputs)
    # This dictionary defines what the user can pass in the YAML playbook.
    module_args = dict(
        test_mode=dict(type='bool', default=False),  # Toggle for mock testing
        mock_path=dict(type='str', required=False)   # Path to the fake JSON file
    )

    # 2. Initialize the AnsibleModule object
    # This object handles communication between your script and Ansible.
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True  # Tells Ansible this module doesn't make "real" changes
    )

    # 3. Initialize the Result Dictionary
    # Everything in this dict will be sent back to the user in the 'register' variable.
    result = dict(
        changed=False,             # Day 2 "Read" modules usually return False for changed
        degraded_operators=[],     # A list to hold any issues we find
        total_checked=0            # Metadata to show the user how much work was done
    )

    # 4. Data Acquisition (Mock vs. Real)
    if module.params['test_mode']:
        # --- MOCK LOGIC ---
        path = module.params['mock_path']
        
        # Validation: Ensure the mock file exists before trying to read it
        if not path or not os.path.exists(path):
            module.fail_json(msg=f"Mock mode is ON, but file was not found at: {path}")
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            module.fail_json(msg=f"Failed to parse JSON from mock file: {str(e)}")
    else:
        # --- REAL LOGIC ---
        # This is where you will eventually add the OpenShift API client code.
        module.fail_json(msg="Real cluster connection is not yet implemented. Please use test_mode: true.")

    # 5. The "Business Logic" (Processing the Data)
    # OpenShift ClusterOperators return data in an 'items' list.
    items = data.get('items', [])
    result['total_checked'] = len(items)

    for item in items:
        # Get the name of the operator (e.g., 'console', 'image-registry')
        name = item.get('metadata', {}).get('name', 'unknown')
        
        # Dig into the 'status.conditions' list
        conditions = item.get('status', {}).get('conditions', [])
        
        # Look for a condition where Type is 'Degraded' and Status is 'True'
        for condition in conditions:
            if condition.get('type') == 'Degraded' and condition.get('status') == 'True':
                # If found, add it to our results list
                result['degraded_operators'].append(name)

    # 6. Exit and Return Results
    # Use exit_json to send the dictionary back to Ansible.
    module.exit_json(**result)

if __name__ == '__main__':
    # Standard Python entry point
    run_module()
