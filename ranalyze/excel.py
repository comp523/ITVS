#!/usr/bin/python3

import openpyxl


def columnize(n):
    column = ''
    if(n == 0):
        return 'A'
    n+=1
    while(n > 0):
        column = chr(ord('A')+n%26 - (1 if n < 25 else 0)) + column
        n = n-n%26
        n = n//26
    return column

#def columnize2(n):
#    l = []
#    end = False
#    while(not end):
#        l.append(n%26)
#        if(n == 0):
#            end = True
#        n = n-n%26
#        n = n//26
#    return l

def wexcel(wb, columns, post):
    if(post[0] in wb.sheetnames):
        if(wb[post[0]]['AAA1'] == None):
            print("u wut m8")
        else:
            row = wb[post[0]]['AAA1']
            x = 0
            while(x < len(columns)):
                wb[post[0]]['{}{}'.format(columnize(x), row+1)] = post[1][columns[x]]
                x+=1
            wb[post[0]]['AAA1'] += 1
    else:
        wb.create_sheet(post[0])
        x = 0
        while(x < len(columns)):
            wb[post[0]]['{}1'.format(columnize(x))] = columns[x]
            wb[post[0]]['{}2'.format(columnize(x))] = post[1][columns[x]]
            x+=1
        wb[post[0]]['AAA1'] = 2




for k in range(10000,20000):
    print([k, columnize(k)])









