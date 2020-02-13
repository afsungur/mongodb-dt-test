mongod -f shard-01-repl-set-01.yaml
sleep 3
mongod -f shard-01-repl-set-02.yaml
sleep 3
mongod -f shard-01-repl-set-03.yaml
sleep 3
mongod -f shard-02-repl-set-01.yaml
sleep 3
mongod -f shard-02-repl-set-02.yaml
sleep 3
mongod -f shard-02-repl-set-03.yaml
sleep 3
mongod -f shard-03-repl-set-01.yaml
sleep 3
mongod -f shard-03-repl-set-02.yaml
sleep 3
mongod -f shard-03-repl-set-03.yaml
sleep 3
