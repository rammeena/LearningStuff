To configure Neutron on Network nodes we need below packages:
# yum install openstack-neutron openstack-neutron-openvswitch -y
--------------------------------------------------------------------------------
To configure Neutron and openvswitch agnet on Network nodes we do not need ml2 packages to be installed.
We only need openstack neutron package and openvswitch agent package.
---------------------------------------------------------------------------------
In this lab setup we are configuring two networks:

1. Flat Provider Network - represented by 'mgmt' network in openvswitch agent file
2. Floating IP Network - represented by 'public' netwokr in openvswitch agent file

Two seperate bridges are required to configure each network which are connected
to respective network switches
--------------------------------------------------------------------------------

