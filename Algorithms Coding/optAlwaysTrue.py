# -*- coding:utf-8 -*- 
from z3 import *
import connectAndTransfer as cat
import pymysql
import time
from functools import reduce

dayofweeks = '1,2,3,4,5,6,7'
starttime = '00:00:00'
endtime = '12:59:59'


def traverseTable(db, userId=''):
    actDict = {}
    atFlag = 0
    result = []
    rule = cat.getAllRules(db, userId)
    # ['ruleId', 'ruleName', 'conditionIds', 'actionIds']
    s = Solver()
    for r in rule:
        act = cat.getAction(r[3], db)
        actKey = str(act[1]) + '+' + str(act[2]) + '+' + str(act[3])
        try:
            actDict[actKey]
        except:
            actDict[actKey] = 1
            actIdSet = []
            ruleSet = []
            sameAct = False
            actIds = cat.getActbyAttr(act[1], act[2], act[3], db)
            for a in actIds:
                a = str(a[0])
                actIdSet.append(a)
            for rl in rule:
                if str(rl[3]) in actIdSet and str(rl[4]) == dayofweeks \
                        and str(rl[5]) == starttime and str(rl[6]) == endtime:
                    conZ3 = True
                    cons = rl[2]
                    if cons != None and cons != True:
                        cons = str(rl[2]).split(',')
                        for c in cons:
                            c = cat.conditionToZ3(cat.getCondition(c, db))
                            conZ3 = And(conZ3, c)
                    sameAct = Or(sameAct, conZ3)
                    ruleSet.append(rl)
            if s.check(Not(sameAct)) == unsat:
                atFlag = 1
                for rs in ruleSet:
                    result.append(rs[1])
    if not result:
        result.append('0')
    return atFlag, result

def alwaysaTrue(db):
    triggerdic = {}
    actiondic = {}
    appletsList = list(cat.getAllRules(db,userId=''))
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
    f(appletsList,triggerdic,actiondic)

def f(appletsList,triggerdic,actiondic):
    s = time.time()
    solver = Solver()
    res = []
    length = len(appletsList)
    checkedRule = []
    for i in range(length):
        if appletsList[i][0] not in checkedRule:
            sameAct = [appletsList[i][1]]
            checkedRule.append(appletsList[i][0])
            triggerSet = []
            triggers = [triggerdic[num] for num in appletsList[i][2].split(',')]
            iTrigger = reduce(And,triggers)
            triggerSet.append(iTrigger)
            actions = [actiondic[num] for num in appletsList[i][3].split(',')]
            iAction = reduce(And,actions)

            for j in range(length):
                if appletsList[j][0] not in checkedRule and j!= i:
                    actions = [actiondic[num] for num in appletsList[j][3].split(',')]
                    jAction = reduce(And,actions)
                    if jAction == iAction:
                        sameAct.append(appletsList[j][1])
                        checkedRule.append(appletsList[j][0])
                        triggers = [triggerdic[num] for num in appletsList[j][2].split(',')]
                        jTrigger = reduce(And,triggers)
                        triggerSet.append(jTrigger)
            allset = reduce(Or,triggerSet)
            if solver.check(Not(allset)) == unsat:
                # res = res if res != [] else [1]
                res.append((sameAct))
    # print(time.time()-s)
    # print(res)
    # res = [0] if res == [] else res
    return res


