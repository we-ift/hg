# -*- coding:utf-8 -*- 
import time
import random
from z3 import *
import c_actionConflict as c1
import c_cyclicTriggering as c2
import c_selfConflict as c3
import c_deviceConflict as c4
import c_ruleRedundancy as c5
import c_unconditionalRule as c6
import new_connect_trans as nct


def check(appletsList):
    triggerdic = {}
    actiondic = {}
    length = len(appletsList)
    # Build a dictionary of z3 expressions without having to convert every time
    for i in range(length):
        triggers = appletsList[i][2]
        actions = appletsList[i][3]
        nums = nct.getIDnums(triggers)
        for num in nums:
            exp = nct.trans(nct.getexp(num, 'T'))
            if triggerdic.get(num) is None:
                triggerdic[num] = exp
        nums = nct.getIDnums(actions)
        for num in nums:
            exp = nct.trans(nct.getexp(num, 'A'))
            if actiondic.get(num) is None:
                actiondic[num] = exp
    # Establish a relational table of implication/triggering relationship, no need to judge every time
    link_table = [[0 for i in range(length)] for i in range(length)]
    link_solver = Solver()
    link_checker = Solver()
    # environmental impact
    link_checker.append(Implies(Int('AC') == 0, Int('air temperature') < 0))
    link_checker.append(Implies(Int('heater') == 1, Int('air temperature') > 1))
    for i in range(length):
        i_actions = nct.getIDnums(appletsList[i][3])
        for j in range(length):
            if i != j:
                link_solver.push()
                flag = sat
                j_triggers = nct.getIDnums(appletsList[j][2])
                for ia in i_actions:
                    link_solver.append(actiondic[ia])
                    for jt in j_triggers:
                        link_solver.append(triggerdic[jt])
                        flag = unsat if flag == unsat else link_checker.check(
                            Not(Implies(actiondic[ia], triggerdic[jt])))
                if flag == unsat and link_solver.check() == sat:
                    link_table[i][j] = 1
                link_solver.pop()
    for i in range(length):
        for j in range(length):
            for k in range(length):
                if link_table[i][k] == 1 and link_table[k][j] == 1 and i != j:
                    link_table[i][j] = 1
    res1 = c1.f(appletsList, triggerdic, actiondic)
    res2 = c2.f(appletsList, triggerdic, actiondic, link_table)
    res3 = c3.f(appletsList)
    res4 = c4.f(appletsList, triggerdic, actiondic, link_table)
    res5 = c5.f(appletsList, triggerdic, actiondic)
    res6 = c6.f(appletsList, triggerdic)
    return [res1, res2, res3, res4, res5, res6]


if __name__ == '__main__':
    conn, cursor = nct.connect()
    sql = '''select * from applets''' 
    cursor.execute(sql)
    app = cursor.fetchall()
    for num in range(10, 101, 10):
        count = [0, 0, 0, 0, 0, 0, 0]
        t_count = 0
        repeat = 100
        for times in range(repeat):
            sample = random.sample(app, num)
            start = time.time()
            res = check(sample)
            dur = time.time() - start
            for i in range(6):
                count[i] += len(res[i])
            count[6] = count[0] + count[1] + count[2] + count[3] + count[4] + count[5]
            t_count += dur
        for i in range(len(count)):
            count[i] = count[i] / repeat
        t_count = t_count / repeat
        with open('random_result.txt', 'a+') as f:
            f.write('-------')
            f.write(str(num) + ' ')
            f.write(str(count[0]) + ' ')
            f.write(str(count[1]) + ' ')
            f.write(str(count[2]) + ' ')
            f.write(str(count[3]) + ' ')
            f.write(str(count[4]) + ' ')
            f.write(str(count[5]) + ' ')
            f.write(str(t_count) + '\n')
    conn.close()



