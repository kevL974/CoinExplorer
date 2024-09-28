from abc import ABC, abstractmethod
from binance import AsyncClient

ACC_BALANCES: str = "balances"
ACC_ASSET: str = "asset"
ACC_ASSET_FREE: str = "free"
ACC_ASSET_LOCK: str = "locked"


class Wallet(ABC):

    @abstractmethod
    async def get_asset_qty(self, asset: str, with_lock: bool = False) -> float:
        """
        Function that returns quantity of asset given on parameters.
        @param asset: target asset
        @param with_lock: if True, it returns asset quantity minus quantity locked by previous orders
        else it returns total quantity

        @return: asset quantity
        """
        pass


class BinanceWallet(Wallet):
    """
    This class stores binance account information.
    """

    def __init__(self, binance_client: AsyncClient):
        Wallet.__init__(self)
        assert binance_client is not None
        self.client = binance_client

    async def get_asset_qty(self, asset: str, with_lock: bool = False) -> float:
        account = await self.client.get_account()
        assets_list = account[ACC_BALANCES]
        for asset_i in assets_list:
            if asset_i[ACC_ASSET] == asset:
                if with_lock:
                    return asset_i[ACC_ASSET_FREE] - asset_i[ACC_ASSET_LOCK]
                else:
                    return asset_i[ACC_ASSET_FREE]