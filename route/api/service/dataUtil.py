from typing import List

def convertInf(d, key="le", value="inf"):
    for i in d:
        if i[key] == float("inf"):
            i[key] = value
    return d

from datetime import datetime, timedelta
def addRangeDate(d, day, value={}) -> List:
    start = datetime.now() - timedelta(days=day)
    
    days = { i["_start"].date() : i for i in d}
    res = []
    for i in range(day+1):
        cdate = start + timedelta(days=i)
        if cdate.date() in days:
            res.append(days[cdate.date()])
        else:
            n = {"_start":cdate}
            n.update(value)
            res.append(n)
    return res