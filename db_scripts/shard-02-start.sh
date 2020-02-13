mongod -f shard-02-repl-set-01.yaml
sleep 5
echo "Started Shard 02 - Replica 01 ..."
mongod -f shard-02-repl-set-02.yaml
sleep 5
echo "Started Shard 02 - Replica 02 ..."
mongod -f shard-02-repl-set-03.yaml
sleep 5
echo "Started Shard 02 - Replica 03 ..."
mongo --port 24001 < shard-02-rs-initiate.js
echo "Replica set initiated for Shard 02"
mongo "mongodb://localhost:24001,localhost:24002,localhost:24003/?readPreference=primary" < shard-02-rs-config.js
echo "Replica set configured for Shard 02"
