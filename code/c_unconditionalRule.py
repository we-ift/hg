# -*- coding:utf-8 -*-
from z3 import *
import time
import new_connect_trans as nct
import json

'''
A -> B & not A -> B
that is, True -> B, always B means unfair
input is all applets
'''
def f(appletsList, triggerdic):
    triggersolver, res = Solver(), []
    fatherpath = os.getcwd().split('\\')[:-1]
    fatherpath.append("metadata")
    alist = []
    for i in range(len(appletsList)-1):
        tlist, rules = [], []
        tid = nct.getIDnums(appletsList[i][2])
        aid = nct.getIDnums(appletsList[i][3])
        if len(tid) == 1 and len(aid) == 1 and aid[0] not in alist:
            rules.append(appletsList[i][0])
            exp = nct.getoexp(tid[0], 'T').split('=')[0].strip().split()
            fatherpath.append("{}.json".format(exp[0]))
            path = "/".join(fatherpath)
            text = ''
            with open(path, 'r') as f:
                text = json.loads(f.read())
                for i in range(1,len(exp)):
                    text = text[exp[i]]
                text = text['value']
            fatherpath.pop()
            if len(text) < 2:
                continue
            alist.append(aid[0])
            for j in range(i+1, len(appletsList)):
                if nct.getIDnums(appletsList[j][3]) == aid:
                    tlist.append(nct.getIDnums(appletsList[j][2])[0])
                    rules.append(appletsList[j][0])
            triggersolver.push()
            name = ' '.join(exp)
            triggersolver.add(Int(name) >= 0)
            triggersolver.add(Int(name) < len(text))
            expression = triggerdic[tid[0]]
            for num in tlist:
                expression = Or(expression, triggerdic[num])
            if triggersolver.check(Not(expression)) == unsat:
                res.append(tuple(rules))
            triggersolver.pop()
    return res

