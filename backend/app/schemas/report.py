from typing import List
from pydantic import BaseModel


class StatusBreakdown(BaseModel):
    status: str
    count: int
    revenue: float


class SalesReport(BaseModel):
    total_orders: int
    total_revenue: float
    by_status: List[StatusBreakdown]


class InventoryReport(BaseModel):
    total_items_tracked: int
    total_stock: int
    low_stock_count: int


class PopularItem(BaseModel):
    menu_item_id: int
    total_ordered: int
    order_count: int
    total_revenue: float


class PopularItemsReport(BaseModel):
    popular_items: List[PopularItem]
