from django.urls import path, include
from rest_framework_bulk.routes import BulkRouter

from billing.views import (
    CartViewSet,
    CartItemViewSet,
    CouponViewSet,
    CouponRedemptionViewSet,
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet,
    InvoiceViewSet,
    RefundViewSet,
)

router = BulkRouter()
router.register(r"carts", CartViewSet, basename="cart")
router.register(r"cart-items", CartItemViewSet, basename="cart-item")
router.register(r"coupons", CouponViewSet, basename="coupon")
router.register(r"coupon-redemptions", CouponRedemptionViewSet, basename="coupon-redemption")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items", OrderItemViewSet, basename="order-item")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"refunds", RefundViewSet, basename="refund")

urlpatterns = [
    path("", include(router.urls)),
]
