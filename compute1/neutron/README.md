To configure Neutron on Network nodes we need below packages:
# yum install openstack-neutron openstack-neutron-openvswitch -y
--------------------------------------------------------------------------------
To configure Neutron on Compute nodes we do not need ml2 packages to be installed.
We only need openstack neutron package and openvswitch agent package.
---------------------------------------------------------------------------------
In this setup we are configuring a Flat provider network for direct IP assignment
which is reprsented by 'mgmt' network which uses 'br-provide' bridge on compute nodes.
---------------------------------------------------------------------------------
Also to create floating IP networks we do not require any extra configuration on
compute nodes, we only need to make 'GRE' or 'VXLAN' tunneling work.
