mongod -f shard-01-repl-set-01.yaml
sleep 5
echo "Started Shard 01 - Replica 01 ..."
mongod -f shard-01-repl-set-02.yaml
sleep 5
echo "Started Shard 01 - Replica 02 ..."
mongod -f shard-01-repl-set-03.yaml
sleep 5
echo "Started Shard 01 - Replica 03 ..."
mongo --port 23001 < shard-01-rs-initiate.js
echo "Replica set initiated for Shard 01"
mongo "mongodb://localhost:23001,localhost:23002,localhost:23003/?readPreference=primary" < shard-01-rs-config.js
echo "Replica set configured for Shard 01"
