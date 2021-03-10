# -*- coding:utf-8 -*-
from z3 import *
import time
import new_connect_trans as nct

def f(appletsList, triggerdic, actiondic, link_table):
    res = []
    solver = Solver()
    s = Solver()
    solver.set(unsat_core=True)
    # Specifications
    solver.assert_and_track(Not(And(Int('AC') == 0, Int('heater') == 1)), 'fc1')
    solver.assert_and_track(Not(And(Int('oven') == 0, Int('door') == 2)), 'fc2')
    solver.assert_and_track(Not(And(Int('camera') == 2, Int('camera bulb') == 0)), 'fc3')
    for i in range(len(appletsList)):
        solver.push()
        solver.push()
        count = 0
        i_triggers = nct.getIDnums(appletsList[i][2])
        i_actions = nct.getIDnums(appletsList[i][3])
        for num in i_triggers:
            solver.assert_and_track(triggerdic[num], str(count))
            count += 1
        for num in i_actions:
            solver.assert_and_track(actiondic[num], str(count))
            count += 1
        if solver.check() == unsat:
            uc = solver.unsat_core()
            if (Bool('fc1') in uc or Bool('fc2') in uc or Bool('fc3') in uc):
                res.append(appletsList[i][0])
        solver.pop()
        for j in range(len(appletsList)):
            if i != j:
                solver.push()
                s.push()
                j_triggers = nct.getIDnums(appletsList[j][2])
                j_actions = nct.getIDnums(appletsList[j][3])
                for num in j_triggers:
                    s.append(triggerdic[num])
                for num in i_triggers:
                    s.append(triggerdic[num])
                for num in i_actions:
                    solver.assert_and_track(actiondic[num], str(count))
                    count += 1
                for num in j_actions:
                    solver.assert_and_track(actiondic[num], str(count))
                    count += 1
                if s.check() == sat and solver.check() == unsat:
                    uc = solver.unsat_core()
                    if (Bool('fc1') in uc or Bool('fc2') in uc or Bool('fc3') in uc) and (appletsList[j][0], appletsList[i][0]) not in res:
                        res.append((appletsList[i][0], appletsList[j][0]))
                s.pop()
                solver.pop()
                solver.push()
                for num in i_triggers:
                    solver.assert_and_track(triggerdic[num], str(count))
                    count += 1
                for num in i_actions:
                    solver.assert_and_track(actiondic[num], str(count))
                    count += 1
                for num in j_actions:
                    solver.assert_and_track(actiondic[num], str(count))
                    count += 1
                if link_table[i][j] == 1 and solver.check() == unsat:
                    uc = solver.unsat_core()
                    if (Bool('fc1') in uc or Bool('fc2') in uc or Bool('fc3') in uc):
                        if (appletsList[i][0], appletsList[j][0]) not in res and \
                                (appletsList[j][0], appletsList[i][0]) not in res:
                            res.append((appletsList[i][0], appletsList[j][0]))
                solver.pop()
        solver.pop()
    return res

