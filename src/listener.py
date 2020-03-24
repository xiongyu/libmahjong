#encoding: utf-8

from .defines import CardType

class CListener:

    def OnConfirmBanker(self, iPlayer):
        pass

    def OnDrawCard(self, iPlayer, cardtype: CardType):
        pass

    # 通知 iPlayer 出牌
    def OnReadyPlay(self, iPlayer):
        pass

    # 这个玩家打了这个牌
    def OnPlay(self, iPlayer, cardtype: CardType):
        pass

    # 询问 iPlayer 要不要碰这个牌
    def OnReadyPeng(self, iPlayer, cardtype: CardType):
        pass

    # iPlayer 碰了这个牌
    def OnPeng(self, iPlayer, cardtype: CardType):
        pass

    # 询问 iPlayer 要不要杠这个牌
    def OnReadyGang(self, iPlayer, cardtype: CardType, iType):
        pass

    # iPlayer 杠了这个牌
    def OnGang(self, iPlayer, cardtype: CardType):
        pass

    def OnReadyComplete(self, iPlayer):
        pass
