import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions

# token = os.environ.get("INFLUXDB_TOKEN")
org = "o1"
url = "http://n1.psj2867.com:8086"
token = "JrPx-xreXdq9KgOL0-o4agrFxsnnuMTcSuqVPX1sTaRLN3Z7lL3MMT18_9aKCQ48larUY64lxOsYdG4MqIvyuw=="

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org,)


bucket="b1"
def write(i):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    point = (
        Point("measurement1")
        .tag("tagname1", "tagvalue1")
        .tag("tagname2", "tagvalue2")
        .field("field1",i )
        .field("field2", "value2")
    )
    write_api.write(bucket=bucket, org="o1", record=point)
    write_api.flush()
[ write(i) for i in range(50) ]

# def read():
#     query_api = client.query_api()

#     query = """from(bucket: "b1")
#      |> range(start: -10m)
#      |> filter(fn: (r) => r._measurement == "measurement1")"""
#     tables = query_api.query(query, org="o1")

#     print(tables)


# read()