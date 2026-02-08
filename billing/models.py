# billing/models.py
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

from core.utils.coreModels import StampedOwnedActive, BranchScopedStampedOwnedActive


# ----------------------------- choices -----------------------------

class CartStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CHECKED_OUT = "checked_out", "Checked Out"
    ABANDONED = "abandoned", "Abandoned"


class OrderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"                 # building order
    PENDING = "pending", "Pending Payment"   # waiting for gateway
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"


class PaymentStatus(models.TextChoices):
    INITIATED = "initiated", "Initiated"
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"


class PaymentProvider(models.TextChoices):
    KHALTI = "khalti", "Khalti"
    ESEWA = "esewa", "eSewa"
    STRIPE = "stripe", "Stripe"
    PAYPAL = "paypal", "PayPal"
    BANK = "bank", "Bank Transfer"
    CASH = "cash", "Cash"
    MANUAL = "manual", "Manual"


class CouponType(models.TextChoices):
    PERCENT = "percent", "Percent"
    FIXED = "fixed", "Fixed Amount"


class DiscountAppliesTo(models.TextChoices):
    ALL = "all", "All Items"
    COURSE = "course", "Specific Course"


class InvoiceStatus(models.TextChoices):
    ISSUED = "issued", "Issued"
    VOID = "void", "Void"


class RefundStatus(models.TextChoices):
    REQUESTED = "requested", "Requested"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PROCESSED = "processed", "Processed"


# ----------------------------- cart -----------------------------

class Cart(BranchScopedStampedOwnedActive):
    """
    One active cart per user per branch.
    LMS carts usually only have qty=1 course items.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        db_index=True,
    )

    status = models.CharField(max_length=20, choices=CartStatus.choices, default=CartStatus.ACTIVE, db_index=True)

    currency_code = models.CharField(max_length=3, default="NPR", db_index=True)

    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "carts"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["branch", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "branch"],
                condition=Q(status=CartStatus.ACTIVE),
                name="uniq_active_cart_user_branch",
            )
        ]

    def __str__(self):
        return f"Cart({self.user_id}, {self.status})"


class CartItem(StampedOwnedActive):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", db_index=True)

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="cart_items",
        db_index=True,
    )

    qty = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    # snapshot pricing at time of adding to cart
    currency_code = models.CharField(max_length=3, default="NPR", db_index=True)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = "cart_items"
        constraints = [
            models.UniqueConstraint(fields=["cart", "course"], name="uniq_cart_course"),
        ]
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.cart_id} -> {self.course_id}"

    def recalc(self, save=True):
        self.line_total = (self.unit_price or 0) * Decimal(self.qty or 1)
        if save:
            self.save(update_fields=["line_total", "updated"])


# ----------------------------- coupons -----------------------------

class Coupon(BranchScopedStampedOwnedActive):
    code = models.CharField(max_length=40, db_index=True)  # "WELCOME10"
    name = models.CharField(max_length=120, blank=True, null=True)

    coupon_type = models.CharField(max_length=10, choices=CouponType.choices, default=CouponType.PERCENT, db_index=True)

    # percent 0-100 OR fixed amount
    value = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    applies_to = models.CharField(max_length=10, choices=DiscountAppliesTo.choices, default=DiscountAppliesTo.ALL, db_index=True)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="coupons",
    )

    currency_code = models.CharField(max_length=3, blank=True, null=True)  # required for FIXED discounts ideally

    max_uses_total = models.PositiveIntegerField(blank=True, null=True)
    max_uses_per_user = models.PositiveIntegerField(blank=True, null=True)

    used_count = models.PositiveIntegerField(default=0)

    min_order_total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    starts_at = models.DateTimeField(blank=True, null=True, db_index=True)
    ends_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        db_table = "coupons"
        constraints = [
            models.UniqueConstraint(fields=["branch", "code"], name="uniq_coupon_branch_code"),
        ]
        indexes = [
            models.Index(fields=["branch", "active"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return self.code

    def is_valid_now(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        if self.max_uses_total is not None and self.used_count >= self.max_uses_total:
            return False
        return True


class CouponRedemption(StampedOwnedActive):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name="redemptions", db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_redemptions", db_index=True)
    order = models.ForeignKey("billing.Order", on_delete=models.CASCADE, related_name="coupon_redemptions", db_index=True)

    class Meta:
        db_table = "coupon_redemptions"
        indexes = [
            models.Index(fields=["coupon", "user"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["coupon", "order"], name="uniq_coupon_order"),
        ]

    def __str__(self):
        return f"{self.coupon_id} -> {self.order_id}"


# ----------------------------- orders -----------------------------

class Order(BranchScopedStampedOwnedActive):
    """
    An order is the commercial record. Enrollment is created when payment succeeds.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
    )

    order_no = models.CharField(max_length=60, blank=True, null=True, db_index=True)  # from NumberSequence if you want
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True)

    currency_code = models.CharField(max_length=3, default="NPR", db_index=True)

    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, blank=True, null=True, related_name="orders")
    coupon_code_snapshot = models.CharField(max_length=40, blank=True, null=True)

    paid_at = models.DateTimeField(blank=True, null=True, db_index=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancel_reason = models.TextField(blank=True, null=True)

    # Billing / customer details snapshot (simple MVP approach)
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=30, blank=True, null=True)

    billing_address = models.JSONField(default=dict, blank=True)  # {"country":"", "city":"", ...}

    # gateway or external refs
    gateway_order_ref = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["status", "paid_at"]),
            models.Index(fields=["order_no"]),
        ]

    def __str__(self):
        return f"Order({self.order_no or self.id})"

    def mark_paid(self, paid_at=None):
        self.status = OrderStatus.PAID
        self.paid_at = paid_at or timezone.now()
        self.save(update_fields=["status", "paid_at", "updated"])


class OrderItem(StampedOwnedActive):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", db_index=True)

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.PROTECT,
        related_name="order_items",
        db_index=True,
    )

    qty = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    # snapshot pricing
    currency_code = models.CharField(max_length=3, default="NPR", db_index=True)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    # informational snapshot (so invoice stays stable even if course title changes)
    course_title_snapshot = models.CharField(max_length=220, blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "order_items"
        constraints = [
            models.UniqueConstraint(fields=["order", "course"], name="uniq_order_course"),
        ]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.order_id} -> {self.course_id}"

    def recalc(self, save=True):
        qty = Decimal(self.qty or 1)
        base = (self.unit_price or 0) * qty
        self.line_total = base - (self.discount_amount or 0) + (self.tax_amount or 0)
        if save:
            self.save(update_fields=["line_total", "updated"])


# ----------------------------- payments -----------------------------

class Payment(BranchScopedStampedOwnedActive):
    """
    Each payment attempt for an order (you might have retries).
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments", db_index=True)

    provider = models.CharField(max_length=20, choices=PaymentProvider.choices, db_index=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.INITIATED, db_index=True)

    currency_code = models.CharField(max_length=3, default="NPR", db_index=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    initiated_at = models.DateTimeField(default=timezone.now, db_index=True)
    completed_at = models.DateTimeField(blank=True, null=True, db_index=True)

    # gateway references (transaction IDs, tokens, etc.)
    gateway_payment_ref = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    gateway_session_ref = models.CharField(max_length=120, blank=True, null=True, db_index=True)

    failure_reason = models.CharField(max_length=255, blank=True, null=True)

    raw_request = models.JSONField(default=dict, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["provider", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["gateway_payment_ref"]),
        ]

    def __str__(self):
        return f"Payment({self.order_id}, {self.provider}, {self.status})"

    def save(self, *args, **kwargs):
        # keep branch consistent with order
        if self.order_id and self.branch_id is None:
            self.branch = self.order.branch
        super().save(*args, **kwargs)

    def mark_succeeded(self, completed_at=None):
        self.status = PaymentStatus.SUCCEEDED
        self.completed_at = completed_at or timezone.now()
        self.save(update_fields=["status", "completed_at", "updated"])

    def mark_failed(self, reason=None):
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "failure_reason", "completed_at", "updated"])


# ----------------------------- invoices (optional but useful) -----------------------------

class Invoice(BranchScopedStampedOwnedActive):
    """
    Legal/business document (optional for Nepal MVP, but useful).
    You can generate this once an order is paid.
    """

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")

    invoice_no = models.CharField(max_length=60, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.ISSUED, db_index=True)

    issued_at = models.DateTimeField(default=timezone.now, db_index=True)

    pdf_url = models.URLField(blank=True, null=True)
    storage_key = models.CharField(max_length=255, blank=True, null=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "invoices"
        indexes = [
            models.Index(fields=["invoice_no"]),
            models.Index(fields=["branch", "issued_at"]),
        ]

    def __str__(self):
        return f"Invoice({self.invoice_no or self.id})"

    def save(self, *args, **kwargs):
        if self.order_id and self.branch_id is None:
            self.branch = self.order.branch
        super().save(*args, **kwargs)


# ----------------------------- refunds (optional) -----------------------------

class Refund(BranchScopedStampedOwnedActive):
    """
    Records refund requests and processing.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds", db_index=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, related_name="refunds")

    status = models.CharField(max_length=20, choices=RefundStatus.choices, default=RefundStatus.REQUESTED, db_index=True)

    currency_code = models.CharField(max_length=3, default="NPR", db_index=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    reason = models.TextField(blank=True, null=True)

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="refunds_requested",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="refunds_processed",
    )
    processed_at = models.DateTimeField(blank=True, null=True)

    gateway_refund_ref = models.CharField(max_length=120, blank=True, null=True, db_index=True)

    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "refunds"
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["branch", "status"]),
            models.Index(fields=["gateway_refund_ref"]),
        ]

    def __str__(self):
        return f"Refund({self.order_id}, {self.amount}, {self.status})"

    def save(self, *args, **kwargs):
        if self.order_id and self.branch_id is None:
            self.branch = self.order.branch
        super().save(*args, **kwargs)
