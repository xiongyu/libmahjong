#encoding:utf-8

"""
广东麻将的规则

胡牌规则分3种情况
    1. 只有一对相同牌型的牌，剩余的牌型都是123，111，1111 这样的情况
    2. 14个牌，可以组成7对
    3. 一筒，九筒，一条，九条，一万，九万，东南西北中发白

胡牌牌型: 
    - 123 为 顺子
    - 111 为 3个相同的牌，刻子
    - 1111 为 杠，如果不杠，放在牌堆里，则不能使用1111表示
    - 00 为 一对牌
    - 0 为单独一个牌

    其中杠牌“1111”，就当作“111”看待，如果有4个相同的不杠，那就不能算是“111”
    - 00,123,123,123,123
    - 00,123,123,123,111
    - 00,123,123,111,111
    - 00,123,111,111,111
    - 00,111,111,111,111
    - 00,00,00,00,00,00,00
    - 一筒，九筒，一条，九条，一万，九万，东南西北中发白, 0

牌型：
    - 万条饼
    - 东西南北风
    - 中发白

万：1-9
条：11-19
筒：21-29
东南西北中发白：91-97
"""

from .listener import CListener
from .defines import CardType, g_CardsMap, g_CheckList, HuType, g_HuMap, CardStatus
import random
import pprint


#iCard: 在这个牌出现的第一个底部打标记
def PrintCards(dTiles, iCard = -1):
    sHead = ""
    sBody = ""
    sStatus = ""
    sBottom = ""
    sFlag = ""
    b = False
    for iType in (CardType.WAN, CardType.TIAO, CardType.TONG, CardType.OTHER):
        klist = list(dTiles[iType.value].keys())
        klist.sort()
        for k in klist:
            vlist = dTiles[iType.value][k]
            for oTile in vlist:
                sHead += "|----"
                sBody += "|%s"%oTile.String()
                sIndex = str(oTile.Value()).ljust(2, " ")
                sStatus += "|%s%s"%(sIndex, oTile.StatusStr())
                sBottom += "|----"
                if not b and iCard == oTile.Value():
                    sFlag += " ^^^^"
                    b = True
                else:
                    sFlag += "     "
    sHead += "|"
    sBody += "|"
    sStatus += "|"
    sBottom += "|"
    print(sHead)
    print(sBody)
    print(sStatus)
    print(sBottom)
    if -1 != iCard:
        print(sFlag)

def Check_13yao(dTiles):
    # 如果牌数不为14，则直接返回失败
    iTotal = 0
    for dInfo in dTiles.values():
        for tileslist in dInfo.values():
            iTotal += len(tileslist)
    if iTotal < 14:
        return 14

    # 检查1，9万，1，9筒，1，9条
    for tInfo in g_CheckList:
        iType, _1, _9 = tInfo
        vlist = dTiles[iType]
        if (not _1 in vlist) or (not _9 in vlist):
            return 1

    # 检查东南西北中发白
    otherlist = dTiles[CardType.OTHER.value].keys()
    for iOtherValue in range(CardType.DONG.value, CardType.BAI.value + 1):
        if not iOtherValue in otherlist:
            return iOtherValue
    return 0

def Check_7Pair(dTiles):
    # 如果牌数不为14，则直接返回失败
    iTotal = 0
    for dInfo in dTiles.values():
        for tileslist in dInfo.values():
            for oCard in tileslist:
                if CardStatus.Null != oCard.m_Status:
                    continue
                iTotal += 1
    if iTotal < 14:
        return 14

    bPair = True
    for dInfo in dTiles.values():
        for tileslist in dInfo.values():
            if 0 != len(tileslist) % 2:
                # 其中一种牌不是一对，就不能胡牌
                bPair = False
                break
        if not bPair:
            break
    if not bPair:
        return 1

    # 如果全部对子检查都通过，那就成功
    return 0

def Check_Normal(dTiles):
    # 如果牌数小于14，则直接返回失败
    iTotal = 0
    bPair = False
    for dInfo in dTiles.values():
        for tileslist in dInfo.values():
            iTotal += len(tileslist)
            if 0 == len(tileslist) % 2:
                bPair = True
    
    # 连14张牌都不够，不能胡
    if iTotal < 14:
        return 14

    # 一对都没有，不能胡
    if not bPair:
        return 1

    # 检查是不是所有牌都可以组成顺子或者刻子
    tiles = []
    for dInfo in dTiles.values():
        for tileslist in dInfo.values():
            for oTile in tileslist:
                # 已经杠碰了的牌，就跳过
                if oTile.m_Status != CardStatus.Null:
                    continue
                tiles.append(oTile.Value())
    tiles.sort()
    # 胡牌一定要有对子，所以先找出对子，再把剩下的判断下
    # 因为已经排过序了，所以可以按顺序递增判断
    pairset = set()
    completset = []
    for i in range(len(tiles) - 1):
        if tiles[i] == tiles[i + 1]:
            pairset.add(tiles[i])
    # 找出对子之后，一对对来排除可能性。
    for iValue in pairset:
        ntiles = tiles[:]
        # 把这个对子移除
        ntiles.remove(iValue)
        ntiles.remove(iValue)
        completset.append((iValue, iValue))
        if len(ntiles) <= 0:
            #如果去掉对子之后，就没牌了，那就表示赢了
            return 0
        # 只需要找3个牌的组合，所以把剩余的牌数除以3，得出数量
        for i in range(int(len(ntiles) / 3)):
            if ( 3 == ntiles.count(ntiles[0]) ):
                # 找刻子
                completset.append((ntiles[0],) * 3)
                # 已经排序过了，所以直接切片吧
                ntiles = ntiles[3:]
            elif ntiles[0] < CardType.OTHER.value \
                    and ntiles[0]+1 in ntiles \
                    and ntiles[0] + 2 in ntiles:
                # 找顺子
                v = ntiles[0]
                completset.append((v, v + 1, v + 2))
                ntiles.remove(v)
                ntiles.remove(v + 1)
                ntiles.remove(v + 2)
            else:
                # 没找到顺子，又没找到刻子，表示不能胡牌啊
                # 换一下对对子
                break
        else:
            # 来到这里，表示所有的牌都找到了组合
            # print(completset)
            return 0

    # 啥都没找到，不能胡牌
    return 3

#麻将牌
class CCard:
    m_CardType = CardType.Unknow
    m_Value = CardType.Unknow.value

    # 从牌堆里拿出来后，就表示已经使用过，不能再发这个实例给任何人
    m_Used = 0

    # 这个牌是否已经属于碰杠状态
    m_Status = CardStatus.Null

    # 这个牌是否已经属于碰状态
    m_Peng = 0

    def __init__(self, iValue):
        if type(iValue) == CardType:
            iValue = iValue.value
        self.m_Value = iValue
        self.m_CardType = CardType(iValue)

    def StatusStr(self):
        if CardStatus.Peng == self.m_Status:
            return "碰"
        elif CardStatus.Gang == self.m_Status:
            return "杠"
        return "  "

    def Type(self):
        return self.m_Value - (self.m_Value % 10)

    def Value(self):
        return self.m_Value

    def String(self):
        return g_CardsMap[self.m_Value]

    def __repr__(self):
        return "<CCard at %s %s>"%(hex(id(self)), self.m_CardType)

    def __str__(self):
        return "<CCard at %s %s>"%(hex(id(self)), g_CardsMap[self.m_Value])

# 每个人的手牌容器
class CCardsContainer:
    m_Count = 0
    m_Cards = dict()

    def __init__(self):
        self.Cleanup()

    def Cleanup(self):
        self.m_Count = 0
        self.m_Cards = {
            CardType.WAN.value : {},
            CardType.TONG.value: {},
            CardType.TIAO.value: {},
            CardType.OTHER.value: {},
        }

    def AddCard(self, oCard, oStruct = None):
        bOther = True
        if not oStruct:
            oStruct = self.m_Cards
            bOther = False
        iType = oCard.Type()
        if not oCard.Value() in oStruct[iType]:
            oStruct[iType][oCard.Value()] = []
        oStruct[iType][oCard.Value()].append(oCard)
        if not bOther:
            self.m_Count += 1

    # 出牌
    def RemoveCard(self, cardtype: CardType, oStruct = None):
        bOther = True
        if not oStruct:
            oStruct = self.m_Cards
            bOther = False

        oCard = CCard(cardtype)

        iType = oCard.Type()
        if not oCard.Value() in oStruct[iType]:
            # 根本没有这张牌
            return 1
        iValue = oCard.Value()
        if not iValue in oStruct[iType]:
            # 没有这张牌
            return 2
        if 1 > len(oStruct[iType][iValue]):
            # 没有这张牌
            return 3
        # 移除第一张牌
        oPlayCard = oStruct[iType][iValue][0]
        oStruct[iType][iValue] = oStruct[iType][iValue][1:]
        if not bOther:
            self.m_Count -= 1
        # 如果已经是最后一张打出去，就移除这个key,方便判断
        if 1 > len(oStruct[iType][iValue]):
            del oStruct[iType][iValue]
        
        # 这样写不是很好，但暂时先这样吧。
        return oPlayCard

    def Count(self, cardtype: CardType):
        oCard = CCard(cardtype)
        dInfo = self.m_Cards[oCard.Type()]
        if not oCard.Value() in dInfo:
            return 0
        return len(dInfo[oCard.Value()])

    def Gang(self, cardtype: CardType):
        iCount = self.Count(cardtype)
        if 4 != iCount:
            return False

        oCard = CCard(cardtype)
        for oPengCard in self.m_Cards[oCard.Type()][oCard.Value()]:
            oPengCard.m_Status = CardStatus.Gang
        
        return True

    def Peng(self, cardtype: CardType):
        iCount = self.Count(cardtype)
        if 3 > iCount:
            return False

        oCard = CCard(cardtype)
        i = 0
        for oPengCard in self.m_Cards[oCard.Type()][oCard.Value()]:
            i += 1
            oPengCard.m_Status = CardStatus.Peng
            if i >= 3:
                break
        
        return True

    # 暴力算法，把牌都遍历一次，一个个加进来试，成功就表示听这个牌
    def GetListenCard(self):
        listencard = set()

        dNewCards = {}
        for iType, dInfo in self.m_Cards.items():
            dNewCards[iType] = {}
            for iValue, vlist in dInfo.items():
                dNewCards[iType][iValue] = vlist[:]

        # 开始遍历检查
        for name, member in CardType.__members__.items():
            if name in ("Unknow", "WAN", "TIAO", "TONG", "OTHER"):
                continue
            # 把新的牌，加入到新的容器里
            oNewCard = CCard(member)
            self.AddCard(oNewCard, dNewCards)
            ret = self.CheckCompleted(dNewCards, self.m_Count + 1)
            self.RemoveCard(oNewCard.m_CardType, dNewCards)
            # 这个牌不能促成胡牌，那就表示不是听的牌
            if HuType.NotComplete == ret:
                continue
            # 可以促成听牌，有用，加入到听牌列表里
            listencard.add(member)
        
        return listencard

    def CheckCompleted(self, oStruct = None, iCount = 0):
        if not oStruct:
            oStruct = self.m_Cards
            iCount = self.m_Count

        # 胡牌至少要14张牌
        if iCount < 14:
            return HuType.NotComplete
        
        # 先检查没有对子的胡牌，13幺
        ret = Check_13yao(oStruct)
        if 0 == ret:
            return HuType.ThirteenOrphans

        ret = Check_7Pair(oStruct)
        if 0 == ret:
            return HuType.SevenPairs

        ret = Check_Normal(oStruct)
        if 0 == ret:
            return HuType.Normal

        return HuType.NotComplete

# 牌桌
class CMahjongTable:

    m_Tiles = []
    m_Version = 0
    m_Banker = 1
    m_Player = 1
    m_Step = 0
    # 每一局摸牌的起点
    m_StartIndex = 0
    # 每一局最后一个牌的位置，杠之后需要从最后摸起
    m_EndIndex = 0
    # 最新一只被摸出的牌
    m_DrawCard = CardType.Unknow

    def Log(self, sLog):
        self.m_LogList.insert(0, sLog)

    def __init__(self, oListener = None):
        if not oListener:
            self.m_Listener = CListener()
        else:
            self.m_Listener = oListener

        self.m_PlayCard = []
        self.m_LogList = []

        # 初始化麻将牌
        self.m_Players = {
              1: CCardsContainer()
            , 2: CCardsContainer()
            , 3: CCardsContainer()
            , 4: CCardsContainer()
        }
        # 万
        for i in range(1, 10):
            for _ in range(0, 4):
                self.m_Tiles.append(CCard(i))
        # 条
        for i in range(11, 20):
            for _ in range(0, 4):
                self.m_Tiles.append(CCard(i))
        # 筒
        for i in range(21, 30):
            for _ in range(0, 4):
                self.m_Tiles.append(CCard(i))
        # 东南西北中发白
        for i in range(91, 98):
            for _ in range(0, 4):
                self.m_Tiles.append(CCard(i))
        self.Log("初始化准备结束.")

    def ShuffleTheTiles(self):
        random.shuffle(self.m_Tiles)
        self.Log("洗牌.")

    def Dice(self):
        self.m_StartIndex = 0
        self.m_EndIndex = len(self.m_Tiles) - 1

    def Deal(self):
        # 从庄家开始，按顺序，每人拿四个牌3次，第四次每人拿一个
        iPlayer = self.m_Banker
        playerlist = []
        for _ in range(4):
            playerlist.append(iPlayer)
            iPlayer += 1
            if iPlayer > 4:
                iPlayer = 1

        # 总共4轮，每人每轮拿4个牌
        for iTimes in range(4):
            # 每个人都拿一次
            for iPlayer in playerlist:
                if 3 == iTimes:
                    iCount = 1
                else:
                    iCount = 4
                # 每次拿iCount张牌
                for _ in range(iCount):
                    oTile = self.m_Tiles[self.m_StartIndex]
                    oTile.m_Used = True
                    self.m_Players[iPlayer].AddCard(oTile)
                    self.m_StartIndex += 1
        self.Log("发牌.")
        
    def ComfireBanker(self):
        self.m_Banker = 1
        self.m_Listener.OnConfirmBanker(self.m_Banker)

    def DealCards(self):
        # 发牌前，更新版本号
        self.m_Version += 1
        # 洗牌
        self.ShuffleTheTiles()
        # 确定庄家
        self.ComfireBanker()
        # 掷骰子，确定摸牌起点
        self.Dice()
        # 发初始牌
        self.Deal()

    # 碰牌
    def Peng(self, iPlayer, addcardtype: CardType):
        oContainer = self.m_Players[iPlayer]
        if 2 > oContainer.Count(addcardtype):
            return False
        # 如果自己有2个了，可以碰，就把捡回来的加到手牌里
        if self.m_Tiles[-1].m_CardType != addcardtype:
            raise Exception("Gang Error")
        oContainer.AddCard(self.m_Tiles[-1])
        oContainer.Peng(addcardtype)
        self.Log("%s 碰 %s"%(iPlayer, g_CardsMap[addcardtype.value]))
        self.m_Listener.OnPeng(iPlayer, addcardtype)
        return True

    # 杠牌，分为别人打出来的杠，和自己摸牌杠
    def Gang(self, iPlayer, addcardtype: CardType, iType):
        oContainer = self.m_Players[iPlayer]
        self.Log("%s 杠 %s"%(iPlayer, g_CardsMap[addcardtype.value]))
        if 1 == iType:
            # 自己摸到的杠
            if 4 > oContainer.Count(addcardtype):
                return False
        else:
            # 捡别人打出来的杠
            if 3 > oContainer.Count(addcardtype):
                return False
            # 如果自己有3个了，可以杠，就把捡回来的加到手牌里
            if self.m_Tiles[-1].m_CardType != addcardtype:
                raise Exception("Gang Error")
            oContainer.AddCard(self.m_Tiles[-1])

        oContainer.Gang(addcardtype)
        self.m_Listener.OnGang(iPlayer, addcardtype)
        return True

    # 摸牌, 默认摸给当前回合的玩家
    def DrawCard(self):
        oCard = self.m_Tiles[self.m_StartIndex]
        self.m_StartIndex += 1
        oContainer = self.m_Players[self.m_Player]
        oContainer.AddCard(oCard)
        self.m_DrawCard = oCard.m_CardType
        print("--->",oCard,self.m_DrawCard)
        self.m_Listener.OnDrawCard(self.m_Player, oCard)
        return oCard

    # 暂时不能吃胡
    def CheckNeedHu(self, iPlayer, cardtype: CardType):
        return False

    # 检查有没可以碰，杠的
    # 0- 不能碰杠
    # 1- 可以碰
    # 2- 可以碰杠
    def CheckGangPeng(self, iPlayer, cardtype: CardType):
        for iOtherPlayer in self.m_Players.keys():
            if iOtherPlayer == iPlayer:
                continue
            iCount = self.m_Players[iOtherPlayer].Count(cardtype)
            #不能碰和杠，数量连2个都不够, 下一个
            if iCount < 2:
                continue
            # 可以碰
            if iCount == 2:
                self.m_Listener.OnReadyPeng(iOtherPlayer, cardtype)
                return 1
            # 可以杠（当然就包括可以碰)
            if iCount == 3:
                self.m_Listener.OnReadyGang(iOtherPlayer, cardtype, 0)
                return 2

        # 不能碰杠，就返回0
        return 0

    # 出牌
    def Play(self, iPlayer, cardtype: CardType):
        # 打出去的牌，重新回归牌池
        oPlayCard = self.m_Players[iPlayer].RemoveCard(cardtype)
        self.m_Tiles.append(oPlayCard)

        # 记录已经打出去的牌（其实这里可以优化掉了，暂时还有用）
        self.m_PlayCard.append(cardtype)
        self.Log("玩家 %s 出牌:%s"%(iPlayer, g_CardsMap[cardtype.value]))
        #检查有没人对这个牌有意思
        # 先检查胡牌的
        ret = self.CheckNeedHu(iPlayer, cardtype)
        if not ret:
            # 检查杠，碰
            self.CheckGangPeng(iPlayer, cardtype)

    # 下一回合, 不传iPlayer，就默认下一个，传了1～4进来
    # 就使用玩家作为当前回合的玩家
    def NextStep(self, iPlayer = 0, bSkipDraw = False):
        # 第一回合，无论传什么进来，都是庄家开始
        if 0 == self.m_Step:
            self.m_Player = self.m_Banker
        else:
            if iPlayer:
                if not iPlayer in (1, 2, 3, 4):
                    print("Unkonw player %s"%(iPlayer))
                else:
                    self.m_Player = iPlayer
            else:
                self.m_Player += 1
                if self.m_Player > 4:
                    self.m_Player = 1
        
        self.m_Step += 1
        # 不跳过摸牌阶段(碰，吃就不能摸牌)，就摸牌吧
        if not bSkipDraw:
            oCard = self.DrawCard()
            if oCard:
                oContainer = self.m_Players[self.m_Player]
                # 检查是否可以杠，胡
                iCount = oContainer.Count(oCard.Value())
                if 4 == iCount:
                    # 问玩家要不要杠
                    self.m_Listener.OnReadyGang(self.m_Player, oCard.m_CardType, 1)
                hupai = oContainer.CheckCompleted()
                if HuType.NotComplete != hupai:
                    # 问玩家要不要胡，可以和杠同时的，也可以选择不胡不杠
                    self.m_Listener.OnReadyComplete(self.m_Player)
            else:
                print("流局")

        self.m_Listener.OnReadyPlay(self.m_Player)
        return self.m_Player
        

    def Simulate(self):
        pass

