import datetime
import json
import time
import pulsar
import threading
import requests
import typing

from pocketx.account import (
    Account,
    AccountType,
    FutureAccount,
    StockAccount
)

# from pocketx.utils import create_solace
from pocketx.backend.utils import create_solace

from pocketx.contracts import (
    BaseContract,
    Contract,
    Contracts,
    FetchStatus,
    Future,
    Index,
    Option,
    Stock,
    get_product_contracts,
    StreamMultiContract
)

from pocketx.position import (
    FuturePosition,
    FuturePositionDetail,
    FutureProfitLoss,
    Margin,
    Settlement,
    StockPositionDetail,
    StockProfitLoss,
    StockPosition,
    Settlement,
    AccountBalance,
    StockProfitDetail,
    FutureProfitDetail,
    FutureProfitLossSummary,
    StockProfitLossSummary,
)

from pocketx.data import (
    Snapshot,
)

from pocketx.constant import (
    Action,
    Exchange,
    OrderState,
    SecurityType,
    Status,
    Unit,
    ScannerType,
    TicksQueryType,
    QuoteType,
    QuoteVersion,
    TickType,
)

from pocketx.order import (
    ComboOrder,
    Order,
    OrderDealRecords,
    StrictInt,
    Trade,
    ComboTrade,
    conint,
)

from pocketx.error import (
    AccountNotProvideError,
    AccountNotSignError,
    TargetContractNotExistError,
)

class Pocket():

    def __init__(
            self,
            simulation: bool = False,
    ):

        self.user_info = None
        self.ca = None
        self.stock_account = None
        self.futopt_account = None
        self.Contracts = Contracts()
        self.Order = Order
        self.ca = {"activated":None, "propertyFile":None}
        self.account_positions = {}
        self.trades = {}
        self.trades_list = []
        self.simulation = simulation
        self._setup_solace()

    def _setup_solace(self):
        self._solace = create_solace(simulation=self.simulation)


    def fetch_contracts(
            self,
            contract_download: bool = False,
            contracts_timeout: int = 0,
            # contracts_cb: typing.Callable[[], None] = None
            contracts_cb = None
    ):

        if contract_download:
            self.Contracts.status = FetchStatus.Fetching

            try:
                start_time = datetime.datetime.now()
                contracts = self._solace.load_contracts(contracts_timeout)
                end_time = datetime.datetime.now()
                print(f"Spend {str(end_time-start_time)} !!!!!!!!!!!!!!!!!!!!!!!!")

                self._populate_contracts(contracts)
                self.Contracts.status = FetchStatus.Fetched


            except Exception as e:
                print(f"Error fetching contracts: {e}")
                self.Contracts.status = FetchStatus.Unfetch

            print(f"Contracts status: {self.Contracts.status}")

    def _populate_contracts(
            self,
            contracts
    ):

        self.Contracts = Contracts(
            Stocks = contracts["Stock"],
            Futures = contracts["Future"],
            Options = contracts["Option"],
            Indexs = contracts["Index"]
            )

        self.Contracts._set_fetched()
        self._solace.Contracts = self.Contracts


    def login(
            self,
            api_key: str,
            password: str,
            fetch_contract: bool = True,
            contracts_timeout: int = 0,
            subscribe_trade: bool = True,
            simu_ca: str = None
    ):

        self.user_info = self._solace.token_login(api_key, password, simu_ca)

        print("="*43 + " User Logged in " + "="*43 + "\n")

        if fetch_contract:
            contract_download = fetch_contract
            contracts_cb = None
            self.fetch_contracts(contract_download, contracts_timeout, contracts_cb)

        self.accounts = self._solace.process_accounts()
        self.stock_account = self._solace.default_stock_account(self.accounts)
        self.futopt_account = self._solace.default_futopt_account(self.accounts)

        if subscribe_trade:
            kwargs = {"account": None}
            subscribe_thread = threading.Thread(target=self._solace.receive_message, kwargs=kwargs)
            subscribe_thread.daemon = True
            subscribe_thread.start()

        return self.accounts

    def logout(self):
        self.user_info = None
        self.headers = {}

        print("\n" + "="*43 + " User Logged out " + "="*43)

    def activate_ca(self, ca_path: str, ca_passwd: str, person_id: str = "", store: int = 0):
        """activate your ca for trading

        Args:
            ca_path (str):
                the path of your ca, support both absloutely and relatively path, use same ca with eleader
            ca_passwd (str): password of your ca
        """
        if self.user_info:
            res = self._solace.twca_sign(ca_path, ca_passwd, person_id, store)
            return res

        else:
            raise Exception("簽證啟用失敗，請先進行登入！")

    def set_default_account(self, account):
        if isinstance(account, StockAccount):
            self._solace.set_default_account(account)
            self.stock_account = account

        elif isinstance(account, FutureAccount):
            self._solace.set_default_account(account)
            self.futopt_account = account

    def place_order(
            self,
            contract: Contract,
            order: Order,
            timeout: int = 5000,
            # cb: typing.Callable[[Trade], None] = None,
            cb = None
    ) -> Trade:

        if not order.account:
            if isinstance(contract, Future) or isinstance(contract, Option):
                order.account = self.futopt_account
            elif isinstance(contract, Stock):
                order.account = self.stock_account
            else:
                # log.error("Please provide the account place to.")
                return None

        if contract.target_code:
            if self.Contracts.Futures.get(contract.target_code) is None:
                raise TargetContractNotExistError(contract)
            contract = self.Contracts.Futures.get(contract.target_code)

        trade = self._solace.place_order_api(contract, order, timeout, cb)

        try:
            entid = trade.order.entid
            return self._solace.trades[entid]

        except:
            return trade

    def update_order(
            self,
            trade: Trade,
            price: typing.Union[StrictInt, float] = None,
            qty: int = None,
            timeout: int = 5000,
            # cb: typing.Callable[[Trade], None] = None,
            cb=None,
    ) -> Trade:

        trade = self._solace.update_order_api(trade=trade, price=price, qty=qty)
        return trade
        # return self._solace.trades[trade.order.entid]

    def cancel_order(
            self,
            trade: Trade,
            timeout: int = 5000,
            # cb: typing.Callable[[Trade], None] = None,
            cb = None
    ) -> Trade:

        trade = self._solace.cancel_order_api(trade=trade)
        return trade
        # return self._solace.trades[trade.order.entid]

    def account_balance(
        self,
        timeout: int = 5000,
        # cb: typing.Callable[[AccountBalance], None] = None,
        cb = None
    ) -> AccountBalance:
        """get stock account balance"""
        return self._solace.account_balance(self.stock_account, timeout=timeout)

    def update_status(
            self,
            account: Account = None,
            trade: Trade = None,
            timeout: int = 5000,
            cb=None,
            # cb: typing.Callable[[typing.List[Trade]], None] = None,
    ):
        """update status of all trades you have"""
        if trade:
            response = self._solace.update_status(
                trade=trade,
                timeout=timeout,
                cb=cb,
            )
            return response
        elif account:
            if account.signed or self.simulation:
                response = self._solace.update_status(account=account, timeout=timeout, cb=cb)
                return response
        else:
            if self.stock_account:
                if self.stock_account.signed or self.simulation:
                    response = self._solace.update_status(
                        account=self.stock_account, timeout=timeout, cb=cb
                    )
                    return response
            if self.futopt_account:
                if self.futopt_account.signed or self.simulation:
                    response = self._solace.update_status(
                        account=self.futopt_account, timeout=timeout, cb=cb
                    )
                    return response

    def list_accounts(self):
        return self._solace.accounts

    def list_positions(
            self,
            account: Account = None,
            unit: Unit = Unit.Common,
            timeout: int = 5000,
            cb=None,
            # cb: typing.Callable[[typing.List[typing.Union[StockPosition, FuturePosition]]], None] = None,
    ) -> typing.List[typing.Union[StockPosition, FuturePosition]]:

        if account:
            account_positions = self._solace.list_positions(account=account, unit=unit, timeout=timeout, cb=cb)
            return account_positions

        else:
            account_positions = self._solace.list_positions(account=self.stock_account, unit=unit, timeout=timeout, cb=cb)
            return account_positions


    def list_position_detail(
        self,
        account: Account = None,
        detail_id: int = 0,
        timeout: int = 5000,
        cb = None,
        # cb: typing.Callable[
        #     [typing.List[typing.Union[StockPositionDetail, FuturePositionDetail]]],
        #     None,
        # ] = None,
    ) -> typing.List[typing.Union[StockPositionDetail, FuturePositionDetail]]:

        if account:
            return self._solace.list_position_detail(
                account, detail_id, timeout=timeout, cb=cb
            )
        else:
            default_account = self._portfolio_default_account()
            return self._solace.list_position_detail(
                default_account, detail_id, timeout=timeout, cb=cb
            )


    def list_profit_loss(
        self,
        account: Account = None,
        begin_date: str = "",
        end_date: str = "",
        unit: Unit = Unit.Common,
        timeout: int = 5000,
        cb = None,
        # cb: typing.Callable[
        #     [typing.List[typing.Union[StockProfitLoss, FutureProfitLoss]]], None
        # ] = None,
    ) -> typing.List[typing.Union[StockProfitLoss, FutureProfitLoss]]:

        if account:
            profitloss = self._solace.list_profit_loss(account=account,
                                          begin_date=begin_date,
                                          end_date=end_date,
                                          unit=unit,
                                          timeout=timeout,
                                          )

            return profitloss

        else:
            profitloss = self._solace.list_profit_loss(account=self.stock_account,
                                          begin_date=begin_date,
                                          end_date=end_date,
                                          unit=unit,
                                          timeout=timeout,
                                          )

            return profitloss


    def settlements(
        self,
        account: Account = None,
        timeout: int = 5000,
        cb = None
        # cb: typing.Callable[[typing.List[SettlementV1]], None] = None,
    ) -> typing.List[Settlement]:
        """query stock account of settlements"""
        if account:
            return self._solace.settlements(account=account, timeout=timeout, cb=cb)

        else:
            if self.stock_account:
                return self._solace.settlements(account=self.stock_account, timeout=timeout, cb=cb)


    def list_trades(self) -> typing.List[Trade]:
        """list all trades"""
        return self._solace.trades_list
        # return self._solace.trades

    def get_close(self, code: str):
        """
        提供給 SDK 使用者直接查詢收盤價。
        內部呼叫 self._solace.get_close(code)。
        """
        return self._solace.get_close(code)

    def snapshots(
        self,
        contracts: typing.List[typing.Union[Option, Future, Stock, Index]],
        timeout: int = 30000,
        cb: typing.Callable[[Snapshot], None] = None,
    ) -> typing.List[Snapshot]:
        """
        snapshots
        目前僅提供收盤價(close)
        其餘待補充
        """
        snapshots = self._solace.snapshots(contracts, timeout, cb)
        return snapshots
