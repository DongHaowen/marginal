source ./tidb.env

tiup cluster check ${TOPOLOGY_FILE}
tiup cluster check ${TOPOLOGY_FILE} --apply
tiup cluster deploy ${CLUSTER_NAME} ${TOPOLOGY_FILE}