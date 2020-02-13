rs.initiate(
  {
    _id: "shard-03-replica-set",
    members: [
      { _id : 0, host : "localhost:25001" },
      { _id : 1, host : "localhost:25002" },
      { _id : 2, host : "localhost:25003" }
    ]
  }
)
