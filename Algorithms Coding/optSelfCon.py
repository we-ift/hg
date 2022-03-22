# -*- coding:utf-8 -*- 
from z3 import *
import connectAndTransfer as cat
import pymysql
import time
from functools import reduce

def traverseTable(db,userId=''):
    invFlag = 0
    result = []
    rule = cat.getAllRules(db,userId)
    # ['ruleId', 'ruleName', 'conditionIds', 'actionIds']
    s = Solver()
    for r in rule:
        con = r[2]
        act = r[3]
        consZ3 = True
        if con != None and con != True :
            cons = str(con).split(',')
            for c in cons:
                conZ3 = cat.conditionToZ3(cat.getCondition(c,db))
                consZ3 = And(consZ3,conZ3)
        actZ3 = cat.actionToZ3(cat.getAction(act,db))
        if s.check(Not(Implies(consZ3,actZ3))) == unsat:
            invFlag = 1
            if result == []:
                result.append(1)
            result.append(r[1])
    if result==[]:
        result.append('0')
    return invFlag,result


def selfCon(db):
    triggerdic = {}
    actiondic = {}
    appletsList = list(cat.getAllRules(db,userId=''))[:20]
    # print(appletsList)
    length = len(appletsList)
    # 建立z3表达式的字典 不用每次都转换
    for i in range(length):
        triggers = appletsList[i][2]
        actions = appletsList[i][3]
        nums = triggers.split(',')
        for num in nums:
            exp = cat.conditionToZ3(cat.getCondition(num,db))
            if triggerdic.get(num) is None:
                triggerdic[num] = exp
        nums = actions.split(',')
        for num in nums:
            exp = cat.actionToZ3(cat.getAction(num,db))
            if actiondic.get(num) is None:
                actiondic[num] = exp
    # 检验
    return f(appletsList,triggerdic,actiondic)

def f(appletsList,triggerdic,actiondic):
    # appletsList = [('1', 'a', '127', '151', '1,2,3,4,5,6,7', '00:00:00', '23:59:59', '5', '1')]
    # print(appletsList)
    s = time.time()
    solver = Solver()
    res = []
    length = len(appletsList)
    for i in range(length):
        triggers = [triggerdic[num] for num in appletsList[i][2].split(',')]
        iTrigger = reduce(And,triggers)
        actions = [actiondic[num] for num in appletsList[i][3].split(',')]
        iAction = reduce(And,actions)
        solver.push()
        solver.append(iTrigger)
        solver.append(iAction)
        if solver.check() == unsat:
            # res = res if res != [] else [1]
            res.append((appletsList[i][1]))
        solver.pop()
    # print(time.time()-s)
    # print(res)
    # res = [0] if res == [] else res
    return res
    
