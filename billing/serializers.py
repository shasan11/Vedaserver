from core.utils.AdaptedBulkSerializer import BulkModelSerializer
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


class CartSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Cart
        fields = "__all__"


class CartItemSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CartItem
        fields = "__all__"


class CouponSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Coupon
        fields = "__all__"


class CouponRedemptionSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = CouponRedemption
        fields = "__all__"


class OrderSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Order
        fields = "__all__"


class OrderItemSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = OrderItem
        fields = "__all__"


class PaymentSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Payment
        fields = "__all__"


class InvoiceSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Invoice
        fields = "__all__"


class RefundSerializer(BulkModelSerializer):
    class Meta(BulkModelSerializer.Meta):
        model = Refund
        fields = "__all__"
