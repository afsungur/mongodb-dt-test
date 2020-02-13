# kill existing mongod and mongos processes
echo "Killing existing mongod and mongos processes if exist"
ps -ef | grep -E "mongos|mongod" | grep -v grep | awk '{print $2}' | xargs kill -9
mode=$1
echo "Mode : $mode"

if [ "$mode" = "CREATE" ] 
then
	echo "~/localdbcluster/ folder will be deleted and re-created with its subfolders..."
	rm -rf ~/localdbcluster/
	mkdir -p ~/localdbcluster/data/shard-01/01/
	mkdir -p ~/localdbcluster/data/shard-01/02/
	mkdir -p ~/localdbcluster/data/shard-01/03/
	mkdir -p ~/localdbcluster/data/shard-02/01/
	mkdir -p ~/localdbcluster/data/shard-02/02/
	mkdir -p ~/localdbcluster/data/shard-02/03/
	mkdir -p ~/localdbcluster/data/shard-03/01/
	mkdir -p ~/localdbcluster/data/shard-03/02/
	mkdir -p ~/localdbcluster/data/shard-03/03/
	mkdir -p ~/localdbcluster/data/configserver/01/
	mkdir -p ~/localdbcluster/data/configserver/02/
	mkdir -p ~/localdbcluster/data/configserver/03/
	mkdir -p ~/localdbcluster/log/shard-01/01/
	mkdir -p ~/localdbcluster/log/shard-01/02/
	mkdir -p ~/localdbcluster/log/shard-01/03/
	mkdir -p ~/localdbcluster/log/shard-02/01/
	mkdir -p ~/localdbcluster/log/shard-02/02/
	mkdir -p ~/localdbcluster/log/shard-02/03/
	mkdir -p ~/localdbcluster/log/shard-03/01/
	mkdir -p ~/localdbcluster/log/shard-03/02/
	mkdir -p ~/localdbcluster/log/shard-03/03/
	mkdir -p ~/localdbcluster/log/configserver/01/
	mkdir -p ~/localdbcluster/log/configserver/02/
	mkdir -p ~/localdbcluster/log/configserver/03/
	mkdir -p ~/localdbcluster/log/mongos/01/
	mkdir -p ~/localdbcluster/log/mongos/02/
	mkdir -p ~/localdbcluster/log/mongos/03/
fi

echo "====================================================="
echo "Config server replicas are going to be started ..."
sh config-server-start.sh
echo "====================================================="
echo "Shard-01 replicas are going to be started ..."
sh shard-01-start.sh
echo "====================================================="
echo "Shard-02 replicas are going to be started ..."
sh shard-02-start.sh
echo "====================================================="
echo "Shard-03 replicas are going to be started ..."
sh shard-03-start.sh
echo "====================================================="
echo "Mongoses are going to be started ..."
sh mongos-start.sh
echo "====================================================="
echo "Mongodb processes:"
echo ""
ps -ef | grep -E "mongod|mongos" | grep -v grep
echo "====================================================="


if [ "$mode" = "CREATE" ]
then
	echo "====================================================="
	echo "Adding shards ..."
	sh mongos-add-shard.sh
	echo "Shards added ..."
	echo "====================================================="
	

	echo "====================================================="
	echo "Enabling sharding..."
	sh enable-sharding.sh
	echo "Sharding enabled..."
	echo "====================================================="
	
	echo "====================================================="
	echo "Creating indexes..."
	sh index_create.sh
	echo "Index created ..."
	echo "====================================================="
fi
