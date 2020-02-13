cfg=rs.config()
cfg.settings.heartbeatIntervalMillis=1000
cfg.settings.heartbeatTimeoutSecs=1
cfg.settings.electionTimeoutMillis=1000
rs.reconfig(cfg, {force:true})
