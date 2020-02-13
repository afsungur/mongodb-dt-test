mgeneratejs account_template.json -n 10000 | mongoimport --port 30001 --db crm --collection account &
mgeneratejs customer_template.json -n 1000 | mongoimport --port 30001 --db crm --collection customer &
mgeneratejs order_template.json -n 10000 | mongoimport --port 30001 --db crm --collection order &
mgeneratejs resource_template.json -n 5000000 | mongoimport --port 30001 --db crm --collection resource &
mgeneratejs subscription_template.json -n 100000 | mongoimport --port 30001 --db crm --collection subscription &
