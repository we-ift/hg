# -*- coding:utf-8 -*- 
from z3 import *
import new_connect_trans as nct
'''
A1 -> B
A2 -> !B
input is all applets
'''
def f(appletsList, triggerdic, actiondic):
    triggersolver = Solver()
    actionsolver = Solver()
    res = []
    for i in range(len(appletsList) - 1):
        for j in range(i + 1, len(appletsList)):
            triggersolver.push()
            actionsolver.push()
            itriggers = nct.getIDnums(appletsList[i][2])
            jtriggers = nct.getIDnums(appletsList[j][2])
            for num in itriggers:
                triggersolver.append(triggerdic[num])
            for num in jtriggers:
                triggersolver.append(triggerdic[num])
            iactions = nct.getIDnums(appletsList[i][3])
            jactions = nct.getIDnums(appletsList[j][3])
            for num in iactions:
                actionsolver.append(actiondic[num])
            for num in jactions:
                actionsolver.append(actiondic[num])
            if triggersolver.check() == sat and actionsolver.check() == unsat:
                if (appletsList[i][0], appletsList[j][0]) not in res and\
                        (appletsList[j][0], appletsList[i][0]) not in res:
                    res.append((appletsList[i][0], appletsList[j][0]))
            actionsolver.pop()
            triggersolver.pop()
    return res