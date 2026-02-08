import django_filters

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


class CartFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Cart
        fields = ["branch", "user", "status"]


class CartItemFilter(django_filters.FilterSet):
    cart = django_filters.UUIDFilter(field_name="cart_id")
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = CartItem
        fields = ["cart", "course"]


class CouponFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    code = django_filters.CharFilter(lookup_expr="iexact")
    coupon_type = django_filters.CharFilter(lookup_expr="iexact")
    applies_to = django_filters.CharFilter(lookup_expr="iexact")
    course = django_filters.UUIDFilter(field_name="course_id")
    active = django_filters.BooleanFilter()

    class Meta:
        model = Coupon
        fields = ["branch", "code", "coupon_type", "applies_to", "course", "active"]


class CouponRedemptionFilter(django_filters.FilterSet):
    coupon = django_filters.UUIDFilter(field_name="coupon_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    order = django_filters.UUIDFilter(field_name="order_id")

    class Meta:
        model = CouponRedemption
        fields = ["coupon", "user", "order"]


class OrderFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    user = django_filters.UUIDFilter(field_name="user_id")
    status = django_filters.CharFilter(lookup_expr="iexact")
    order_no = django_filters.CharFilter(lookup_expr="iexact")
    coupon = django_filters.UUIDFilter(field_name="coupon_id")

    class Meta:
        model = Order
        fields = ["branch", "user", "status", "order_no", "coupon"]


class OrderItemFilter(django_filters.FilterSet):
    order = django_filters.UUIDFilter(field_name="order_id")
    course = django_filters.UUIDFilter(field_name="course_id")

    class Meta:
        model = OrderItem
        fields = ["order", "course"]


class PaymentFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    order = django_filters.UUIDFilter(field_name="order_id")
    provider = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    gateway_payment_ref = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Payment
        fields = ["branch", "order", "provider", "status", "gateway_payment_ref"]


class InvoiceFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    order = django_filters.UUIDFilter(field_name="order_id")
    invoice_no = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Invoice
        fields = ["branch", "order", "invoice_no", "status"]


class RefundFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    order = django_filters.UUIDFilter(field_name="order_id")
    payment = django_filters.UUIDFilter(field_name="payment_id")
    status = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Refund
        fields = ["branch", "order", "payment", "status"]
