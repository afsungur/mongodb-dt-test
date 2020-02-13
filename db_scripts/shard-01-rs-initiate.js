rs.initiate(
  {
    _id: "shard-01-replica-set",
    members: [
      { _id : 0, host : "localhost:23001" },
      { _id : 1, host : "localhost:23002" },
      { _id : 2, host : "localhost:23003" }
    ]
  }
)
