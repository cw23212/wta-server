from db import influx

from core import db_config

def B(bucket, measurement):    
    return f"""
    from(bucket: "{bucket}")
     |> filter(fn: (r) => r._measurement == "{measurement}")
     |> range(start: -inf)
     |> limit(n: 20) 
    """

def Fsid(v):
    return f"""
     |> filter(fn: (r) => r.sid == "{v}")
    """
def Fpage(v):
    return f"""
     |> filter(fn: (r) => r.page == "{v}")
    """

def Ftype(v):
    return f"""
     |> filter(fn: (r) => r.type == "{v}")
    """

def sumExpression(page):
    type = "exp"
    query =  B("b1","measurement1") 
    query += Ftype("exp")
    query += Fpage(page)
    query += """
        |> group(columns: ["_field"])
        |> mean()
    """    
    influx.read(query)

    
def sumExpression(page):
    type = "exp"
    query =  B("b1","measurement1") 
    query += Ftype("exp")
    query += Fpage(page)
    query += """
        |> group(columns: ["_field"])
        |> mean()
    """    
    influx.read(query)