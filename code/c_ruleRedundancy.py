# -*- coding:utf-8 -*-
from z3 import *
import time
import new_connect_trans as nct

"""
A -> B
A' -> B
A implies A' or A' implies A
input is all applets
"""
def f(appletsList, triggerdic, actiondic):
    res = []
    solver = Solver()
    length = len(appletsList)
    for i in range(length):
        i_trigger_nums = nct.getIDnums(appletsList[i][2])
        i_triggers = [triggerdic[num] for num in i_trigger_nums]
        i_action_nums = nct.getIDnums(appletsList[i][3])
        i_actions = [actiondic[num] for num in i_action_nums]
        for j in range(length):
            if i != j:
                flag = 0
                j_trigger_nums = nct.getIDnums(appletsList[j][2])
                j_triggers = [triggerdic[num] for num in j_trigger_nums]
                j_action_nums = nct.getIDnums(appletsList[j][3])
                j_actions = [actiondic[num] for num in j_action_nums]
                if i_actions == j_actions:
                    for i_trigger in i_triggers:
                        for j_trigger in j_triggers:
                            if solver.check(Not(Implies(i_trigger, j_trigger))) == unsat:
                                flag += 1
                    if flag == len(i_triggers):
                        if (appletsList[i][0], appletsList[j][0]) not in res and \
                                (appletsList[j][0], appletsList[i][0]) not in res:
                            res.append((appletsList[i][0], appletsList[j][0]))
    return res
