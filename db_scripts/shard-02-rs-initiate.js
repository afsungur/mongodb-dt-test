rs.initiate(
  {
    _id: "shard-02-replica-set",
    members: [
      { _id : 0, host : "localhost:24001" },
      { _id : 1, host : "localhost:24002" },
      { _id : 2, host : "localhost:24003" }
    ]
  }
)
