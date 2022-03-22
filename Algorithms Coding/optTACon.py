# -*- coding:utf-8 -*- 
from os import link
from z3 import *
import pymysql
import connectAndTransfer as cat
import time
import ast
import timecheck
from functools import reduce

# A -> ** -> ** -> !A

#单独校验的时候用此函数，全部校验统一用f()
def selfconflict(db):
    solver = Solver()
    triggerdic = {}
    actiondic = {}
    appletsList = list(cat.getAllRules(db,userId=''))[:100]
    length = len(appletsList)
    linkTable = [[0 for _ in range(length)] for _ in range(length)]
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
    #建立链接表
    for i in range(length):
        triggers = [triggerdic[num] for num in appletsList[i][2].split(',')]
        iTrigger = reduce(And,triggers)
        actions = [actiondic[num] for num in appletsList[i][3].split(',')]
        iAction = reduce(And,actions)
        for j in range(i+1,length):
            triggers = [triggerdic[num] for num in appletsList[j][2].split(',')]
            jTrigger = reduce(And,triggers)
            actions = [actiondic[num] for num in appletsList[j][3].split(',')]
            jAction = reduce(And,actions)
            if solver.check(Not(Implies(jTrigger,iAction))) == unsat :
                linkTable[i][j] = 1
            elif solver.check(Not(Implies(iTrigger,jAction))) == unsat :
                linkTable[j][i] = 1
    for i in range(length):
        for j in range(length):
            for k in range(length):
                if i != j and linkTable[i][k] == 1 and linkTable[k][j] == 1:
                    linkTable[i][j] = 1
    # 检验
    f(appletsList,triggerdic,actiondic,linkTable)

def f(appletsList,triggerdic,actiondic,linkTable):
    s = time.time()
    solver = Solver()
    res = []
    length = len(appletsList)
    for i in range(length):
        solver.push()
        triggers = appletsList[i][2].split(',')
        for num in triggers:
            exp = triggerdic[num]
            solver.append(exp)
        for j in range(length):
            if i == j or linkTable[i][j] == False: continue
            solver.push()
            actions = appletsList[j][3].split(',')
            for num in actions:
                exp = actiondic[num]
                solver.append(exp)
            if solver.check() == unsat:
                # res = res if res != [] else [1]
                res.append((appletsList[i][1] + ' ,and, ' + appletsList[j][1]))
            solver.pop()
        solver.pop()   
    return res

