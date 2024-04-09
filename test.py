from db import influx
from core.db_config import *
points = [
    {
        "measurement" : "tmp",
        "tags" : {
            "sid" : "1",
            "page" : "a.com"
        },
        "fields" : {
            "h":.4,
            "a":.4,
            "s":.4,
            "d":.4,
            "n":.4,
        }
    },
]

influx.writeSync("b1",points)