import pymysql
import re
from z3 import *


def connect():
    # your own database here
    conn = pymysql.connect(host="", user="", password="", database="", charset="")
    cursor = conn.cursor()
    return conn, cursor


# Expression conversion format of the database
def trans(z3exp=''):
    if z3exp == '':
        z3exp = "oven == 1"
    if z3exp.find('>=') > -1:
        attr = z3exp.split('>=')[0].strip()
        val = z3exp.split('>=')[1].strip()
        exp = Int(attr) >= val
    elif z3exp.find('<=') > -1:
        attr = z3exp.split('<=')[0].strip()
        val = z3exp.split('<=')[1].strip()
        exp = Int(attr) <= val
    elif z3exp.find('>') > -1:
        attr = z3exp.split('>')[0].strip()
        val = z3exp.split('>')[1].strip()
        exp = Int(attr) > val
    elif z3exp.find('<') > -1:
        attr = z3exp.split('<')[0].strip()
        val = z3exp.split('<')[1].strip()
        exp = Int(attr) < val
    elif z3exp.find('!=') > -1:
        attr = z3exp.split('!=')[0].strip()
        val = z3exp.split('!=')[1].strip()
        exp = Int(attr) != val
    elif z3exp.find('==') > -1:
        attr = z3exp.split('==')[0].strip()
        val = z3exp.split('==')[1].strip()
        exp = Int(attr) == val
    else:
        exp = 'unknown format'
    return exp


# Separate numbers from ids in applets
def getIDnums(idstr=''):
    res = []
    if idstr == '':
        idstr = "['24','25']"
    # res = list(IDs)
    ids = idstr.split('[')[1].split(']')[0].split(',')
    for num in ids:
        num = num.strip()
        res.append(int(num.strip("'").strip('"')))
    return res


# Get the corresponding z3exp from the digital id
def getexp(atid, char):
    conn, cursor = connect()
    if char == 'A' or char == 'a':
        sql = '''select z3exp from actions where actionID="{}"'''.format(atid)
    elif char == 'T' or char == 't':
        sql = '''select z3exp from triggers where triggerID="{}"'''.format(atid)
    else:
        return "unknown char"
    cursor.execute(sql)
    res = cursor.fetchone()
    conn.close()
    if res is None:
        return "unknown ID"
    else:
        return res[0]


# Get exp from id
def getoexp(atid, char):
    conn, cursor = connect()
    if char == 'A' or char == 'a':
        sql = '''select exp from actions where actionID="{}"'''.format(atid)
    elif char == 'T' or char == 't':
        sql = '''select exp from triggers where triggerID="{}"'''.format(atid)
    else:
        return "unknown char"
    cursor.execute(sql)
    res = cursor.fetchone()
    conn.close()
    if res is None:
        return "unknown ID"
    else:
        return res[0]
