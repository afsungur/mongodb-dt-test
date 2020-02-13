use crm
db.account.createIndex({customerId: 1});
db.resource.createIndex({type:1, status: 1});
db.customer.createIndex({customerId:1});
