import pymysql
import json
import io
input = b""
with open(r"E:\Prem\python\delta\controlRoomDatabase.json", "rb") as f:
    print(f.readable())
    input = f.read()



def _json_decode(json_bytes, encoding):
    tiow = io.TextIOWrapper(
        io.BytesIO(json_bytes), encoding=encoding, newline=""
    )
    obj = json.load(tiow)
    tiow.close()
    return obj

data = _json_decode(input, "utf-8-sig")
print(data)

#db = pymysql.connect("localhost", "username", "password", "college")
#cursor = db.cursor()

db = pymysql.connect("localhost","username","password","controlRoom")
cursor = db.cursor()

def columns():
    global columnQueries
    columnQueries = ""

    for props in values["properties"]:


        if ("nullable" in props["metadata"].keys() and props["metadata"]["nullable"] == False):
            if(props["type"] == "timestamp"):
                sql_addC = f'{props["name"]} DATETIME NOT NULL,\n    '

            if (props["type"] == "number"):
                dataType = 'int' if (props["metadata"]["subtype"] == "integer") else 'float'
                lowerL = props["metadata"]["lowerlimit"]
                upperL = props["metadata"]["upperlimit"]

                if ("value" in props["metadata"].keys()):
                    if (props["metadata"]["settable"] == False):
                        sql_addC = f'{props["name"]} {dataType} NOT NULL {props["name"]}={props["metadata"]["value"]},\n    '
                    else:
                        sql_addC = f'{props["name"]} {dataType} NOT NULL CHECK({props["name"]} IN {props["metadata"]["values"]}),\n    '

                else:
                    sql_addC = f'{props["name"]} {dataType} NOT NULL CHECK({props["name"]}>={lowerL} && {props["name"]}<={upperL}),\n    '

            elif (props["type"] == "string"):
                maxL = props["metadata"]["maximumLength"]
                minL = props["metadata"]["minimumLength"]

                if ("value" in props["metadata"].keys()):
                    if ("settable" in props["metadata"].keys() and props["metadata"]["settable"]):
                        sql_addC = f'{props["name"]} nvarchar({maxL}) NOT NULL CHECK({props["name"]} IN {props["metadata"]["values"]}),\n    '
                    else:
                        sql_addC = f'{props["name"]} nvarchar({maxL}) NOT NULL CHECK({props["name"]}=={props["metadata"]["value"]}),\n    '
                else:
                    sql_addC = f'{props["name"]} nvarchar({maxL}) NOT NULL CHECK(len({props["name"]})>={minL}),\n    '

            #try:
            #    cursor.execute(sql_addC)
            #    db.commit()
            #except:
            #    db.rollback()'''*

        elif("nullable" not in props["metadata"].keys()):
            if(props["type"] == "timestamp"):
                sql_addC = f'{props["name"]} DATETIME ,\n    '

            if (props["type"] == "number"):
                dataType = 'int' if (props["metadata"]["subtype"] == "integer") else 'float'
                lowerL = props["metadata"]["lowerlimit"]
                upperL = props["metadata"]["upperlimit"]

                if ("value" in props["metadata"].keys()):
                    if (props["metadata"]["settable"] == False):
                        sql_addC = f'{props["name"]} {dataType} {props["name"]}={props["metadata"]["value"]},\n    '
                    else:
                        sql_addC = f'{props["name"]} {dataType} CHECK({props["name"]} IN {props["metadata"]["values"]}),\n    '

                else:
                    sql_addC = f'{props["name"]} {dataType} CHECK({lowerL}<={props["name"]}<={upperL}),\n    '

            elif (props["type"] == "string"):
                maxL = props["metadata"]["maximumLength"]
                minL = props["metadata"]["minimumLength"]

                if ("value" in props["metadata"].keys()):
                    if ("settable" in props["metadata"].keys() and props["metadata"]["settable"]):
                        sql_addC = f'{props["name"]} nvarchar({maxL}) CHECK({props["name"]} IN {props["metadata"]["values"]}),\n    '
                    else:
                        sql_addC = f'{props["name"]} nvarchar({maxL}) CHECK({props["name"]}=={props["metadata"]["value"]}),\n    '
                else:
                    sql_addC = f'{props["name"]} nvarchar({maxL}) CHECK({minL}<=len({props["name"]})),\n    '
        columnQueries+=sql_addC
    return columnQueries[:len(columnQueries)-6]

for values in data["defintions"]:
    sql_table = f'''CREATE TABLE {values["name"]}(
    id int AUTO_INCREMENT,
    PRIMARY KEY(id),
    {columns()}
);'''
    print(sql_table)
    try:
        cursor.execute(sql_table)
        db.commit()
    except:
        db.rollback()
db.close()
