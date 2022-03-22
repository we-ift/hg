# -*- coding:utf-8 -*- 
from z3 import *
import connectAndTransfer as cat
import pymysql
import time
from functools import reduce
import optActCon
import optAlwaysTrue
import optPolicyCon
import optRedundancy
import optSelfCon
import optTACon

def check(db,userId=''):
    solver = Solver()
    res = [[] for _ in range(7)]
    tm = [0 for _ in range(7)]
    apps = [[] for _ in range(3)]
    appletsList = list(cat.getAllRules(db,userId))
    appletsListLen = len(appletsList)
    for app in appletsList:
        apps[app[-1]-1].append(app)
    start0 = time.time()
    for sceneId in range(3):
        appletsList = apps[sceneId]
        triggerdic = {}
        actiondic = {}
        length = len(appletsList)
        linkTable = [[False for _ in range(length)] for _ in range(length)]
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
        #添加系统策略
        policy = cat.getPolicy(db)
        #添加环境影响
        #建立链接表
        solver.push()
        effects = cat.getEffect(db)
        for e in effects:
            solver.append(e)
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
                if solver.check((Implies(jTrigger,iAction))) == sat :
                    linkTable[i][j] = True
                elif solver.check((Implies(iTrigger,jAction))) == sat :
                    linkTable[j][i] = True
        for i in range(length):
            for j in range(length):
                for k in range(length):
                    if i != j and linkTable[i][k] == True and linkTable[k][j] == True:
                        linkTable[i][j] = True
        solver.pop()


        # 检验
        # res = []
        start = time.time()
        r = optTACon.f(appletsList, triggerdic, actiondic, linkTable)
        res[1] += r
        time1 = time.time()
        tm[1] += time1-start
        r = optAlwaysTrue.f(appletsList, triggerdic, actiondic)
        res[2] += r
        time2 = time.time()
        tm[2] += time2-time1
        r = optRedundancy.f(appletsList, triggerdic, actiondic) 
        res[3] += r
        time3 = time.time()
        tm[3] += time3-time2
        r = optSelfCon.f(appletsList, triggerdic, actiondic)
        res[4] += r
        time4 = time.time()
        tm[5] += time4-time3
        r = optActCon.f(appletsList, triggerdic, actiondic)
        res[5] += r
        time5 = time.time()
        tm[5] += time5-time4
        r = optPolicyCon.f(appletsList, triggerdic, actiondic, linkTable, policy)
        res[6] += r
        time6 = time.time()
        tm[6] += time6-time5
    tm[0] += time6-start0
    return {
        "自冲突":res[4],
        "自冲突时间":str(time4-time3)[:5],
        "多值冲突":res[5],
        "多值冲突时间":str(time5-time4)[:5],
        "冗余冲突":res[3],
        "冗余冲突时间":str(time3-time2)[:5],
        "并发冲突":res[6],
        "并发冲突时间":str(time6-time5)[:5],
        "覆盖冲突":res[1],
        "覆盖冲突时间":str(time1-start)[:5],
        "无条件触发":res[2],
        "无条件触发时间":str(time2-time1)[:5],
        "冲突":1,
        "冲突总时间":str(time6-start)[:5]
    }
    # for i in range(len(res)):
    #     res[i] = [1] + res[i] if res[i] != [] else [0]
    # return len(res[1])-1,len(res[2])-1,len(res[3])-1,\
    #     len(res[4])-1,len(res[5])-1,len(res[6])-1,float(str(tm[0])[:6]),\
    #     len(res[1])+len(res[2])+len(res[3])+len(res[4])+len(res[5])+len(res[6])-6,\
    #     appletsListLen
    


