# hg

This is the core algorithm used by HomeGuard. The program entry is the mainCheck.py file.
========================================================
The main package that the program depends on is Z3, which can be installed using the code 'pip install z3-solver'.

The experiment rules data in the Data folder is exported from the mysql database. You can import into your own local mysql database and configure your database information in the connectAndTransfer.py file. This allows the code to connect to your database for user rules reading.
The operation of the mysql database can install dependencies through the code 'pip install pymysql'

========================================================
The ActCon.py file is the algorithm used to detect Action Conflicts.
The AlwaysTrue.py file is the algorithm used to detect Unconditional Triggering.
The PolicyCon.py file is the code used to detect Device Conflicts.
The SelfCon.py file is the algorithm used to detect Self Conflicts.
The TACon.py file is the algorithm used to detect Cyclic Triggering.
The Redundancy.py file is the algorithm used to detect Redundant Rules.

connectAndTransfer.py contains some tool functions used in the detection process, including functions that interact with the database, functions that involve format conversion, etc.
