# OpenShift Day 2 Ansible Collection

This collection provides specialized modules for **OpenShift Day 2 Operations**, focusing on health checks, automated troubleshooting, and pre-upgrade validation.

## Key Features
* **Clusterless Testing:** Includes a "Mock Mode" to test logic without a live OpenShift cluster.
* **Health Monitoring:** Identifies degraded ClusterOperators and node pressures.
* **Modular Design:** Each module is a single-purpose "chunk" for easy integration into larger playbooks.

## Included Modules
* `ocp_cluster_health`: Validates the status of all OpenShift ClusterOperators.

## Getting Started (Mock Mode)
To see the module in action without a cluster, run the provided test playbook:

```bash
ansible-playbook playbook-health-check.yml
# openshift-collection
