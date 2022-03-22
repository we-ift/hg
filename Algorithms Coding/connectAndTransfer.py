# -*- coding:utf-8 -*-
from functools import reduce
from os import curdir
import pymysql
from z3 import *

def connect():
    return pymysql.connect(host="hostIP",user="username",password="pwd",database="ifttt" )

# ['ruleId', 'ruleName', 'conditionIds', 'actionIds','dayofweeks','starttime','endtime']
def getAllRules(db, userId=''):
    cursor = db.cursor()
    if userId == '':
        cursor.execute("SELECT * FROM t_rule")
        rule = cursor.fetchall()
    else:
        try:
            cursor.execute("SELECT * FROM t_rule WHERE userId = '" + str(userId) + "'")
            rule = cursor.fetchall()
        except:
            rule = []
    return rule

# def getAllRules(db,userId,sceneId):
#     cursor = db.cursor()
#     rule = []
#     if userId and sceneId:
#         try:
#             cursor.execute("SELECT * FROM t_rule WHERE userId = '" + str(userId) +\
#                  "' AND sceneid = '" + str(sceneId) + "'")
#             rule = cursor.fetchall()
#         except:
#             pass
#     return rule

# ['conditionIds', 'deviceId', 'attribute', 'compareType', 'standardValue']
def getCondition(Cid, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_condition WHERE conditionId = '" + str(Cid) + "'")
    con = cursor.fetchone()
    if con == None:
        con = True
    return con


def getConbyDev(Did, db):
    Did = str(Did)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_condition WHERE deviceId = '" + str(Did) + "'")
    con = cursor.fetchall()
    if con == None:
        con = True
    # db.close()
    return con


# ['actionId', 'deviceId', 'attribute', 'newValue', 'oldValue']
def getAction(Aid, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_action WHERE actionId = '" + str(Aid) + "'")
    act = cursor.fetchone()
    if act == None:
        act = True
    return act


def getActbyDev(Did, db):
    Did = str(Did)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_action WHERE deviceId = '" + str(Did) + "'")
    act = cursor.fetchall()
    if act == None:
        act = True
    return act


def getActbyAttr(a1, a2, a3, db):
    cursor = db.cursor()
    cursor.execute("SELECT actionId FROM t_action WHERE deviceId = '" + str(a1) + "'" \
                   + " and attribute = '" + str(a2) + "'" + "and newValue = '" + str(a3) + "'")
    act = cursor.fetchall()
    return act


def getRule(Rid, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_rule WHERE ruleId = '" + str(Rid) + "'")
    rl = cursor.fetchone()
    if rl == None:
        rl = True
    return rl

# deviceId deviceUuid deviceName categoryId readOnlyId readOnlyAttributes commonAttributes 
def getDevice(Did, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_device WHERE deviceId = '" + str(Did) + "'")
    dev = cursor.fetchone()
    if dev == None:
        dev = True
    return dev


# ['actionId', 'deviceId', 'attribute', 'newValue']
def getDevEffect(Did, attribute, newValue, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_entity WHERE deviceId = '" + str(Did) + "'" \
                   + "and attribute = '" + str(attribute) + "'" + "and newValue = '" + str(newValue) + "'")
    effect = cursor.fetchone()
    return effect


# 获取所有specification
def getAllSpec(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_spec")
    spec = cursor.fetchall()
    return spec


#
def getSpecAction(spec, db):
    actId = []
    cursor = db.cursor()
    cursor.execute("SELECT actionId FROM t_action WHERE deviceId = '" + str(spec[0]) + "'" \
                   + "and attribute = '" + str(spec[1]) + "' and newValue = '" + str(spec[2]) + "'")
    act = cursor.fetchall()
    for a in act:
        actId.append(str(a[0]))
    return actId


def getSpecCon(spec, db):
    conId = []
    cursor = db.cursor()
    cursor.execute("SELECT conditionId FROM t_condition WHERE deviceId = '" + str(spec[0]) + "'" \
                   + "and attribute = '" + str(spec[1]) + "' and standardValue = '" + str(spec[2]) + "'")
    con = cursor.fetchall()
    for c in con:
        conId.append(str(c[0]))
    return conId


def getNotCon(spec, db):
    conId = []
    cursor = db.cursor()
    cursor.execute("SELECT actionId FROM t_action WHERE deviceId = '" + str(spec[0]) + "'" \
                   + "and attribute = '" + str(spec[1]) + "' and newValue <> '" + str(spec[2]) + "'")
    actId = cursor.fetchall()
    if str(actId) != '()':
        for aid in actId:
            cursor.execute("SELECT conditionId FROM t_rule WHERE actionIds = '" + str(aid) + "'")
            cid = cursor.fetchall()
            for c in cid:
                conId.append(str(c[0]))
    return conId


# 把条件转换成Z3表达式
# ['conditionIds', 'deviceId', 'attribute', 'compareType', 'standardValue']
def conditionToZ3(condition):
    if not condition == None and not condition == True:
        x = Int((str(condition[1]) + ":" + str(condition[2])).encode('utf-8'))
        # print(condition[4])
        # 1是等于
        if condition[3] == 1:
            con = x == condition[4]
        # 2是大于
        elif condition[3] == 2:
            con = x > condition[4]
        # 3是小于
        elif condition[3] == 3:
            con = x < condition[4]
        # 4是大于等于
        elif condition[3] == 4:
            con = x >= condition[4]
        # 5是小于等于
        elif condition[3] == 5:
            con = x <= condition[4]
        # 6是不等于
        elif condition[3] == 6:
            con = x != condition[4]
        else:
            con = False
        return con
    else:
        return True


# 把动作转换成Z3表达式
# ['actionId', 'deviceId', 'attribute', 'newValue']
def actionToZ3(action):
    if action == None:
        return True
    x = Int((str(action[1]) + ":" + action[2]).encode('utf-8'))
    act = x == action[3]
    return act


def ConditionsImplie(con1, con2, db):
    s = Solver()
    a = True
    b = True
    for c1 in con1:
        c1z = conditionToZ3(getCondition(c1, db))
        a = And(a, c1z)
    for c2 in con2:
        c2z = conditionToZ3(getCondition(c2, db))
        b = And(b, c2z)
    if s.check(Not(Implies(a, b))) == unsat:
        return True
    return False


def getPolicy(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_spec")
    specs = cursor.fetchall()
    policies = []
    for spec in specs:
        x = Int((str(spec[0]) + ":" + str(spec[1])).encode('utf-8')) == spec[2]
        y = Int((str(spec[3]) + ":" + str(spec[4])).encode('utf-8')) == spec[5]
        if spec[6] == 0:
            policies.append(Not(And(x,y)))
        else:
            policies.append(Implies(x,y))
    # print(policies)
    return policies

def getEffect(db):
    # cursor = db.cursor()
    # cursor.execute("SELECT * FROM t_entity")
    # entities = cursor.fetchall()
    effects = []
    x1 = Int('79:设备状态'.encode('utf-8')) == 3
    y1 = Int('88:温度'.encode('utf-8')) > 26
    effects.append(Implies(x1,y1))
    x2 = Int('79:设备状态'.encode('utf-8')) == 4
    y2 = Int('88:温度'.encode('utf-8')) < 26
    effects.append(Implies(x2,y2))
    x3 = Int('84:设备状态'.encode('utf-8')) == 1
    effects.append(Implies(x3,y1))

    x1 = Int('99:设备状态'.encode('utf-8')) == 3
    y1 = Int('105:温度'.encode('utf-8')) > 26
    effects.append(Implies(x1,y1))
    x2 = Int('99:设备状态'.encode('utf-8')) == 4
    y2 = Int('105:温度'.encode('utf-8')) < 26
    effects.append(Implies(x2,y2))
    x3 = Int('103:设备状态'.encode('utf-8')) == 1
    effects.append(Implies(x3,y1))

    x1 = Int('116:设备状态'.encode('utf-8')) == 3
    y1 = Int('119:温度'.encode('utf-8')) > 26
    effects.append(Implies(x1,y1))
    x2 = Int('116:设备状态'.encode('utf-8')) == 4
    y2 = Int('119:温度'.encode('utf-8')) < 26
    effects.append(Implies(x2,y2))
    x3 = Int('117:设备状态'.encode('utf-8')) == 1
    effects.append(Implies(x3,y1))
    return effects
