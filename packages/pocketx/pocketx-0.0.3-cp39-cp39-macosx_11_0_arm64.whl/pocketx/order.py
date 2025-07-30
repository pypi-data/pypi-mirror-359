import typing
import datetime

from pocketx.base import BaseModel, conint, StrictInt, ConStrAsciiMax6
from pocketx.account import Account
from pocketx.contracts import Contract, ComboContract
from pocketx.constant import (
    Action,
    FuturesPriceType,
    OrderType,
    FuturesOCType,
    StockPriceType,
    StockOrderCond,
    StockOrderLot,
    Status,
    OrderState,
    Act,
)


class Deal(BaseModel):
    seq: str
    price: typing.Union[StrictInt, float]
    quantity: int
    ts: float


class OrderStatus(BaseModel):
    id: str = ""
    status: Status
    status_code: str = ""
    web_id: str = ""
    msg: str = ""
    order_datetime: typing.Optional[datetime.datetime] = None
    modified_time: typing.Optional[datetime.datetime] = None
    modified_price: typing.Union[StrictInt, float] = 0
    order_quantity: int = 0
    deal_quantity: int = 0
    cancel_quantity: int = 0
    deals: typing.List[Deal] = None
    act: Act = None


class ComboStatus(OrderStatus):
    deals: typing.Dict[str, typing.List[Deal]] = None


class BaseOrder(BaseModel):
    action: Action
    price: typing.Union[StrictInt, float]
    quantity: conint(gt=0)
    account: Account = None
    custom_field: ConStrAsciiMax6 = ""


    def __repr_args__(self):
        return [
            (k, v)
            for k, v in self._iter(to_dict=False, exclude_defaults=True, exclude={"ca"})
        ]


class FuturesOrder(BaseOrder):
    price_type: FuturesPriceType
    order_type: OrderType
    octype: FuturesOCType = FuturesOCType.Auto


class StockOrder(BaseOrder):
    price_type: StockPriceType
    order_type: OrderType
    order_lot: StockOrderLot
    order_cond: StockOrderCond = StockOrderCond.Cash
    daytrade_short: bool = False
    id: str = ""
    seqno: str = ""
    ordno: str = ""
    seq: int = 0
    entid: str = ""

    ca: str = ""


class Order(StockOrder, FuturesOrder):
    price_type: typing.Union[StockPriceType, FuturesPriceType]
    order_type: OrderType

    def __init__(
        self,
        price: typing.Union[StrictInt, float],
        quantity: conint(gt=0),
        action: Action,
        price_type: typing.Union[StockPriceType, FuturesPriceType],
        order_type: OrderType,
        **kwargs
    ):
        super().__init__(
            **{
                **dict(
                    price=price,
                    quantity=quantity,
                    action=action,
                    price_type=price_type,
                    order_type=order_type,
                ),
                **kwargs,
            }
        )


class ComboOrder(FuturesOrder):
    action: Action = Action.Sell

    def __init__(
        self,
        price: typing.Union[StrictInt, float],
        quantity: conint(gt=0),
        price_type: FuturesPriceType,
        order_type: OrderType,
        action: Action = Action.Sell,
        **kwargs
    ):
        super().__init__(
            **{
                **dict(
                    price=price,
                    quantity=quantity,
                    action=action,
                    price_type=price_type,
                    order_type=order_type,
                ),
                **kwargs,
            }
        )

OrderTypeVar = typing.Union[Order, StockOrder, FuturesOrder]

class Trade(BaseModel):
    contract: Contract
    order: OrderTypeVar
    status: OrderStatus

    def __init__(self, contract: Contract, order: OrderTypeVar, status: OrderStatus):
        super().__init__(**dict(contract=contract, order=order, status=status))


class ComboTrade(BaseModel):
    contract: ComboContract
    order: OrderTypeVar
    status: ComboStatus

    def __init__(self, contract: ComboContract, order: OrderTypeVar, status: ComboStatus):
        super().__init__(**dict(contract=contract, order=order, status=status))


class OrderDealRecords(BaseModel):
    OrderState: OrderState
    record: typing.Dict
