# -*- coding:utf-8 -*- 
from z3 import *
import time
import new_connect_trans as nct

'''
A -> ** -> ** -> !A
input is all applets
'''

def f(appletsList, triggerdic, actiondic, link_table):
    res = []
    solver = Solver()
    for i in range(len(appletsList)):
        solver.push()
        i_triggers = nct.getIDnums(appletsList[i][2])
        for num in i_triggers:
            solver.append(triggerdic[num])
        for j in range(len(appletsList)):
            if i != j:
                solver.push()
                j_actions = nct.getIDnums(appletsList[j][3])
                for num in j_actions:
                    solver.append(actiondic[num])
                if link_table[i][j] == 1 and solver.check() == unsat:
                    if (appletsList[i][0], appletsList[j][0]) not in res and \
                            (appletsList[j][0], appletsList[i][0]) not in res:
                        res.append((appletsList[i][0], appletsList[j][0]))
                solver.pop()
        solver.pop()
    return res