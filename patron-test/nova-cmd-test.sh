nova net-list
#nova net-create 'demonet' 0.0.0.0
NET_ID=`neutron net-list`
NET_ID=`echo $NET_ID | cut -d '|' -f 6 | cut -d ' ' -f 2`
nova net $NET_ID
#nova net-delete $NET_ID
#nova service-delete <id>
nova dns-domains
nova list
#start a new instance
DEMONET_ID=`neutron net-list`
DEMONET_ID=`echo $DEMONET_ID | cut -d '|' -f 6 | cut -d ' ' -f 2`
read -p "Input your key's name:" KEY_NAME
nova keypair-add --pub_key ~/.ssh/id_rsa.pub $KEY_NAME
nova keypair-list
nova keypair-show $KEY_NAME
read -p "Input your instance's name:" INSTANCE_NAME
nova boot --flavor 1 --image "cirros-0.3.4-x86_64" --key-name $KEY_NAME --nic net-id=$DEMONET_ID --security-group default $INSTANCE_NAME
nova absolute-limits
nova credentials
nova cloudpipe-list
nova network-list
nova network-show demo-net
#host
nova host-list
read -p "Input hostname:" HOSTNAME
nova service-list
nova service-disable $HOSTNAME nova-compute
nova service-enable $HOSTNAME nova-compute
#nova host-action $HOSTNAME
nova host-describe $HOSTNAME
nova host-evacuate $HOSTNAME
nova host-evacuate-live $HOSTNAME

#nova host-meta $HOSTNAME <action>
nova host-servers-migrate $HOSTNAME
#nova host-update $HOSTNAME
nova hypervisor-list
nova hypervisor-servers $HOSTNAME
nova hypervisor-show $HOSTNAME
nova hypervisor-stats
nova hypervisor-uptime $HOSTNAME
nova network-list
nova network-show demo-net
read -p "Input your aggregate's name:" AGGRE_NAME
nova aggregate-create $AGGRE_NAME
nova aggregate-details $AGGRE_NAME
nova aggregate-list
read -p "Input your server's name:" SERVER_NAME
nova aggregate-add-host $AGGRE_NAME $SERVER_NAME
nova aggregate-remove-host $AGGRE_NAME $SERVER_NAME
nova aggregate-delete $AGGRE_NAME
nova availability-zone-list
#image
nova image-create $INSTANCE_NAME demo-image1
nova image-list
nova image-meta demo-image1 set 'key'='value'
nova image-meta demo-image1 delete 'key'='value'
nova image-show demo-image1
nova image-delete demo-image1
# while instance is running
nova console-log $INSTANCE_NAME
nova diagnostics $INSTANCE_NAME
nova get-password $INSTANCE_NAME
nova interface-list $INSTANCE_NAME
nova instance-action-list $INSTANCE_NAME
nova get-serial-console $INSTANCE_NAME
nova interface-attach $INSTANCE_NAME
nova add-secgroup $INSTANCE_NAME demo-secgroup1
nova remove-secgroup $INSTANCE_NAME demo-secgroup1
#nova clear-password $INSTANCE_NAME
nova refresh-network $INSTANCE_NAME
nova reset-network $INSTANCE_NAME
nova reset-state $INSTANCE_NAME
nova shelve $INSTANCE_NAME
nova shelve-offload $INSTANCE_NAME
nova show $INSTANCE_NAME
nova list-secgroup $INSTANCE_NAME
nova rescue $INSTANCE_NAME
nova ssh $INSTANCE_NAME
#change root password
nova root-password $INSTANCE_NAME
nova stop $INSTANCE_NAME
nova start $INSTANCE_NAME
nova suspend $INSTANCE_NAME
nova resume $INSTANCE_NAME
nova lock $INSTANCE_NAME
nova unlock $INSTANCE_NAME
nova shelve $INSTANCE_NAME
nova shelve-offload $INSTANCE_NAME
nova pause $INSTANCE_NAME
nova unpause $INSTANCE_NAME
nova unrescue $INSTANCE_NAME
nova unshelve $INSTANCE_NAME
nova reboot $INSTANCE_NAME
#nova rebuild $INSTANCE_NAME <image>
nova resize $INSTANCE_NAME 2
nova resize-confirm $INSTANCE_NAME
nova resize-revert $INSTANCE_NAME
#nova soft-delelte $INSTANCE_NAME
#nova force-delelte $INSTANCE_NAME
nova restore $INSTANCE_NAME
read -p "Input a new instance's name:" NEW_INSTANCE_NAME
nova rename $INSTANCE_NAME $NEW_INSTANCE_NAME
nova delete $NEW_INSTANCE_NAME
nova keypair-delete $KEY_NAME
nova list-extensions
nova migration-list
#nova migration $INSTANCE_NAME
#flavor
nova flavor-list
nova flavor-show 1
nova flavor-create m1.demo 6 512 10 1
nova flavor-delete 6
nova flavor-access-list
#floating-ip
nova floating-ip-list
nova floating-ip-pool-list
nova floating-ip-bulk-list
nova floating-ip-create
nova secgroup-list
nova secgroup-list-default-rules
nova secgroup-create demo-secgroup1 "demo secgroup 1"
nova secgroup-update demo-secgroup1 demo-secgroup1-new "demo secgroup 1 new"
nova secgroup-delete demo-secgroup1-new
nova secgroup-list-rules default
nova endpoints
read -p "Input server-group name:" SERVER_GROUP_NAME
nova server-group-create $SERVER_GROUP_NAME "affinity"
SERVER_GROUP_ID=`nova server-group-list`
SERVER_GROUP_ID=`echo $SERVER_GROUP_ID | cut -d '|' -f 8 | cut -d ' ' -f 2`
nova server-group-delete $SERVER_GROUP_ID
nova server-group-get $SERVER_GROUP_ID
nova server-group-list
nova tenant-network-create "tenant-network" 0.0.0.0
nova tenant-network-list
nova tenant-network-delete <network_id>
nova tenant-network-show <network_id>
nova quota-class-show "a"
nova quota-class-update "a"
nova quota-defaults
#nova quota-delete --tenant <tenant-id> [--user <user-id>]
nova quota-show

#nova network-associate-host <network> <host>
#nova network-associate-project <network>
#nova network-create <network_label>
#nova network-delete <network>
#nova network-disassociate <network>
#nova dns-create <ip> <name> <domain>
#nova dns-create-private-domain <domain>
#nova dns-create-public-domain <domain>
#nova dns-delete <domain> <name>
#nova dns-delete-domain <domain>
#nova dns-list <domain>
nova quota-update <tenant-id>
nova usage
nova usage-list
nova version-list
nova cloudpipe-list
nova x509-get-root-cert

