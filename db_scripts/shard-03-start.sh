mongod -f shard-03-repl-set-01.yaml
sleep 5
echo "Started Shard 03 Replica 01 ..."
mongod -f shard-03-repl-set-02.yaml
sleep 5
echo "Started Shard 03 Replica 02 ..."
mongod -f shard-03-repl-set-03.yaml
sleep 5
echo "Started Shard 03 Replica 03 ..."
mongo --port 25001 < shard-03-rs-initiate.js
echo "Replica set initiated for Shard 03"
mongo "mongodb://localhost:25001,localhost:25002,localhost:25003/?readPreference=primary" < shard-03-rs-config.js
echo "Replica set configured for Shard 03"
