
# import openpyxl
import os
import sys
import re

def findstr(source, startbit, endstr):
    source = str(source)
    i = 0
    endbit = startbit
    while i < len(source):
        if source[i] == endstr:
            endbit = i
            break
        else:
            i = i + 1

    tstr = source[startbit:endbit]
    return tstr

def readDBC(DBCfilepath):
    db = {}
    try:
        print('DBC file encoding is UTF-8')
        dbc = open(DBCfilepath,'r',encoding='UTF-8')
        dbc_list = dbc.readlines()
    except ValueError:
        print('DBC file encoding is not UTF-8, try GBK encoding')
        dbc = open(DBCfilepath,'r',encoding='GBK')
        dbc_list = dbc.readlines()

    length = len(dbc_list)
    for i in range(length):
        line=dbc_list[i]
        if line[0:3] == 'BO_':
            #line = dbcline_list[i]
            readbit=4
            id = findstr(line[readbit:],0,' ')
            #id =hex(int(id))
            readbit=readbit+len(id)+1
            msgname = findstr(line[readbit:],0,':')

            readbit = readbit + len(msgname) + 2
            msglen = findstr(line[readbit:], 0, ' ')

            readbit = readbit + len(msglen) + 1
            txecu = findstr(line[readbit:], 0, '\n')
            db[msgname] = {'id': id, 'msglen': msglen, 'txecu': txecu, 'signal': {}, 'TxCycTime': ''}

        # Build cycle time lookup in single pass (O(n) instead of O(n²))
        tx_cycle_times = {}
        for line in dbc_list:
            if line.startswith('BA_ "GenMsgCycleTime" BO_ '):
                rest = line[26:]  # after 'BA_ "GenMsgCycleTime" BO_ '
                id_end = rest.index(' ')
                msg_id = rest[:id_end]
                tx_cycle_times[msg_id] = findstr(rest[id_end + 1:], 0, ';')
        for msgkey in db:
            db[msgkey]['TxCycTime'] = tx_cycle_times.get(db[msgkey]['id'], '')

            i+=1
            line = dbc_list[i]
            if line[0:3] !='BO_':
               while line[0:5] ==' SG_ ':

                   readbit = 5
                   signame = findstr(line[readbit:], 0, ' ')
                   readbit = readbit + len(signame)
                   temp = findstr(line[readbit:], 0, ':')
                   readbit = readbit + len(temp) + 2
                   endbit = findstr(line[readbit:], 0, '|')  #startbit????
                   readbit = readbit + len(endbit) + 1
                   siglen = findstr(line[readbit:], 0, '@')
                   readbit = readbit + len(siglen) + 1
                   byteorder = findstr(line[readbit:], 0, '+')
                   readbit = readbit + len(byteorder) + 3
                   factor = findstr(line[readbit:], 0, ',')
                   readbit = readbit + len(factor) + 1
                   offset = findstr(line[readbit:], 0, ')')
                   readbit = readbit + len(offset) + 3
                   min = findstr(line[readbit:], 0, '|')
                   readbit = readbit + len(min) + 1
                   max = findstr(line[readbit:], 0, ']')
                   readbit = readbit + len(max) + 3
                   unit = findstr(line[readbit:], 0, '"')
                   readbit = readbit + len(unit) + 3
                   rxecu = []
                   while readbit < len(line):
                       temp = findstr(line[readbit:], 0, ',')
                       if temp == '':
                           temp = findstr(line[readbit:], 0, '\n')
                           rxecu.append(temp)
                           break
                       else:
                           rxecu.append(temp)
                           readbit = readbit + len(temp) + 1
                   db[msgname]['signal'][signame] = {'endbit': endbit, 'siglen': siglen, 'byteorder': byteorder,
                                                     'factor': factor, 'offset': offset, 'min': min, 'max': max,
                                                     'unit': unit, 'rxecu': rxecu}
                   i += 1
                   line = dbc_list[i]

        else:
            i += 1
    dbc.close()
    return db



