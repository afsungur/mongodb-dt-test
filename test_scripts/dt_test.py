#!/usr/bin/python3
import sys
import random
import time
import datetime
import pymongo
import json
import string
import configparser
import concurrent.futures
import logging
import os
import mongodb_util

# global variables
MAXIMUM_CUSTOMER_ID=1000
total_number_of_updates=0
total_number_of_inserts=0
total_number_of_transactions=0
config=None
should_kill_primaries=None
should_kill_mongos=None
should_kill_itself=None
already_killed=False
callback_api=True

def set_logger():
    """Sets the logger parameters from configuration file

        Parameters
        ----------
        config : Object
            Configuration file content holder

    """
    global config
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

def set_failure_parameters():
    """Sets the failure parameters from configuration file

        Parameters
        ----------
        config : Object
            Configuration file content holder

    """
    global config
    global should_kill_primaries
    global should_kill_mongos
    global should_kill_itself
    should_kill_primaries_str=str(config['FAIL']['kill'])
    should_kill_primaries=True if should_kill_primaries_str in ('primaries','PRIMARIES') else False

    should_kill_mongos_str=str(config['FAIL']['kill'])
    should_kill_mongos=True if should_kill_mongos_str in ('mongos','MONGOS') else False

    should_kill_itself_str=str(config['FAIL']['kill'])
    should_kill_itself=True if should_kill_itself_str in ('itself','ITSELF') else False

####
# Main start function
####

def set_config():
    global config
    config = configparser.ConfigParser()
    config.read('config.properties')

def main():
    logging.info("====================================================================================================================================")

    #failure parameters settings e.g. Primaries kill, mongos kill
    set_failure_parameters()

    mongodb_util.init()
    mongodb_uri=config['URI']['mongos']
    connect_timeout=int(config['URI']['mongosSelectionTimeoutMS'])

    number_of_transactions=int(config['PARAMS']['numberOfTransactions'])
    number_of_order_items=int(config['PARAMS']['numberOfOrderItemsPerTransaction'])
    number_of_threads=int(config['PARAMS']['numberOfThreads'])


    connection = pymongo.MongoClient(mongodb_uri, connectTimeoutMS=connect_timeout)

    logging.info("====================================================================================================================================")
    logging.info("COUNTS BEFORE TRANSACTIONS:")
    print_counts(connection)
    print_counts_per_shard()


    logging.info("====================================================================================================================================")
    logging.info(f"Test is being started with {number_of_threads} thread(s) ...")
    future_list = []
    start_millisecond = int(round(time.time() * 1000))
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_threads, thread_name_prefix="Thread") as executor:
        for index in range(number_of_threads):
            if (callback_api):
                future = executor.submit(perform_insert, mongodb_uri, number_of_transactions, number_of_order_items)
            else:
                future = executor.submit(perform_insert_no_cb, mongodb_uri, number_of_transactions, number_of_order_items)
            logging.debug(f"Thread {index} has been created ...")

    end_millisecond = int(round(time.time() * 1000))
    total_duration_ms = end_millisecond-start_millisecond
    throughput = round(number_of_transactions*number_of_threads/(total_duration_ms/1000),2)

    logging.info("============================================")
    logging.info(f"[ALL THREADS] Throughput: {throughput} transactions per second")
    logging.info("============================================")
    logging.info("====================================================================================================================================")
    logging.info("COUNTS AFTER TRANSACTIONS:")
    print_counts(connection)
    print_counts_per_shard()

def randomString(stringLength):
    """Generate a random string

        Parameters
        ----------
        string_length : string
            Length of the generated string

    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def print_counts_collection(collection_order,collection_account,collection_subscription,collection_resource,session):
    """Prints the counts for the four collections in a given session unless the session parameter is null

        Parameters
        ----------
        collection_order : collection
        collection_account : collection
        collection_subscription : collection
        collection_resource : collection
        session: ClientSession

        """
    count_free_resource=collection_resource.count_documents({"type":"IMSI", "status":"FREE"},session)
    count_reserved_resource=collection_resource.count_documents({"type":"IMSI", "status":"RESERVED"},session)
    count_order=collection_order.count_documents({},session)
    count_account=collection_account.count_documents({},session)
    count_subscription=collection_subscription.count_documents({},session)
    logging.info(f"Free Resource Count: {count_free_resource}")
    logging.info(f"Reserved Resource Count: {count_reserved_resource}")
    logging.info(f"Order Count: {count_order}")
    logging.info(f"Account Count: {count_account}")
    logging.info(f"Subscription Count: {count_subscription}")

def print_counts_for_shard(shard_no,uri):
    """Prints the counts for given shard

        Parameters
        ----------
        shard_no : int
            The number of shard just for printing purpose

        uri: string
            Connection string for the shard primary (not through mongos)

    """
    connection = pymongo.MongoClient(uri)
    logging.info("============================================")
    logging.info(f'For shard #{shard_no}, counts:')
    collection_order = connection.crm.order
    collection_account = connection.crm.account
    collection_subscription = connection.crm.subscription
    collection_resource = connection.crm.resource
    print_counts_collection(collection_order, collection_account, collection_subscription, collection_resource, None)
    logging.info("============================================")


def print_counts(connection):
    """Prints the counts for the four collections in the connection

        Parameters
        ----------
        connection : MongoClient
            connection parameter for printing

        """
    logging.info("============================================")
    logging.info(f'Entire database, counts:')
    collection_order = connection.crm.order
    collection_account = connection.crm.account
    collection_subscription = connection.crm.subscription
    collection_resource = connection.crm.resource
    print_counts_collection(collection_order, collection_account, collection_subscription, collection_resource, None)
    logging.info("============================================")

def print_counts_session(session):
    """Prints the counts for the four collections in the session

        Parameters
        ----------
        session : ClientSession
            session parameter for printing

        """

    logging.info("============================================")
    logging.info(f'Entire database, counts:')
    collection_order = session.client.crm.order
    collection_account = session.client.crm.account
    collection_subscription = session.client.crm.subscription
    collection_resource = session.client.crm.resource
    print_counts_collection(collection_order, collection_account, collection_subscription, collection_resource, session)
    logging.info("============================================")

def print_counts_per_shard():
    """Prints the counts for all shards"""
    print_counts_for_shard('01', config['URI']['shard01'])
    print_counts_for_shard('02', config['URI']['shard02'])
    print_counts_for_shard('03', config['URI']['shard03'])

def print_thread_throughput(start,end,num_of_tx):
    """Prints the throughput for a thread

        Parameters
        ----------
        start : long
            The millisecond of start time

        end: long
            The millisecond of end time

        num_of_tx: int
            Number of order transactions executed

        """
    diff=(end-start)/1000
    throughput=round(num_of_tx/diff)
    logging.debug(f"Total duration: {diff} seconds for {num_of_tx} transactions")
    logging.debug(f"Throughput: {throughput} transactions per second")



def perform_insert_no_cb(mongodb_uri, number_of_transactions, number_of_order_items):
    """Does the insert operations in a given thread with the parameters

        Parameters
        ----------
        mongodb_uri : string
            Connection string to the mongodb for the thread

        number_of_transactions: int
            Number of transactions are going to be executed in the session for the thread

        number_of_order_items: int
            Number of order items in each transaction

        """
    logging.info(f'Connecting to: {mongodb_uri}')
    connection = pymongo.MongoClient(mongodb_uri)

    # Each thread will have own session (only one)
    with connection.start_session() as session:
        start_millisecond = int(round(time.time() * 1000))
        # in one session we will execute this amount of transactions
        for transaction_number in range(1, number_of_transactions+1):
            logging.debug(f"Transaction {transaction_number} is going to be started ...")
            # Execute the callback function do_dt_tx and sends the parameters, number_of_order_items, transaction_number to this callback function
            
            try_count=0
            tx_failed=False       
            
            while(True):
                try:
                    with session.start_transaction(
                        read_concern=pymongo.read_concern.ReadConcern('snapshot'),
                        write_concern=pymongo.write_concern.WriteConcern("majority", wtimeout=1000),
                        read_preference=pymongo.read_preferences.ReadPreference.PRIMARY):

                        do_dt_tx(session, number_of_order_items, transaction_number)
                        logging.debug(f"Transaction {transaction_number} has been completed ...")
                        break    
                except (pymongo.errors.ConnectionFailure, pymongo.errors.OperationFailure) as e:
                    logging.error(f"It is either connection or operation failure: {str(e)}")
                    if (e.has_error_label("TransientTransactionError")):
                        logging.error("TRANSIENT ERROR, transaction is going to be retried again")
                        continue
                    else:
                        raise
                except:
                    logging.error("Unexpected error: ", sys.exc_info()[0])
                    tx_failed=True
                    break

            if (transaction_number%50==0 and transaction_number>0):
                logging.info(f"Transaction number {transaction_number} has been completed ...")
            
    end_millisecond = int(round(time.time() * 1000))
    print_thread_throughput(start_millisecond, end_millisecond, number_of_transactions) # logging.debug
    return start_millisecond, end_millisecond, number_of_transactions


def perform_insert(mongodb_uri, number_of_transactions, number_of_order_items):
    """Does the insert operations in a given thread with the parameters

        Parameters
        ----------
        mongodb_uri : string
            Connection string to the mongodb for the thread

        number_of_transactions: int
            Number of transactions are going to be executed in the session for the thread

        number_of_order_items: int
            Number of order items in each transaction

        """
    logging.info(f'Connecting to: {mongodb_uri}')
    connection = pymongo.MongoClient(mongodb_uri)

    # Each thread will have own session (only one)
    with connection.start_session() as session:
        start_millisecond = int(round(time.time() * 1000))

        # in one session we will execute this amount of transactions
        for transaction_number in range(1, number_of_transactions+1):
            logging.debug(f"Transaction {transaction_number} is going to be started ...")

            # Execute the callback function do_dt_tx and sends the parameters, number_of_order_items, transaction_number to this callback function
            session.with_transaction(
                lambda s: do_dt_tx(s, number_of_order_items, transaction_number, custom_kwarg=1),
                read_concern=pymongo.read_concern.ReadConcern('snapshot'),
                write_concern=pymongo.write_concern.WriteConcern("majority", wtimeout=1000),
                read_preference=pymongo.read_preferences.ReadPreference.PRIMARY
            )

            # after transaction finished successfully then it will continue here
            logging.debug(f"Transaction {transaction_number} has been completed ...")

            if (transaction_number%50==0 and transaction_number>0):
                logging.info(f"Transaction number {transaction_number} has been completed ...")

        end_millisecond = int(round(time.time() * 1000))
        print_thread_throughput(start_millisecond, end_millisecond, number_of_transactions) # logging.debug
        return start_millisecond, end_millisecond, number_of_transactions

def do_dt_tx(session, number_of_order_items, transaction_number, custom_kwarg=None):
    """Does the distributed transaction in a given session with the parameters
       Based on the global variables it performs the necessary failure scenarios

        Parameters
        ----------
        session : ClientSession
            Transaction is performed in this session

        number_of_order_items: int
            Number of order items in the transaction

        transaction_number: int
            The number of the transaction, is incremented by one by the caller
        """
    global should_kill_primaries
    global should_kill_mongos
    global already_killed
    global should_kill_itself
    logging.debug(f"Transaction number: {transaction_number} has been started ...")

    # collections that records will be inserted into
    collection_order = session.client.crm.order
    collection_account = session.client.crm.account
    collection_subscription = session.client.crm.subscription
    collection_resource = session.client.crm.resource

    # fetch random customer
    random_customer_id=random.randint(1,MAXIMUM_CUSTOMER_ID)
    fetched_account=collection_account.find_one({"customerId":random_customer_id})

    order_items=[]
    accounts=[]
    subscriptions=[]

    # for each order item there has to be one resource should be allocated
    #   it means that one of the resource document in the resource collection with the type:IMSI and status:FREE should be allocated
    #   allocation mean that updating that resource's status to RESERVED from FREE
    # for each order item there has to be one new account should be inserted into account collection
    # for each order item there has to be one new subscription should be inserted into subcription collection
    # and finally one order should be inserted into order collection together with the order_item object
    for i in range(number_of_order_items):
        resource=collection_resource.find_one_and_update(filter={"type": "IMSI", "status": "FREE"},update={"$set": {"status": "RESERVED"}},session=session)
        logging.debug(f"Resource collection has been updated (step: {i})...")
        product= { "quantity": random.randint(1,5),
                   "productCode1" : randomString(7),
                   "productCode2" : randomString(7),
                   "productSpecId" : random.randint(1,10000),
                   "resource" : resource
                }
        order_item = { "type": "PRODUCT ADD", "product" : product }
        order_items.append(order_item)
        subscription = {
            "customerId" : fetched_account["customerId"],
            "accountId" : fetched_account['accountId'],
            "product" : product
            }
        subscriptions.append(subscription)
        account = {
            "accountStatus" : "ACTIVE",
            "customerId" : fetched_account['customerId'],
            "createdDate" : datetime.datetime.now(),
            "modifiedDate" : datetime.datetime.now(),
            "imsi" : random.randint(1000000,2000000),
            "category" : "FIRST_CLASS",
            "invoice" : { "invoiceLanguage" : "ENGLISH"}
        }
        accounts.append(account)

    order = {
        "accountId" : fetched_account['accountId'],
        "customerId" : fetched_account['customerId'],
        "orderItems" : order_items,
        "createdDate" : datetime.datetime.now(),
        "modifiedDate" : datetime.datetime.now(),
        "username" : randomString(10),
        "orderStatus" : "CREATED"
    }

    mongos_uri=session._pinned_address # like: ('localhost', 30001)
    result_subscription=collection_subscription.insert_many(subscriptions,session=session)
    logging.debug(f"{len(result_subscription.inserted_ids)} documents have been inserted into subscription collection")
    logging.debug(f"Are the primaries going to be killed: {should_kill_primaries}")

    if (transaction_number==5 and should_kill_primaries and not already_killed):
        logging.warning(f"[Transaction number: {transaction_number}, primaries are going to be killed now!]")
        mongodb_util.show_replica()
        mongodb_util.kill_primaries()
        already_killed=True
        time.sleep(5)
        mongodb_util.show_replica()

    logging.debug(f"Is the pinned mongos going to be killed: {should_kill_mongos}")
    if (transaction_number==5 and should_kill_mongos and not already_killed):
        logging.warning(f"Transaction number: {transaction_number}, pinned mongos is going to be killed soon!")
        logging.debug(f"Pinned mongos address: {session._pinned_address}")
        logging.debug(f"Read preference of transaction: {session._transaction.opts.read_preference}")
        logging.debug(f"Is that sharded transaction: {session._transaction.sharded}")
        logging.debug(f"mongos address: {mongos_uri}")
        mongos_host, mongos_port = mongos_uri
        logging.debug(f"Pinned mongos running on port {mongos_port}")
        mongodb_util.show_available_mongoses()
        logging.warning("Pinned mongos is going to be killed right now!")
        mongodb_util.kill_mongos(mongos_port)
        already_killed=True
        time.sleep(3)
        mongodb_util.show_available_mongoses()

    result_account=collection_account.insert_many(accounts,session=session)
    logging.debug(f"{len(result_account.inserted_ids)} documents have been inserted into account collection")

    if (transaction_number==5 and should_kill_itself):
        logging.warning(f"[Transaction number: {transaction_number}, thread itself will be killed")
        logging.debug("Killing the distributed transaction thread ...")
        sys.exit(1) # only kills the thread, keeps the process alive

    result_order=collection_order.insert_one(order,session=session)
    logging.debug(f"ObjectId('{result_order.inserted_id}') Order document has been inserted into order collection")
    logging.debug(f"Pinned mongos for this transaction: {mongos_uri}")


if __name__ == '__main__':
    set_config()
    set_logger()
    if (len(sys.argv) > 1):
        param=sys.argv[1].strip()
        if param == "COUNT":
            logging.info("Counts will be printed...")
            mongodb_uri=config['URI']['mongos']
            connection = pymongo.MongoClient(mongodb_uri)
            print_counts(connection)
        elif param == "NO_CB":
            logging.info("Callback API Will not be used ...")
            callback_api=False
            main()
    else:
        main()
