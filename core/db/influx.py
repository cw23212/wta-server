import logging
import os
import time
import functools
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS, WriteOptions
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.domain.write_precision import WritePrecision

from core.secret.db_config import *

logger = logging.getLogger("wta." + __name__)

client = None
def startClient():
    global client
    client = InfluxDBClientAsync(url=url, token=token, org=org)
    return client



# @functools.cache
def getWriteApi():
    write_api = client.write_api()
    return write_api



async def write(bucket, points):
    res = await getWriteApi().write(bucket=bucket
    , org=org
    , record=points
    , write_precision = WritePrecision.US)
    logger.debug(f"influx wrtie {points} - {res}")
    # write_api.flush()


def writeSync(bucket, points):
    client = InfluxDBClient(url=url, token=token, org=org)
    with client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        with write_api:
            res = write_api.write(
                bucket=bucket,
                org=org,
                record=points,
            )
            logger.debug(f"influx wrtie {points} - {res}")
    # write_api.flush()

async def read(query, columns=None):
    try:
        tables = await client.query_api().query(query)
        logger.debug(f"influx read {query} - {len(tables)}")    
        tables = tables.to_values(columns=columns)    
        res = [ i.mapping.copy() for i in tables]
        for i in res:
            del i["result"]
        return res
    except Exception as e:        
        logger.error(e)
        raise e
    

def readSync(query):
    client = InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()
    tables = query_api.query(query)  
    tables = tables.to_values()    
    return [ i.mapping.copy() for i in tables]


def tableToJson(table):
    json_data = []

    for record in table.records:
        print(type(record))
        json_data.append(
            {                
                "fields": {"tag": record.get_field(), "value": record.get_value()},
                "time": record.get_time(),  # can be shaped as you like, e.g. ISO with .replace(tzinfo=None).isoformat()+'Z'
            }
        )
    return json_data

def tablesToJson(tables):
    return [ tableToJson(i) for i in tables ]
