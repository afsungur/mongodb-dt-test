mongod -f config-server-repl-set-01.yaml
sleep 5
echo "Started 1st replica of config server..."
mongod -f config-server-repl-set-02.yaml
sleep 5
echo "Started 2nd replica of config server..."
mongod -f config-server-repl-set-03.yaml
sleep 5
echo "Started 3rd replica of config server..."
mongo --port 21001 < config-server-rs-initiate.js
echo "Config server replica set initiated ..."
