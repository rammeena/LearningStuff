This install is configured for below networking implemenations:
1. Tenant Networks
2. Floating IP Network
3. Flat Provider Network - Direct IP assignment

To install neutron on controller nodes use the below command:
------------------------------------------------------------
# yum install openstack-neutron openstack-neutron-ml2

We install ml2 plugin only on controller nodes, it is not required on compute and network nodes. 
Core Neutron code 'openstack-neutron' is required on all openstack nodes like controller, compute and Network nodes.
