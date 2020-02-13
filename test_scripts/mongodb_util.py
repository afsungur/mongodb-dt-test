#!/usr/bin/python3
import sys
import pymongo
import psutil
from signal import SIGTERM, SIGKILL
import configparser
import logging
import os

connection_shard_01=None
connection_shard_02=None
connection_shard_03=None

def set_logger(config):
    """Sets the logger parameters from configuration file

        Parameters
        ----------
        config : Object
            Configuration file content holder

    """
    verbose_str=str(config['PARAMS']['verbose'])
    logging_level=logging.DEBUG if verbose_str in ('true','True') else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="[%(asctime)s][%(threadName)-12.12s][%(levelname)-5.5s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )

def set_shard_connections(config):
    """Sets global shard connection variables

        Parameters
        ----------
        config : Object
            Configuration file content holder

    """
    global connection_shard_01, connection_shard_02, connection_shard_03
    connection_shard_01 = pymongo.MongoClient(config['URI']['shard01'])
    connection_shard_02 = pymongo.MongoClient(config['URI']['shard02'])
    connection_shard_03 = pymongo.MongoClient(config['URI']['shard03'])


def get_primary_ports():
    """Returns the port numbers of primary members of each shard"""
    shard_01_msg=connection_shard_01.admin.command('replSetGetStatus')
    shard_02_msg=connection_shard_02.admin.command('replSetGetStatus')
    shard_03_msg=connection_shard_03.admin.command('replSetGetStatus')

    members_01=shard_01_msg['members']
    members_02=shard_02_msg['members']
    members_03=shard_03_msg['members']
    shard_01_master=None
    shard_02_master=None
    shard_03_master=None

    for member in members_01:
        if (member['stateStr'] == 'PRIMARY'):
            shard_01_master=member['name']

    for member in members_02:
        if (member['stateStr'] == 'PRIMARY'):
            shard_02_master=member['name']

    for member in members_03:
        if (member['stateStr'] == 'PRIMARY'):
            shard_03_master=member['name']

    pieces=shard_01_master.split(":")
    shard_01_primary_port=pieces[1]

    pieces=shard_02_master.split(":")
    shard_02_primary_port=pieces[1]

    pieces=shard_03_master.split(":")
    shard_03_primary_port=pieces[1]
    return shard_01_primary_port, shard_02_primary_port, shard_03_primary_port
    
def show_replica():
    """Prints the replica set member statuses, primary node and secondary nodes"""
    shard_01_msg=connection_shard_01.admin.command('replSetGetStatus')
    shard_02_msg=connection_shard_02.admin.command('replSetGetStatus')
    shard_03_msg=connection_shard_03.admin.command('replSetGetStatus')

    members_01=shard_01_msg['members']
    members_02=shard_02_msg['members']
    members_03=shard_03_msg['members']
    shard_01_master=None
    shard_02_master=None
    shard_03_master=None

    for member in members_01:
        if (member['stateStr'] == 'PRIMARY'):
            shard_01_master=member['name']

    for member in members_02:
        if (member['stateStr'] == 'PRIMARY'):
            shard_02_master=member['name']

    for member in members_03:
        if (member['stateStr'] == 'PRIMARY'):
            shard_03_master=member['name']

    pieces=shard_01_master.split(":")
    shard_01_primary_port=pieces[1]

    pieces=shard_02_master.split(":")
    shard_02_primary_port=pieces[1]

    pieces=shard_03_master.split(":")
    shard_03_primary_port=pieces[1]

    logging.info("===========================================================================")
    for member in members_01:
        logging.info(f"For shard 01,  IP and Port and Status of this member: {member['name']} , {member['stateStr']}")

    logging.info("===========================================================================")
    for member in members_02:
        logging.info(f"For shard 02,  IP and Port and Status of this member: {member['name']} , {member['stateStr']}")

    logging.info("===========================================================================")
    for member in members_03:
        logging.info(f"For shard 03,  IP and Port and Status of this member: {member['name']} , {member['stateStr']}")

def get_process_id(portnum):
    fp = os.popen("lsof -i :%s -sTCP:LISTEN" % portnum)
    lines = fp.readlines()
    fp.close()
    pid = None
    if len(lines) >= 2:
        pid = int(lines[1].split()[1])
    return pid

def kill_primaries_with_port(shard_01_primary_port, shard_02_primary_port, shard_03_primary_port):
    """Kills the primaries of each shard
           It finds the process ids by looking for the process list based on given port numbers

        Parameters
        ----------
        shard_01_primary_port : int
            Port number of the primary of shard 01

        shard_02_primary_port : int
            Port number of the primary of shard 02

        shard_03_primary_port : int
            Port number of the primary of shard 03

        """   
    logging.info("Masters are going to be killed")
    logging.info("================================================================================")
    pid_01 = get_process_id(shard_01_primary_port)
    logging.info(f"Process ID for shard 01-primary: {pid_01}")
    proc = psutil.Process(pid_01)
    proc.kill()
    logging.info("Killed the process for shard 01")

    pid_02 = get_process_id(shard_02_primary_port)
    logging.info(f"Process ID for shard 02-primary: {pid_02}")
    proc = psutil.Process(pid_02)
    proc.kill()
    logging.info("Killed the process for shard 02")

    pid_03 = get_process_id(shard_03_primary_port)
    logging.info(f"Process ID for shard 03-primary: {pid_03}")
    proc = psutil.Process(pid_03)
    proc.kill()
    logging.info("Killed the process for shard 03")

def kill_primaries():
    """Kills the all primaries of each shard"""
    logging.warning("Primaries are going to be killed ...")
    shard_01_primary_port, shard_02_primary_port, shard_03_primary_port = get_primary_ports()
    logging.debug(f"Shard-01 primary port: {shard_01_primary_port}")
    logging.debug(f"Shard-02 primary port: {shard_02_primary_port}")
    logging.debug(f"Shard-03 primary port: {shard_03_primary_port}")
    kill_primaries_with_port(shard_01_primary_port, shard_02_primary_port, shard_03_primary_port)

def kill_mongos(mongos_port):
    """Kills the mongos which is running on given port

        Parameters
        ----------
        mongos_port : int
            Port number of the mongos
    """
    pid = get_process_id(mongos_port)
    logging.info("================================================================================")
    logging.info(f"Kill the mongos process on given port {mongos_port}")
    proc = psutil.Process(pid)
    proc.send_signal(SIGKILL)
    logging.info("================================================================================")
    

def show_available_mongoses():
    """Prints the available mongoses"""
    logging.info("================================================================================")
    logging.info("Available Mongoses:")
    pid = get_process_id(30001)
    logging.info(f"For the port: 30001, this is the process id: {pid}")

    pid = get_process_id(30002)
    logging.info(f"For the port: 30002, this is the process id: {pid}")

    pid = get_process_id(30003)
    logging.info(f"For the port: 30003, this is the process id: {pid}")
    logging.info("================================================================================")



def init():
    config = configparser.ConfigParser()
    config.read('config.properties')

    #logging settings
    set_logger(config)
    set_shard_connections(config)

if __name__ == '__main__':
    init()
    param=sys.argv[1].strip()
    if param == "KILL_PRIMARIES":
        kill_primaries()
    elif param == "SHOW_REPLICAS":
        show_replica()
    elif param == "SHOW_MONGOSES":
        show_available_mongoses()

