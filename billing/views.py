from core.utils.BulkModelViewSet import BaseModelViewSet
from billing.models import (
    Cart,
    CartItem,
    Coupon,
    CouponRedemption,
    Order,
    OrderItem,
    Payment,
    Invoice,
    Refund,
)
from billing.serializers import (
    CartSerializer,
    CartItemSerializer,
    CouponSerializer,
    CouponRedemptionSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer,
    InvoiceSerializer,
    RefundSerializer,
)
from billing.filters import (
    CartFilter,
    CartItemFilter,
    CouponFilter,
    CouponRedemptionFilter,
    OrderFilter,
    OrderItemFilter,
    PaymentFilter,
    InvoiceFilter,
    RefundFilter,
)


class CartViewSet(BaseModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    filterset_class = CartFilter
    search_fields = ["currency_code", "status"]
    ordering_fields = "__all__"


class CartItemViewSet(BaseModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    filterset_class = CartItemFilter
    search_fields = ["course__title"]
    ordering_fields = "__all__"


class CouponViewSet(BaseModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    filterset_class = CouponFilter
    search_fields = ["code", "name"]
    ordering_fields = "__all__"


class CouponRedemptionViewSet(BaseModelViewSet):
    queryset = CouponRedemption.objects.all()
    serializer_class = CouponRedemptionSerializer
    filterset_class = CouponRedemptionFilter
    search_fields = ["coupon__code", "order__order_no", "user__email"]
    ordering_fields = "__all__"


class OrderViewSet(BaseModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    search_fields = ["order_no", "customer_email", "customer_phone"]
    ordering_fields = "__all__"


class OrderItemViewSet(BaseModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filterset_class = OrderItemFilter
    search_fields = ["course_title_snapshot", "course__title"]
    ordering_fields = "__all__"


class PaymentViewSet(BaseModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    search_fields = ["gateway_payment_ref", "gateway_session_ref", "provider"]
    ordering_fields = "__all__"


class InvoiceViewSet(BaseModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filterset_class = InvoiceFilter
    search_fields = ["invoice_no"]
    ordering_fields = "__all__"


class RefundViewSet(BaseModelViewSet):
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    filterset_class = RefundFilter
    search_fields = ["gateway_refund_ref"]
    ordering_fields = "__all__"
