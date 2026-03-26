# OpenShift Day 2 Ansible Collection

This collection provides specialized modules for **OpenShift Day 2 Operations**, focusing on health checks, automated troubleshooting, and lifecycle management.

## Key Features
* **Clusterless Testing:** Includes a "Mock Mode" to test logic without a live OpenShift cluster.
* **Health Monitoring:** Identifies degraded ClusterOperators and node pressures.
* **Modular Design:** Each module is a single-purpose "chunk" for easy integration.

## Current Modules
* `ocp_cluster_health`: Validates the status of all OpenShift ClusterOperators.

## Project Roadmap (Modules in Development)
I am currently working on expanding this collection with the following "chunks":

###  Health & Diagnostics
* `ocp_node_condition_info`: Identify nodes with Disk, Memory, or PID pressure.
* `ocp_pod_restart_check`: Detect pods in CrashLoopBackOff with high restart counts.
* `ocp_etcd_health_info`: Verify ETCD quorum and leader stability.

###  Patching & Maintenance
* `ocp_mcp_wait`: Wait for MachineConfigPools to complete node reboots/updates.
* `ocp_olm_update_check`: Identify Operators with pending or failed InstallPlans.

###  Upgrade Lifecycle
* `ocp_upgrade_available_info`: Analyze valid and conditional upgrade paths.
* `ocp_api_v1beta1_detector`: Scan for deprecated APIs before cluster upgrades.

###  Resource Optimization
* `ocp_pvc_usage_info`: Report on Persistent Volume Claims nearing capacity.
* `ocp_cert_report_info`: Audit internal and ingress certificates for upcoming expiry.
