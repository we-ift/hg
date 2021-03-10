# -*- coding:utf-8 -*- 
from z3 import *
import time
import new_connect_trans as nct

'''
A -> !A
input is all applets
'''
def f(appletsList):
    res = []
    solver = Solver()
    length = len(appletsList)
    for i in range(length):
        solver.push()
        triggers = appletsList[i][2]
        actions = appletsList[i][3]
        nums = nct.getIDnums(triggers)
        if len(nums) == 1:
            exp = nct.trans(nct.getexp(nums[0], 'T'))
            solver.append(exp)
            nums = nct.getIDnums(actions)
            for num in nums:
                exp = nct.trans(nct.getexp(num, 'A'))
                solver.append(exp)
            if solver.check() == unsat:
                res.append(appletsList[i][0])
        solver.pop()
    return res
