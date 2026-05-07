source ./tidb.env

IDENTITY_FLAG="-i $KEY_SAVE_PATH"

tiup cluster check ${TOPOLOGY_FILE} ${IDENTITY_FLAG}
tiup cluster check ${TOPOLOGY_FILE} ${IDENTITY_FLAG} --apply
tiup cluster deploy ${CLUSTER_NAME} ${CLUSTER_VERSION} ${TOPOLOGY_FILE} ${IDENTITY_FLAG}  