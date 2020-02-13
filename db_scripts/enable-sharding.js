sh.enableSharding('crm')
db.adminCommand({ shardCollection: 'crm.order', key: {"customerId": "hashed"}})
db.adminCommand({ shardCollection: 'crm.account', key: {"customerId": "hashed"}})
db.adminCommand({ shardCollection: 'crm.subscription', key: {"customerId": "hashed"}})
