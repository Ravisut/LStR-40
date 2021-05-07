pix=[7,12,15,24,28,30,35,38,39,43,45,54,57,67,75,77,86,93,95,103,109,113]

def getPerformance(nmagic):
    i = 0

    for x in pix:
        i = i + 1
        if i in nmagic:
            fg_rebalance = True
            print(str(i)+ ' True ++++++++++')

        else:
            fg_rebalance = False
            print(str(i)+' False')

getPerformance(pix)