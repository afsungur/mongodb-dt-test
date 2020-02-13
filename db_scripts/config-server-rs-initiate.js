rs.initiate(
  {
    _id: "config-server-replica-set",
    configsvr: true,
    members: [
      { _id : 0, host : "localhost:21001" },
      { _id : 1, host : "localhost:21002" },
      { _id : 2, host : "localhost:21003" }
    ]
  }
)
