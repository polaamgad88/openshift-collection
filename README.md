# OpenShift Day 2 Ansible Collection (`polaamgad88.openshift_day2`)

This collection provides specialized Ansible modules designed for **OpenShift Day 2 Operations**. It moves beyond basic installation, focusing on deep-dive diagnostics, security auditing, resource optimization, and automated lifecycle management.

---

##  Key Features

* **Infrastructure Health:** Real-time analysis of ClusterOperators and Node pressures.
* **Security First:** Automated auditing of TLS certificate expiration across all namespaces.
* **Capacity Planning:** Accurate memory commitment ratios (Requests vs. Allocatable) to prevent OOM evictions.
* **Human-Centric Output:** Pre-formatted diagnostic tables designed for SREs and Admins.

---

##  Current Modules

### 1. `ocp_cluster_health`
Validates the status of all OpenShift ClusterOperators, highlighting **Degraded** or **Non-Available** components.

### 2. `ocp_worker_node_resource_info`
Analyzes node capacity and pod resource requests.
* Calculates **Commitment Ratio %**.
* Identifies nodes under high memory pressure.
* Supports filtering by roles (`worker`, `master`, or `all`).

### 3. `ocp_secret_expiry_info`
A security auditor that scans secrets (`tls.crt`, `ca.crt`) across the cluster.
* Decodes certificates on the fly.
* Reports days remaining until expiry.
* Flags expired certificates (like the critical `pprof-cert`).

### 4. `ocp_token_get`
A utility module to exchange LDAP/HTPasswd credentials for a temporary OAuth Bearer token.

---

## Project Roadmap (In Development)

I am expanding this collection into a full-scale **OpenShift Automation Factory**. The following modules are currently under development:

### Identity & Access Management (IAM)
* **`ocp_idp_ldap_setup`**: Seamless integration with LDAP/Active Directory including CA certificate injection.
* **`ocp_local_admin_manager`**: Automated `htpasswd` provider creation and secure deletion of the default `kubeadmin` account.

### Storage Administration (Data)
* **`ocp_odf_provisioner`**: Full-stack installation of OpenShift Data Foundation (ODF).
* **`ocp_storage_disk_manager`**: Automated disk identification and `LocalVolume` CR creation for local storage clusters.

### Observability & Logging
* **`ocp_logging_stack_deploy`**: One-click deployment of the Cluster Logging operator and Loki stack.
* **`ocp_log_forwarder_config`**: Seamless configuration of log forwarding to external targets (Elasticsearch, Kafka, Splunk).

### Multi-Cluster Operations (ACM)
* **`ocp_acm_import`**: Automates the joining process for importing managed clusters into an ACM Hub.
* **`ocp_submariner_gateway`**: Configuration and verification of cross-cluster networking.

---

### Installation & Usage

### Install from Ansible Galaxy
```bash
ansible-galaxy collection install polaamgad88.openshift_day2
