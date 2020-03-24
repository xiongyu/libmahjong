#encoding:utf-8

from src.listener import CListener
from src.major import CCard \
, CCardsContainer, CardType \
, g_CardsMap, PrintCards, g_HuMap, HuType\
, CMahjongTable
from src.cmdui import RendenerCmdGui, CleanScreen


dInfo = {
    1: {
        "Name": "Tony",
        "Gang": [],
        "Peng": [],
        "Cards": 0,
    },
    2: {
        "Name": "Lier",
        "Gang": [],
        "Peng": [],
        "Cards": 0,
    },
    3: {
        "Name": "Peter",
        "Gang": [],
        "Peng": [],
        "Cards": 0,
    },
    4: {
        "Name": "Cavan",
        "Gang": [],
        "Peng": [],
        "Cards": 0,
    }
}

class CMyListener(CListener):

    def OnConfirmBanker(self, iPlayer):
        pass

    def OnDrawCard(self, iPlayer, cardtype: CardType):
        pass

    # 通知 iPlayer 出牌
    def OnReadyPlay(self, iPlayer):
        UpdateIndo(self.m_Table)
        if 3 == iPlayer:
            dUsedCard = []
            for cardtype in table.m_PlayCard:
                dUsedCard.append(g_CardsMap[cardtype.value])
            oCard = WaitInput(self.m_Table, dInfo, dUsedCard)
            if None == oCard:
                return
            self.m_Table.Play(iPlayer, oCard)
        else:
            self.m_Table.Play(iPlayer, self.m_Table.m_DrawCard)

    # 这个玩家打了这个牌
    def OnPlay(self, iPlayer, cardtype: CardType):
        UpdateIndo(self.m_Table)
        dUsedCard = []
        for cardtype in table.m_PlayCard:
            dUsedCard.append(g_CardsMap[cardtype.value])
        CleanScreen()
        RendenerCmdGui(dInfo, dUsedCard, self.m_Table.m_LogList)

    # 询问 iPlayer 要不要碰这个牌
    def OnReadyPeng(self, iPlayer, cardtype: CardType):
        if 3 != iPlayer:
            return
        a = input("牌：%s 你可以选择 碰(P)，或者什么都不会直接回车跳过："%(g_CardsMap[cardtype.value]))
        if not a:
            return
        if a == "P":
            self.m_Table.Peng(iPlayer, cardtype)

    # iPlayer 碰了这个牌
    def OnPeng(self, iPlayer, cardtype: CardType):
        if 3 == iPlayer:
            self.OnReadyPlay(iPlayer)

    # 询问 iPlayer 要不要杠这个牌
    def OnReadyGang(self, iPlayer, cardtype: CardType, iType):
        if 3 != iPlayer:
            return
        a = input("牌：%s 你可以选择杠(G)，碰(P)，或者什么都不会直接回车跳过："%(g_CardsMap[cardtype.value]))
        if not a:
            return
        if a == "G":
            self.m_Table.Gang(iPlayer, cardtype, iType)
        elif a == "P":
            self.m_Table.Peng(iPlayer, cardtype)

    # iPlayer 杠了这个牌
    def OnGang(self, iPlayer, cardtype: CardType):
        if 3 == iPlayer:
            self.OnReadyPlay(iPlayer)

def WaitInput(table, dInfo, dUsedCard):
    sFlag = "输入要出的牌："
    while(True):
        CleanScreen()
        print(RendenerCmdGui(dInfo, dUsedCard, table.m_LogList))
        PrintCards(table.m_Players[3].m_Cards, table.m_DrawCard.value)
        try:
            s = input(sFlag)
        except KeyboardInterrupt:
            print("取消输入")
            return None

        try:
            intinput = int(s)
        except:
            intinput = -99
        if -99 == intinput or intinput in (CardType.WAN.value
                , CardType.TONG.value
                , CardType.TIAO.value
                , CardType.OTHER.value
                , CardType.Unknow.value) or not intinput in g_CardsMap.keys():
            sFlag = "输入有误，请重新输入："
        else:
            return CardType(intinput)

def UpdateIndo(table):
    for i in range(1, 5):
        dInfo[i]["Cards"] = table.m_Players[i].m_Count

print("""\
============================================================================
|                              命令行麻将 v0.0.1                           |
|                        made by h.xiongyu@gmail.com                       |
|               https://github.com/huangxiongyu/cmdmajor.git               |
============================================================================
""")

oListener = CMyListener()
table = CMahjongTable(oListener)
oListener.m_Table = table
table.DealCards()

while(True):
    table.NextStep()

