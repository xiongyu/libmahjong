g_CMDUI = """\
                      碰牌：PP11 PP12 PP13 PP14
                      杠牌：GP11 GP12 GP13 GP14
                      玩家：Test001     手牌数:CARDS1

              |---------------------东--------------------|
              | CPQ001 CPQ002 CPQ003 CPQ004 CPQ005 CPQ006 |
              | CPQ007 CPQ008 CPQ009 CPQ010 CPQ011 CPQ012 |
              | CPQ013 CPQ014 CPQ015 CPQ016 CPQ017 CPQ018 |
玩家：Test002 | CPQ019 CPQ020 CPQ021 CPQ022 CPQ023 CPQ024 |  玩家：Test004
              | CPQ025 CPQ026 CPQ027 CPQ028 CPQ029 CPQ030 |             
手牌数: CARDS2| CPQ031 CPQ032 CPQ033 CPQ034 CPQ035 CPQ036 |  手牌数: CARDS4
              | CPQ037 CPQ038 CPQ039 CPQ040 CPQ041 CPQ042 |
碰牌:         | CPQ043 CPQ044 CPQ045 CPQ046 CPQ047 CPQ048 |  碰牌: 
   PP21 PP22 南 CPQ049 CPQ050 CPQ051 CPQ052 CPQ053 CPQ054 北    PP41 PP42
   PP23 PP24  | CPQ055 CPQ056 CPQ057 CPQ058 CPQ059 CPQ060 |     PP43 PP44
杠牌:         | CPQ061 CPQ062 CPQ063 CPQ064 CPQ065 CPQ066 |  杠牌:
   GP21 GP22  | CPQ067 CPQ068 CPQ069 CPQ070 CPQ071 CPQ072 |     GP41 GP42
   GP23 GP24  | CPQ073 CPQ074 CPQ075 CPQ076 CPQ077 CPQ078 |     GP43 GP44
              | CPQ079 CPQ080 CPQ081 CPQ082 CPQ083 CPQ084 |
              | CPQ085 CPQ086 CPQ087 CPQ088 CPQ089 CPQ090 | 
              | CPQ091 CPQ092 CPQ093 CPQ094 CPQ095 CPQ096 |
              | CPQ097 CPQ098 CPQ099 CPQ100 CPQ101 CPQ102 |
              | CPQ103 CPQ104 CPQ105 CPQ106 CPQ107 CPQ108 |
              |---------------------西--------------------|

                      玩家：Test003     手牌数:CARDS3
                      碰牌：PP31 PP32 PP33 PP34
                      杠牌：GP31 GP32 GP33 GP34
${GameLog1}
${GameLog2}
${GameLog3}
"""

# 渲染命令行界面
def RendenerCmdGui(dInfo, dUsedCard, sLogList = None):
    sGui = g_CMDUI
    for i in range(1, 5):
        # 渲染玩家数据
        sGui = sGui.replace("Test00%s"%(i), dInfo[i]["Name"].ljust(7, " "))
        sGui = sGui.replace("CARDS%s"%(i), str(dInfo[i]["Cards"]).ljust(6, " "))
       
        # 渲染碰牌数据
        for iPengIndex in range(1, 5):
            if iPengIndex > len(dInfo[i]["Peng"]):
                sPeng = "    "
            else:
                sPeng = dInfo[i]["Peng"][iPengIndex - 1]
            sGui = sGui.replace("PP%s%s"%(i, iPengIndex), sPeng)
            
        # 渲染杠牌数据
        for iGangIndex in range(1, 5):
            if iGangIndex > len(dInfo[i]["Gang"]):
                sGang = "    "
            else:
                sGang = dInfo[i]["Gang"][iGangIndex - 1]
            sGui = sGui.replace("GP%s%s"%(i, iGangIndex), sGang)

    # 渲染已经打出的牌的数据
    for i in range(0, 108):
        sIndex = str(i + 1).rjust(3, "0")
        if i >= len(dUsedCard):
            sCard = "    "
        else:
            sCard = dUsedCard[i]
        sGui = sGui.replace("CPQ%s "%sIndex, " %s  "%sCard)

    # 渲染游戏日志
    for i in range(1, 4):
        if sLogList == None or 3 > len(sLogList):
            sGui = sGui.replace("${GameLog%s}"%i, "")
        else:
            sHead = "[Msg] "
            if 1 == i:
                sHead = "[New] "
            sGui = sGui.replace("${GameLog%s}"%i, sHead + sLogList[i - 1])

    return sGui

def CleanScreen():
    import os, sys
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")