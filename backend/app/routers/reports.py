from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.report import SalesReport, InventoryReport, PopularItemsReport
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/sales", response_model=SalesReport)
def sales_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        total_orders = db.query(func.count(Order.id)).scalar() or 0
        total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0.0
        status_breakdown = (
            db.query(
                Order.status,
                func.count(Order.id).label("count"),
                func.sum(Order.total_amount).label("revenue"),
            )
            .group_by(Order.status)
            .all()
        )

        by_status = []
        for row in status_breakdown:
            by_status.append(
                {
                    "status": row.status,
                    "count": row.count,
                    "revenue": round(row.revenue or 0.0, 2),
                }
            )

        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "by_status": by_status,
        }
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500, detail=INTERNAL_ERROR_DETAIL
        )


@router.get("/inventory", response_model=InventoryReport)
def inventory_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        total_items = db.query(func.count(Inventory.id)).scalar() or 0
        total_stock = db.query(func.sum(Inventory.stock)).scalar() or 0
        low_stock_count = (
            db.query(func.count(Inventory.id))
            .filter(Inventory.stock <= Inventory.min_stock)
            .scalar()
            or 0
        )

        return {
            "total_items_tracked": total_items,
            "total_stock": total_stock,
            "low_stock_count": low_stock_count,
        }
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500,
            detail=INTERNAL_ERROR_DETAIL,
        )


@router.get("/popular", response_model=PopularItemsReport)
def popular_items_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        popular_items = (
            db.query(
                OrderItem.menu_item_id,
                func.sum(OrderItem.quantity).label("total_ordered"),
                func.count(OrderItem.order_id.distinct()).label("order_count"),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label(
                    "total_revenue"
                ),
            )
            .group_by(OrderItem.menu_item_id)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(20)
            .all()
        )

        results = []
        for row in popular_items:
            results.append(
                {
                    "menu_item_id": row.menu_item_id,
                    "total_ordered": row.total_ordered,
                    "order_count": row.order_count,
                    "total_revenue": round(row.total_revenue or 0.0, 2),
                }
            )

        return {"popular_items": results}
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            status_code=500,
            detail=INTERNAL_ERROR_DETAIL,
        )
