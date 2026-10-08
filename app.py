"""
COLBA - نظام إدارة المخزون والمحل التجاري
إعادة بناء حديثة للبرنامج الأصلي (Tkinter + ملفات نصية)
باستخدام Flask + SQLAlchemy (Supabase/PostgreSQL أو SQLite محليًا) + واجهة ويب (PWA)

الدورة المالية والمخزنية:
1. إضافة منتجات جديدة يدويًا (مرة واحدة عند الإنشاء).
2. أي كمية جديدة تصل لاحقًا تُسجَّل عبر "فاتورة" (Invoice) وليس عبر تعديل الكمية يدويًا.
   الفاتورة تحدّث الكمية تلقائيًا، وإذا تغيّر سعر الشراء/البيع لمنتج له كمية سابقة
   يُسجَّل الفرق كـ"ربح/خسارة استثمارية" (PriceChangeLog) بدل تجاهله.
3. البيع الفعلي لا يتم يدويًا؛ يُستنتَج فقط من فروق الجرد (Stocktake) بين كمية البداية والنهاية.
4. المصاريف اليومية تُسجَّل بشكل منفصل عند إغلاق اليوم وتخصم من الصندوق.
5. عند إغلاق اليوم يمكن إدخال "المبلغ الحقيقي" الموجود فعليًا في الصندوق، ويقارنه
   النظام بالمبلغ المتوقع (CashCount) ويحسب فائض/عجز نقدي يُحفظ تاريخيًا.
6. أي سحب من الصندوق يتطلب ملاحظة توضح سبب السحب.
"""
import os
from datetime import datetime, date, timedelta
from collections import OrderedDict
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'colba.db')}")

# Render/Heroku/Supabase تعطي روابط postgres:// أو postgresql:// وهذه الصيغة
# الافتراضية تفترض ضمنيًا driver psycopg2. بسبب عدم توافق psycopg2-binary مع
# إصدارات بايثون الحديثة (خطأ ABI)، ينتقل المشروع إلى psycopg 3 (حزمة
# psycopg[binary])، ويتطلب هذا الـ driver تحديد ذلك صراحة في رابط الاتصال عبر
# postgresql+psycopg://. الاستبدال هنا يطال فقط بادئة المخطط (scheme) في أول
# الرابط، ولا يمسّ بقية الرابط (host/port/اسم القاعدة)، لذلك كلمة المرور حتى
# لو احتوت رموزًا خاصة (@ # % إلخ) تبقى كما هي دون أي كسر أو تشويه.
IS_POSTGRES = DB_PATH.startswith("postgres://") or DB_PATH.startswith("postgresql://")
if DB_PATH.startswith("postgres://"):
    DB_PATH = DB_PATH.replace("postgres://", "postgresql+psycopg://", 1)
elif DB_PATH.startswith("postgresql://") and not DB_PATH.startswith("postgresql+psycopg://"):
    DB_PATH = DB_PATH.replace("postgresql://", "postgresql+psycopg://", 1)

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


def parse_date_arg(value):
    """
    يحوّل نص تاريخ (YYYY-MM-DD) إلى كائن date حقيقي. الأعمدة من نوع Date في
    PostgreSQL لا تقبل المقارنة المباشرة مع نص (خطأ:
    "operator does not exist: date = character varying")، بعكس SQLite التي
    كانت تتساهل مع ذلك. لذلك يجب دائمًا تحويل أي تاريخ قادم من query string
    إلى date قبل استخدامه في فلاتر SQLAlchemy.
    """
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


# ---------------------------------------------------------------------------
# النماذج (Models)
# ---------------------------------------------------------------------------

class Category(db.Model):
    """
    صنف/فئة لتصنيف المنتجات (مثال: مواد غذائية، مشروبات، أدوات منزلية)،
    تُستخدم لتجميع المنتجات المتشابهة بجانب بعضها في شاشة المنتجات بدل
    عرضها مختلطة بدون ترتيب.
    """
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sort_order": self.sort_order,
            "products_count": len(self.products) if self.products else 0,
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    buy_price = db.Column(db.Float, nullable=False, default=0)
    sell_price = db.Column(db.Float, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship("Category", backref="products")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "purchase_total": round(self.quantity * self.buy_price, 2),
            "sell_total": round(self.quantity * self.sell_price, 2),
            "profit_total": round(self.quantity * (self.sell_price - self.buy_price), 2),
        }


class Costs(db.Model):
    __tablename__ = "costs"

    id = db.Column(db.Integer, primary_key=True)
    project_costs = db.Column(db.Float, nullable=False, default=0)
    tax_costs = db.Column(db.Float, nullable=False, default=0)
    labor_costs = db.Column(db.Float, nullable=False, default=0)
    labor_mode = db.Column(db.String(20), nullable=False, default="percent")  # 'percent' أو 'fixed'
    box_balance = db.Column(db.Float, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "project_costs": self.project_costs,
            "tax_costs": self.tax_costs,
            "labor_costs": self.labor_costs,
            "labor_mode": self.labor_mode or "percent",
            "box_balance": self.box_balance,
        }


class SaleRecord(db.Model):
    __tablename__ = "sale_records"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sell_price_at_time = db.Column(db.Float, nullable=False)
    buy_price_at_time = db.Column(db.Float, nullable=False)
    sold_at = db.Column(db.Date, default=date.today)
    source = db.Column(db.String(20), nullable=False, default="manual")  # 'manual' أو 'stocktake'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # يجمع كل بنود عملية جرد واحدة (دفعة واحدة من الحفظ) تحت نفس الرقم، حتى
    # يمكن عرضها كقسم واحد متتالٍ في القائمة (مثل فاتورة) وتمييزه عن عملية
    # جرد أخرى نُفِّذت في نفس اليوم لاحقًا.
    stocktake_batch_id = db.Column(db.Integer, nullable=True)

    product = db.relationship("Product", backref="sales")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity_sold": self.quantity_sold,
            "sell_price_at_time": self.sell_price_at_time,
            "buy_price_at_time": self.buy_price_at_time,
            "profit": round(self.quantity_sold * (self.sell_price_at_time - self.buy_price_at_time), 2),
            "sold_at": self.sold_at.isoformat() if self.sold_at else None,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "stocktake_batch_id": self.stocktake_batch_id,
        }


class BoxTransaction(db.Model):
    __tablename__ = "box_transactions"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StocktakeSession(db.Model):
    """جلسة جرد: فتح بكمية بداية، وإغلاق لاحقًا بكمية نهاية يُحسب الفرق منها كمبيع"""
    __tablename__ = "stocktake_sessions"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    start_quantity = db.Column(db.Integer, nullable=False)
    end_quantity = db.Column(db.Integer, nullable=True)
    sold_quantity = db.Column(db.Integer, nullable=True)
    note = db.Column(db.String(300))
    is_open = db.Column(db.Boolean, nullable=False, default=True)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    sale_record_id = db.Column(db.Integer, db.ForeignKey("sale_records.id"), nullable=True)

    product = db.relationship("Product")
    sale_record = db.relationship("SaleRecord")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "start_quantity": self.start_quantity,
            "end_quantity": self.end_quantity,
            "sold_quantity": self.sold_quantity,
            "note": self.note,
            "is_open": self.is_open,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


class Invoice(db.Model):
    """
    فاتورة إضافة مخزون: تمثّل استلام كمية جديدة من منتج واحد أو أكثر (مثلاً من
    مورد). هذه هي الطريقة الوحيدة المعتمدة لزيادة كمية منتج موجود مسبقًا —
    بدل تعديل الكمية يدويًا من شاشة المنتجات.
    """
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_date = db.Column(db.Date, nullable=False, default=date.today)
    note = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("InvoiceItem", backref="invoice", cascade="all, delete-orphan")

    def to_dict(self, include_items=True):
        items = list(self.items)
        total_cost = sum((it.quantity * it.buy_price) for it in items)
        total_quantity = sum(it.quantity for it in items)
        d = {
            "id": self.id,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_cost": round(total_cost, 2),
            "total_quantity": total_quantity,
            "items_count": len(items),
        }
        if include_items:
            d["items"] = [it.to_dict() for it in items]
        return d


class InvoiceItem(db.Model):
    """
    سطر داخل فاتورة: منتج + كمية مضافة + سعر الشراء/البيع وقت الفاتورة (وقد
    يختلفان عن السعر السابق للمنتج، وهذا الفرق يُتتبَّع عبر PriceChangeLog).
    """
    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name_snapshot = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable=False)
    buy_price = db.Column(db.Float, nullable=False, default=0)
    sell_price = db.Column(db.Float, nullable=False, default=0)
    prev_buy_price = db.Column(db.Float, nullable=True)
    prev_sell_price = db.Column(db.Float, nullable=True)
    prev_quantity = db.Column(db.Integer, nullable=True)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else self.product_name_snapshot,
            "quantity": self.quantity,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "prev_buy_price": self.prev_buy_price,
            "prev_sell_price": self.prev_sell_price,
            "prev_quantity": self.prev_quantity,
            "line_cost": round(self.quantity * self.buy_price, 2),
        }


class PriceChangeLog(db.Model):
    """
    سجل تغيّر سعر منتج بسبب فاتورة جديدة، عندما يكون للمنتج كمية سابقة بسعر
    مختلف. الفرق يُحتسب على إجمالي الكمية بعد الدمج (القديمة + الجديدة)
    ويُصنَّف كـ"ربح استثماري" إذا ارتفع السعر، أو "خسارة استثمارية" إذا انخفض.
    """
    __tablename__ = "price_change_logs"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=True)
    price_field = db.Column(db.String(10), nullable=False)  # 'buy' أو 'sell'
    old_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    quantity_affected = db.Column(db.Integer, nullable=False)
    impact = db.Column(db.Float, nullable=False)  # (new-old) * quantity_affected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "invoice_id": self.invoice_id,
            "price_field": self.price_field,
            "old_price": self.old_price,
            "new_price": self.new_price,
            "quantity_affected": self.quantity_affected,
            "impact": round(self.impact, 2),
            "direction": "gain" if self.impact > 0 else ("loss" if self.impact < 0 else "none"),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CashCount(db.Model):
    """
    مطابقة الصندوق عند إغلاق اليوم: يقارن المبلغ الحقيقي المُدخَل يدويًا بعد عدّ
    الصندوق فعليًا، بالمبلغ المتوقع من النظام (رصيد الصندوق بعد صافي مبيعات
    اليوم مطروحًا منها المصاريف). الفرق يُحفظ كفائض/عجز نقدي تاريخي.
    """
    __tablename__ = "cash_counts"

    id = db.Column(db.Integer, primary_key=True)
    count_date = db.Column(db.Date, nullable=False, default=date.today)
    expected_cash = db.Column(db.Float, nullable=False, default=0)
    actual_cash = db.Column(db.Float, nullable=False, default=0)
    diff = db.Column(db.Float, nullable=False, default=0)  # actual - expected
    daily_total = db.Column(db.Float, nullable=False, default=0)
    daily_expenses = db.Column(db.Float, nullable=False, default=0)
    note = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "count_date": self.count_date.isoformat() if self.count_date else None,
            "expected_cash": round(self.expected_cash, 2),
            "actual_cash": round(self.actual_cash, 2),
            "diff": round(self.diff, 2),
            "status": "surplus" if self.diff > 0 else ("deficit" if self.diff < 0 else "matched"),
            "daily_total": round(self.daily_total, 2),
            "daily_expenses": round(self.daily_expenses, 2),
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def get_or_create_costs():
    costs = Costs.query.first()
    if not costs:
        costs = Costs(project_costs=0, tax_costs=0, labor_costs=0, labor_mode="percent", box_balance=0)
        db.session.add(costs)
        db.session.commit()
    return costs


# ---------------------------------------------------------------------------
# API: الأصناف
# ---------------------------------------------------------------------------

@app.route("/api/categories", methods=["GET"])
def list_categories():
    categories = Category.query.order_by(Category.sort_order.asc(), Category.name.asc()).all()
    return jsonify([c.to_dict() for c in categories])


@app.route("/api/categories", methods=["POST"])
def create_category():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "اسم الصنف مطلوب"}), 400

    existing = Category.query.filter(db.func.lower(Category.name) == name.lower()).first()
    if existing:
        return jsonify({"error": "يوجد صنف بهذا الاسم بالفعل"}), 400

    try:
        sort_order = int(data.get("sort_order", 0) or 0)
    except (TypeError, ValueError):
        sort_order = 0

    if not data.get("sort_order"):
        max_order = db.session.query(db.func.max(Category.sort_order)).scalar() or 0
        sort_order = max_order + 1

    category = Category(name=name, sort_order=sort_order)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@app.route("/api/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json(force=True)

    if "name" in data and data["name"] is not None and str(data["name"]).strip() != "":
        new_name = str(data["name"]).strip()
        dup = Category.query.filter(
            db.func.lower(Category.name) == new_name.lower(), Category.id != category.id
        ).first()
        if dup:
            return jsonify({"error": "يوجد صنف آخر بهذا الاسم بالفعل"}), 400
        category.name = new_name
    if "sort_order" in data and data["sort_order"] not in (None, ""):
        category.sort_order = int(data["sort_order"])

    db.session.commit()
    return jsonify(category.to_dict())


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    """
    حذف صنف: لا يحذف المنتجات المرتبطة به، فقط يفرغ حقل category_id لديها
    (تعود المنتجات إلى "بدون صنف") حتى لا تُفقد بياناتها.
    """
    category = Category.query.get_or_404(category_id)
    for product in list(category.products):
        product.category_id = None
    db.session.delete(category)
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API: المنتجات
# ---------------------------------------------------------------------------

@app.route("/api/products", methods=["GET"])
def list_products():
    products = (
        Product.query.outerjoin(Category)
        .order_by(
            db.case((Category.id.is_(None), 1), else_=0).asc(),
            Category.sort_order.asc(),
            Category.name.asc(),
            Product.name.asc(),
        )
        .all()
    )
    return jsonify([p.to_dict() for p in products])


@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "اسم المنتج مطلوب"}), 400
    try:
        quantity = int(data.get("quantity", 0))
        buy_price = float(data.get("buy_price", 0))
        sell_price = float(data.get("sell_price", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "قيم غير صحيحة"}), 400

    category_id = data.get("category_id") or None
    if category_id:
        try:
            category_id = int(category_id)
        except (TypeError, ValueError):
            return jsonify({"error": "صنف غير صحيح"}), 400
        if not Category.query.get(category_id):
            return jsonify({"error": "الصنف المحدد غير موجود"}), 400

    product = Product(
        name=name, quantity=quantity, buy_price=buy_price, sell_price=sell_price, category_id=category_id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(force=True)

    if "name" in data and data["name"] is not None and str(data["name"]).strip() != "":
        product.name = str(data["name"]).strip()
    if "quantity" in data and data["quantity"] not in (None, ""):
        product.quantity = int(data["quantity"])
    if "buy_price" in data and data["buy_price"] not in (None, ""):
        product.buy_price = float(data["buy_price"])
    if "sell_price" in data and data["sell_price"] not in (None, ""):
        product.sell_price = float(data["sell_price"])
    if "category_id" in data:
        category_id = data["category_id"] or None
        if category_id:
            try:
                category_id = int(category_id)
            except (TypeError, ValueError):
                return jsonify({"error": "صنف غير صحيح"}), 400
            if not Category.query.get(category_id):
                return jsonify({"error": "الصنف المحدد غير موجود"}), 400
        product.category_id = category_id

    db.session.commit()
    return jsonify(product.to_dict())


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API: الفواتير (إضافة مخزون)
# ---------------------------------------------------------------------------

@app.route("/api/invoices", methods=["GET"])
def list_invoices():
    sort_by = request.args.get("sort_by", "date_desc")

    invoices = Invoice.query.all()
    items = [inv.to_dict() for inv in invoices]

    sort_map = {
        "date_desc": lambda x: (x["invoice_date"] or "", x["id"]),
        "date_asc": lambda x: (x["invoice_date"] or "", x["id"]),
        "cost_desc": lambda x: x["total_cost"],
        "cost_asc": lambda x: x["total_cost"],
        "qty_desc": lambda x: x["total_quantity"],
        "qty_asc": lambda x: x["total_quantity"],
    }
    reverse_map = {
        "date_desc": True, "date_asc": False,
        "cost_desc": True, "cost_asc": False,
        "qty_desc": True, "qty_asc": False,
    }
    key_fn = sort_map.get(sort_by, sort_map["date_desc"])
    items.sort(key=key_fn, reverse=reverse_map.get(sort_by, True))

    return jsonify(items)


@app.route("/api/invoices/<int:invoice_id>", methods=["GET"])
def get_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify(invoice.to_dict())


@app.route("/api/invoices", methods=["POST"])
def create_invoice():
    """
    إنشاء فاتورة إضافة مخزون. كل سطر (item) يحتوي إما:
      - product_id لمنتج موجود، أو
      - name (+ اختياريًا buy_price/sell_price) لإنشاء منتج جديد مباشرة.

    لكل سطر لمنتج له كمية سابقة > 0 وتغيّر سعره (شراء أو بيع)، يُسجَّل الفرق
    في PriceChangeLog محسوبًا على إجمالي الكمية بعد الدمج (قديم + جديد)،
    باعتباره ربحًا أو خسارة استثمارية على المخزون القائم.
    """
    data = request.get_json(force=True)
    invoice_date_raw = data.get("invoice_date") or date.today().isoformat()
    invoice_date = parse_date_arg(invoice_date_raw)
    note = (data.get("note") or "").strip() or None
    raw_items = data.get("items") or []

    if not raw_items:
        return jsonify({"error": "يجب إضافة منتج واحد على الأقل للفاتورة"}), 400

    invoice = Invoice(invoice_date=invoice_date, note=note)
    db.session.add(invoice)
    db.session.flush()

    price_logs = []

    for raw in raw_items:
        try:
            qty = int(raw.get("quantity", 0))
        except (TypeError, ValueError):
            db.session.rollback()
            return jsonify({"error": "كمية غير صحيحة في أحد بنود الفاتورة"}), 400
        if qty <= 0:
            db.session.rollback()
            return jsonify({"error": "يجب أن تكون كمية كل منتج أكبر من صفر"}), 400

        product_id = raw.get("product_id")
        product = None
        if product_id:
            product = Product.query.get(int(product_id))
            if not product:
                db.session.rollback()
                return jsonify({"error": "منتج غير موجود في أحد بنود الفاتورة"}), 400
        else:
            new_name = (raw.get("name") or "").strip()
            if not new_name:
                db.session.rollback()
                return jsonify({"error": "اسم المنتج مطلوب عند إضافة منتج جديد من الفاتورة"}), 400
            try:
                new_buy = float(raw.get("buy_price", 0) or 0)
                new_sell = float(raw.get("sell_price", 0) or 0)
            except (TypeError, ValueError):
                db.session.rollback()
                return jsonify({"error": "سعر غير صحيح لمنتج جديد في الفاتورة"}), 400
            new_category_id = raw.get("category_id") or None
            if new_category_id:
                try:
                    new_category_id = int(new_category_id)
                except (TypeError, ValueError):
                    db.session.rollback()
                    return jsonify({"error": "صنف غير صحيح لمنتج جديد في الفاتورة"}), 400
            product = Product(
                name=new_name, quantity=0, buy_price=new_buy, sell_price=new_sell, category_id=new_category_id
            )
            db.session.add(product)
            db.session.flush()

        try:
            new_buy_price = raw.get("buy_price")
            new_buy_price = float(new_buy_price) if new_buy_price not in (None, "") else product.buy_price
            new_sell_price = raw.get("sell_price")
            new_sell_price = float(new_sell_price) if new_sell_price not in (None, "") else product.sell_price
        except (TypeError, ValueError):
            db.session.rollback()
            return jsonify({"error": "سعر غير صحيح في أحد بنود الفاتورة"}), 400

        prev_quantity = product.quantity
        prev_buy_price = product.buy_price
        prev_sell_price = product.sell_price

        # إذا كان للمنتج كمية سابقة وتغيّر السعر، سجّل الفرق كربح/خسارة
        # استثمارية على إجمالي الكمية بعد الدمج (قديم + جديد).
        combined_quantity = prev_quantity + qty
        if prev_quantity > 0:
            if new_buy_price != prev_buy_price:
                impact = (new_buy_price - prev_buy_price) * combined_quantity
                # ارتفاع سعر الشراء يعني كلفة أعلى لاحقًا؛ نعتبره من منظور
                # قيمة المخزون: سعر شراء أعلى = المخزون "يكلّف" أكثر (لا نعتبره
                # ربحًا)، لذلك نعكس الإشارة لسعر الشراء تحديدًا.
                log = PriceChangeLog(
                    product_id=product.id,
                    invoice_id=invoice.id,
                    price_field="buy",
                    old_price=prev_buy_price,
                    new_price=new_buy_price,
                    quantity_affected=combined_quantity,
                    impact=-impact,
                )
                db.session.add(log)
                price_logs.append(log)
            if new_sell_price != prev_sell_price:
                impact = (new_sell_price - prev_sell_price) * combined_quantity
                log = PriceChangeLog(
                    product_id=product.id,
                    invoice_id=invoice.id,
                    price_field="sell",
                    old_price=prev_sell_price,
                    new_price=new_sell_price,
                    quantity_affected=combined_quantity,
                    impact=impact,
                )
                db.session.add(log)
                price_logs.append(log)

        item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=product.id,
            product_name_snapshot=product.name,
            quantity=qty,
            buy_price=new_buy_price,
            sell_price=new_sell_price,
            prev_buy_price=prev_buy_price,
            prev_sell_price=prev_sell_price,
            prev_quantity=prev_quantity,
        )
        db.session.add(item)

        product.quantity = combined_quantity
        product.buy_price = new_buy_price
        product.sell_price = new_sell_price

    db.session.commit()

    return jsonify({
        "invoice": invoice.to_dict(),
        "price_changes": [log.to_dict() for log in price_logs],
    }), 201


@app.route("/api/invoices/<int:invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id):
    """
    حذف فاتورة (تصحيح خطأ إدخال فقط) — يعكس أثرها على كمية المنتجات المرتبطة
    بها إن أمكن، دون التأثير على أسعارها الحالية (لتفادي التعقيد في حال طرأت
    فواتير أخرى لاحقًا على نفس المنتج).
    """
    invoice = Invoice.query.get_or_404(invoice_id)
    for item in invoice.items:
        product = item.product
        if product:
            product.quantity = max(0, product.quantity - item.quantity)
    PriceChangeLog.query.filter_by(invoice_id=invoice.id).delete()
    db.session.delete(invoice)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/price-changes", methods=["GET"])
def list_price_changes():
    logs = PriceChangeLog.query.order_by(PriceChangeLog.created_at.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs])


@app.route("/api/price-changes/timeseries", methods=["GET"])
def price_changes_timeseries():
    """
    سلسلة زمنية لتغيّرات الأسعار (شراء/بيع) الناتجة عن الفواتير، لعرضها في
    التحليلات كرسم بياني عبر الوقت. يمكن تصفيتها اختياريًا بمنتج واحد عبر
    product_id. تُرجع أيضًا آخر تغيّر لكل حقل سعر (شراء/بيع) لكل منتج، وهو
    ما تستخدمه الواجهة لرسم سهم أخضر/أحمر بجانب السعر في بطاقة المنتج.
    """
    product_id = request.args.get("product_id")
    try:
        limit = int(request.args.get("limit", 200))
    except (TypeError, ValueError):
        limit = 200
    limit = max(1, min(limit, 1000))

    query = PriceChangeLog.query
    if product_id:
        try:
            query = query.filter_by(product_id=int(product_id))
        except (TypeError, ValueError):
            return jsonify({"error": "product_id غير صحيح"}), 400

    logs = query.order_by(PriceChangeLog.created_at.asc()).limit(limit).all()

    points = [{
        "date": log.created_at.date().isoformat() if log.created_at else None,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        "product_id": log.product_id,
        "product_name": log.product.name if log.product else None,
        "price_field": log.price_field,
        "old_price": log.old_price,
        "new_price": log.new_price,
        "direction": "up" if log.new_price > log.old_price else ("down" if log.new_price < log.old_price else "none"),
        "impact": round(log.impact, 2),
    } for log in logs]

    # آخر تغيّر مسجّل لكل (منتج، حقل سعر) — تستخدمه الواجهة لعرض السهم
    latest_by_product_field = {}
    for log in logs:  # logs مرتّبة تصاعديًا، لذا آخر عنصر لكل مفتاح هو الأحدث
        key = f"{log.product_id}:{log.price_field}"
        latest_by_product_field[key] = {
            "product_id": log.product_id,
            "price_field": log.price_field,
            "old_price": log.old_price,
            "new_price": log.new_price,
            "direction": "up" if log.new_price > log.old_price else ("down" if log.new_price < log.old_price else "none"),
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }

    return jsonify({
        "points": points,
        "latest_changes": list(latest_by_product_field.values()),
    })


# ---------------------------------------------------------------------------
# API: التكاليف
# ---------------------------------------------------------------------------

@app.route("/api/costs", methods=["GET"])
def get_costs():
    return jsonify(get_or_create_costs().to_dict())


@app.route("/api/costs", methods=["PUT"])
def update_costs():
    costs = get_or_create_costs()
    data = request.get_json(force=True)
    for field in ("project_costs", "tax_costs", "labor_costs", "box_balance"):
        if field in data and data[field] not in (None, ""):
            setattr(costs, field, float(data[field]))
    if "labor_mode" in data and data["labor_mode"] in ("percent", "fixed"):
        costs.labor_mode = data["labor_mode"]
    db.session.commit()
    return jsonify(costs.to_dict())


# ---------------------------------------------------------------------------
# API: الصندوق
# ---------------------------------------------------------------------------

@app.route("/api/box/transactions", methods=["POST"])
def add_box_transaction():
    data = request.get_json(force=True)
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "قيمة غير صحيحة"}), 400

    note = (data.get("note") or "").strip()
    # السحب (مبلغ سالب) يتطلب ملاحظة توضح سبب السحب حتى يبقى لكل نقصان في
    # الصندوق سبب موثّق يمكن الرجوع إليه لاحقًا.
    if amount < 0 and not note:
        return jsonify({"error": "يجب إدخال ملاحظة توضح سبب السحب"}), 400

    tx = BoxTransaction(amount=amount, note=note or None)
    db.session.add(tx)

    costs = get_or_create_costs()
    costs.box_balance += amount
    db.session.commit()
    return jsonify({"transaction": tx.to_dict(), "costs": costs.to_dict()})


@app.route("/api/box/transactions", methods=["GET"])
def list_box_transactions():
    try:
        limit = int(request.args.get("limit", 50))
    except (TypeError, ValueError):
        limit = 50
    limit = max(1, min(limit, 200))
    txs = BoxTransaction.query.order_by(BoxTransaction.created_at.desc()).limit(limit).all()
    return jsonify([t.to_dict() for t in txs])


# ---------------------------------------------------------------------------
# API: لوحة الملخص
# ---------------------------------------------------------------------------

@app.route("/api/summary", methods=["GET"])
def summary():
    products = Product.query.all()
    costs = get_or_create_costs()

    capital = sum(p.quantity * p.buy_price for p in products)
    sell_all = sum(p.quantity * p.sell_price for p in products)
    actual_return = sell_all - capital
    total_costs = costs.project_costs + costs.tax_costs
    total_return = sell_all - total_costs
    total_capital_with_box = capital + costs.box_balance

    # الفائض/العجز النقدي: آخر مطابقة صندوق مسجّلة (من إغلاق يوم سابق)
    last_cash_count = CashCount.query.order_by(CashCount.created_at.desc()).first()
    cash_surplus = last_cash_count.diff if last_cash_count else 0

    return jsonify({
        "capital": round(capital, 2),
        "actual_return": round(actual_return, 2),
        "total_return": round(total_return, 2),
        "total_capital_with_box": round(total_capital_with_box, 2),
        "box_balance": round(costs.box_balance, 2),
        "cash_surplus": round(cash_surplus, 2),
        "last_cash_count_date": last_cash_count.count_date.isoformat() if last_cash_count else None,
        "project_costs": round(costs.project_costs, 2),
        "tax_costs": round(costs.tax_costs, 2),
        "labor_costs": round(costs.labor_costs, 2),
        "labor_mode": costs.labor_mode,
        "products_count": len(products),
    })


# ---------------------------------------------------------------------------
# API: الإحصاء اليومي
# ---------------------------------------------------------------------------

@app.route("/api/stats/daily", methods=["GET"])
def daily_stats():
    target_date_str = request.args.get("date", date.today().isoformat())
    target_date = parse_date_arg(target_date_str)

    records = SaleRecord.query.filter(SaleRecord.sold_at == target_date).all()

    daily_profit = sum(r.quantity_sold * (r.sell_price_at_time - r.buy_price_at_time) for r in records)
    daily_capital = sum(r.quantity_sold * r.buy_price_at_time for r in records)
    daily_total = sum(r.quantity_sold * r.sell_price_at_time for r in records)

    costs = get_or_create_costs()
    if costs.labor_mode == "fixed":
        labor_share = costs.labor_costs or 0
    else:
        labor_share = (costs.labor_costs * daily_profit) / 100 if costs.labor_costs else 0

    by_product = {}
    for r in records:
        pid = r.product_id
        if pid not in by_product:
            by_product[pid] = {
                "product_id": pid,
                "product_name": r.product.name if r.product else "",
                "quantity_sold": 0,
                "buy_price": r.buy_price_at_time,
                "sell_price": r.sell_price_at_time,
            }
        by_product[pid]["quantity_sold"] += r.quantity_sold

    existing_cash_count = CashCount.query.filter_by(count_date=target_date).first()

    return jsonify({
        "date": target_date.isoformat(),
        "daily_profit": round(daily_profit, 2),
        "daily_capital": round(daily_capital, 2),
        "daily_total": round(daily_total, 2),
        "labor_share": round(labor_share, 2),
        "labor_mode": costs.labor_mode,
        "products": list(by_product.values()),
        "cash_count": existing_cash_count.to_dict() if existing_cash_count else None,
    })


@app.route("/api/stats/daily/close", methods=["POST"])
def close_daily_stats():
    """
    إغلاق اليوم: يحسب صافي مبيعات اليوم مطروحًا منه المصاريف المُدخَلة، ويضيف
    الصافي إلى رصيد الصندوق. إذا أُرسل actual_cash (المبلغ الحقيقي المعدود
    فعليًا في الصندوق بعد الإغلاق)، يقارنه النظام بالرصيد المتوقع الجديد
    ويحفظ الفرق كفائض/عجز نقدي في CashCount حتى يمكن تحليله لاحقًا.
    """
    data = request.get_json(force=True)
    target_date_str = data.get("date", date.today().isoformat())
    target_date = parse_date_arg(target_date_str)
    try:
        expenses = float(data.get("expenses", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "قيمة غير صحيحة"}), 400

    records = SaleRecord.query.filter(SaleRecord.sold_at == target_date).all()
    daily_total = sum(r.quantity_sold * r.sell_price_at_time for r in records)
    net = daily_total - expenses

    costs = get_or_create_costs()
    tx = BoxTransaction(amount=net, note=f"إغلاق يوم {target_date.isoformat()}")
    costs.box_balance += net
    db.session.add(tx)
    db.session.flush()

    cash_count = None
    actual_cash_raw = data.get("actual_cash")
    if actual_cash_raw not in (None, ""):
        try:
            actual_cash = float(actual_cash_raw)
        except (TypeError, ValueError):
            db.session.rollback()
            return jsonify({"error": "قيمة المبلغ الحقيقي غير صحيحة"}), 400

        expected_cash = costs.box_balance
        diff = actual_cash - expected_cash

        cash_count = CashCount.query.filter_by(count_date=target_date).first()
        if not cash_count:
            cash_count = CashCount(count_date=target_date)
            db.session.add(cash_count)
        cash_count.expected_cash = expected_cash
        cash_count.actual_cash = actual_cash
        cash_count.diff = diff
        cash_count.daily_total = daily_total
        cash_count.daily_expenses = expenses
        cash_count.note = (data.get("cash_note") or "").strip() or None

    db.session.commit()

    return jsonify({
        "net": round(net, 2),
        "costs": costs.to_dict(),
        "cash_count": cash_count.to_dict() if cash_count else None,
    })


@app.route("/api/stats/cash-history", methods=["GET"])
def cash_history():
    try:
        limit = int(request.args.get("limit", 60))
    except (TypeError, ValueError):
        limit = 60
    limit = max(1, min(limit, 365))
    counts = CashCount.query.order_by(CashCount.count_date.desc()).limit(limit).all()
    return jsonify([c.to_dict() for c in counts])


# ---------------------------------------------------------------------------
# API: الجرد
# ---------------------------------------------------------------------------

@app.route("/api/stocktake/open", methods=["POST"])
def open_stocktake():
    data = request.get_json(force=True)
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"error": "product_id مطلوب"}), 400
    product = Product.query.get_or_404(int(product_id))

    try:
        start_quantity = int(data.get("start_quantity", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "كمية بداية غير صحيحة"}), 400
    if start_quantity < 0:
        return jsonify({"error": "الكمية يجب ألا تكون سالبة"}), 400

    existing_open = StocktakeSession.query.filter_by(product_id=product.id, is_open=True).first()
    if existing_open:
        return jsonify({"error": "يوجد جرد مفتوح بالفعل لهذا المنتج"}), 400

    session = StocktakeSession(
        product_id=product.id,
        start_quantity=start_quantity,
        note=(data.get("note") or "").strip() or None,
        is_open=True,
    )
    db.session.add(session)
    db.session.commit()
    return jsonify(session.to_dict()), 201


@app.route("/api/stocktake/<int:session_id>/close", methods=["POST"])
def close_stocktake(session_id):
    session = StocktakeSession.query.get_or_404(session_id)
    if not session.is_open:
        return jsonify({"error": "هذا الجرد مغلق بالفعل"}), 400

    data = request.get_json(force=True)
    try:
        end_quantity = int(data.get("end_quantity", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "كمية نهاية غير صحيحة"}), 400
    if end_quantity < 0:
        return jsonify({"error": "الكمية يجب ألا تكون سالبة"}), 400

    product = session.product
    sold = session.start_quantity - end_quantity

    if sold > 0:
        sold = min(sold, product.quantity) if product.quantity else sold
        record = SaleRecord(
            product_id=product.id,
            quantity_sold=sold,
            sell_price_at_time=product.sell_price,
            buy_price_at_time=product.buy_price,
            source="stocktake",
        )
        db.session.add(record)
        db.session.flush()
        session.sale_record_id = record.id

    product.quantity = end_quantity

    session.end_quantity = end_quantity
    session.sold_quantity = max(sold, 0)
    session.is_open = False
    session.closed_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"session": session.to_dict(), "product": product.to_dict()})


@app.route("/api/stocktake/<int:session_id>", methods=["DELETE"])
def cancel_stocktake(session_id):
    session = StocktakeSession.query.get_or_404(session_id)
    if not session.is_open:
        return jsonify({"error": "لا يمكن إلغاء جرد مغلق بالفعل"}), 400
    db.session.delete(session)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/stocktake/open-sessions", methods=["GET"])
def list_open_stocktakes():
    sessions = StocktakeSession.query.filter_by(is_open=True).order_by(StocktakeSession.opened_at.desc()).all()
    return jsonify([s.to_dict() for s in sessions])


@app.route("/api/stocktake/history", methods=["GET"])
def stocktake_history():
    sessions = (
        StocktakeSession.query.filter_by(is_open=False)
        .order_by(StocktakeSession.closed_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([s.to_dict() for s in sessions])


# ---------------------------------------------------------------------------
# API: الجرد الجماعي (شاشة واحدة لكل المنتجات، على غرار الفاتورة)
# ---------------------------------------------------------------------------

@app.route("/api/stocktake/bulk", methods=["POST"])
def bulk_stocktake():
    """
    جرد جماعي بشاشة واحدة: تُرسَل قائمة بكل منتج تغيّرت كميته الفعلية عن
    الكمية المسجَّلة حاليًا في قاعدة البيانات (وهي نفسها القيمة المرجعية
    التي تحدَّثت من آخر فاتورة أو تعديل يدوي). لكل منتج نحسب الفرق
    (الكمية المسجَّلة - الكمية المعدودة الآن) كمبيع بتاريخ اليوم (أو
    تاريخ مُحدَّد)، نحدّث كمية المنتج فورًا، ونُرجع "فاتورة مبيع" بكل
    البنود المتأثرة ليتم عرضها للمستخدم وحفظها في السجل والتحليلات
    (عبر جدول SaleRecord نفسه بمصدر 'stocktake').

    لا حاجة لفتح/إغلاق جلسة منفصلة لكل منتج: القيمة "القديمة" تُقرأ مباشرة
    من Product.quantity وقت الحفظ، فتبقى موثوقة حتى لو مرّت فواتير أو
    تعديلات يدوية بين عمليات الجرد.
    """
    data = request.get_json(force=True)
    raw_items = data.get("items") or []
    stocktake_date_raw = data.get("date") or date.today().isoformat()
    stocktake_date = parse_date_arg(stocktake_date_raw)

    if not raw_items:
        return jsonify({"error": "لم يتم إدخال أي منتج للجرد"}), 400

    # رقم دفعة جديد لهذه العملية بالذات: كل عمليات الحفظ (حتى لو نُفِّذت
    # لاحقًا في نفس اليوم) تحصل على رقم مختلف، فيمكن لاحقًا عرضها كأقسام
    # منفصلة (بفاصل) داخل نفس القائمة اليومية دون أن تختلط ببعضها.
    max_batch = db.session.query(db.func.max(SaleRecord.stocktake_batch_id)).scalar() or 0
    batch_id = max_batch + 1

    results = []
    for raw in raw_items:
        product_id = raw.get("product_id")
        if not product_id:
            continue
        try:
            product_id = int(product_id)
            counted_qty = int(raw.get("counted_quantity"))
        except (TypeError, ValueError):
            db.session.rollback()
            return jsonify({"error": "قيمة كمية غير صحيحة في أحد المنتجات"}), 400
        if counted_qty < 0:
            db.session.rollback()
            return jsonify({"error": "الكمية يجب ألا تكون سالبة"}), 400

        product = Product.query.get(product_id)
        if not product:
            continue

        previous_qty = product.quantity
        if counted_qty == previous_qty:
            continue  # لا فرق = لا داعي لأي تسجيل

        sold = previous_qty - counted_qty  # موجب = بيع، سالب = زيادة غير مفسَّرة (تُعدَّل الكمية فقط دون تسجيل بيع)

        # نأخذ لقطة من السعر الحالي وقت هذا الجرد بالذات — هي نفس القيمة
        # التي ستُخزَّن في السجل، فيبقى حساب الإيراد/الربح مطابقًا دائمًا
        # لما سيُعرض لاحقًا من history، بغض النظر عن أي تغيّر سعر لاحق.
        sell_price_snapshot = product.sell_price
        buy_price_snapshot = product.buy_price

        record = None
        if sold > 0:
            record = SaleRecord(
                product_id=product.id,
                quantity_sold=sold,
                sell_price_at_time=sell_price_snapshot,
                buy_price_at_time=buy_price_snapshot,
                sold_at=stocktake_date,
                source="stocktake",
                stocktake_batch_id=batch_id,
            )
            db.session.add(record)
            db.session.flush()

        product.quantity = counted_qty

        revenue = round(max(sold, 0) * sell_price_snapshot, 2)
        profit = round(max(sold, 0) * (sell_price_snapshot - buy_price_snapshot), 2)

        results.append({
            "product_id": product.id,
            "product_name": product.name,
            "previous_quantity": previous_qty,
            "counted_quantity": counted_qty,
            "sold_quantity": max(sold, 0),
            "adjustment": min(sold, 0) * -1,  # قيمة موجبة إن كانت الكمية المعدودة أكبر من المسجّلة (تصحيح زيادة)
            "sell_price": sell_price_snapshot,
            "buy_price": buy_price_snapshot,
            "revenue": revenue,
            "profit": profit,
            "sale_record_id": record.id if record else None,
        })

    db.session.commit()

    total_revenue = round(sum(r["revenue"] for r in results), 2)
    total_profit = round(sum(r["profit"] for r in results), 2)
    total_sold_qty = sum(r["sold_quantity"] for r in results)

    return jsonify({
        "date": stocktake_date.isoformat(),
        "batch_id": batch_id,
        "items": results,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_sold_quantity": total_sold_qty,
    })


@app.route("/api/stocktake/day", methods=["GET"])
def stocktake_day():
    """
    كل عمليات الجرد المسجَّلة في تاريخ معيّن (اليوم افتراضيًا)، مجمَّعة في
    "دفعات" (batches) بترتيب تصاعدي زمني — كل دفعة تمثّل عملية حفظ جرد واحدة
    (قد تحتوي منتجًا واحدًا أو أكثر). تُستخدم لعرض كامل جرد اليوم كقائمة
    واحدة متصلة أشبه بفاتورة، مع فاصل مرئي بين كل دفعة وأخرى، بالإضافة إلى
    مجموع كلي (إيراد + ربح) لكامل اليوم بكل دفعاته مجتمعة.
    """
    target_date_str = request.args.get("date", date.today().isoformat())
    target_date = parse_date_arg(target_date_str)

    records = (
        SaleRecord.query.filter(
            SaleRecord.sold_at == target_date,
            SaleRecord.source == "stocktake",
        )
        .order_by(SaleRecord.stocktake_batch_id.asc().nullsfirst(), SaleRecord.id.asc())
        .all()
    )

    batches_map = OrderedDict()
    for r in records:
        key = r.stocktake_batch_id if r.stocktake_batch_id is not None else f"legacy-{r.id}"
        if key not in batches_map:
            batches_map[key] = {
                "batch_id": r.stocktake_batch_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "items": [],
            }
        batches_map[key]["items"].append({
            "product_id": r.product_id,
            "product_name": r.product.name if r.product else "منتج محذوف",
            "quantity_sold": r.quantity_sold,
            "sell_price": r.sell_price_at_time,
            "buy_price": r.buy_price_at_time,
            "revenue": round(r.quantity_sold * r.sell_price_at_time, 2),
            "profit": round(r.quantity_sold * (r.sell_price_at_time - r.buy_price_at_time), 2),
        })

    batches = []
    for b in batches_map.values():
        b["total_revenue"] = round(sum(it["revenue"] for it in b["items"]), 2)
        b["total_profit"] = round(sum(it["profit"] for it in b["items"]), 2)
        b["total_quantity"] = sum(it["quantity_sold"] for it in b["items"])
        batches.append(b)

    return jsonify({
        "date": target_date.isoformat(),
        "batches": batches,
        "total_revenue": round(sum(b["total_revenue"] for b in batches), 2),
        "total_profit": round(sum(b["total_profit"] for b in batches), 2),
        "total_quantity": sum(b["total_quantity"] for b in batches),
    })


# ---------------------------------------------------------------------------
# API: التحليلات — سلاسل زمنية (يومي/أسبوعي/شهري/سنوي) + الأكثر مبيعًا
# ---------------------------------------------------------------------------

def _period_bounds(period, target_date):
    if period == "daily":
        return target_date, target_date
    if period == "weekly":
        start = target_date - timedelta(days=target_date.weekday())
        return start, start + timedelta(days=6)
    if period == "monthly":
        start = target_date.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        return start, end
    if period == "yearly":
        start = target_date.replace(month=1, day=1)
        end = target_date.replace(month=12, day=31)
        return start, end
    raise ValueError("period غير مدعومة")


def _period_label(period, bucket_date):
    if period == "daily":
        return bucket_date.isoformat()
    if period == "weekly":
        return f"أسبوع {bucket_date.isoformat()}"
    if period == "monthly":
        return bucket_date.strftime("%Y-%m")
    if period == "yearly":
        return bucket_date.strftime("%Y")
    return bucket_date.isoformat()


def _bucket_key(period, sold_at):
    start, _ = _period_bounds(period, sold_at)
    return start


@app.route("/api/analytics/timeseries", methods=["GET"])
def analytics_timeseries():
    period = request.args.get("period", "daily")
    if period not in ("daily", "weekly", "monthly", "yearly"):
        return jsonify({"error": "period يجب أن تكون daily أو weekly أو monthly أو yearly"}), 400

    try:
        points_count = int(request.args.get("points", 14))
    except (TypeError, ValueError):
        points_count = 14
    points_count = max(1, min(points_count, 90))

    today = date.today()

    bucket_starts = []
    cursor = today
    for _ in range(points_count):
        start, _ = _period_bounds(period, cursor)
        bucket_starts.append(start)
        if period in ("daily", "weekly", "monthly"):
            cursor = start - timedelta(days=1)
        else:
            cursor = start.replace(year=start.year - 1)
    bucket_starts = sorted(set(bucket_starts))

    earliest_start = bucket_starts[0]
    records = SaleRecord.query.filter(SaleRecord.sold_at >= earliest_start).all()

    buckets = OrderedDict()
    for start in bucket_starts:
        buckets[start] = {"profit": 0.0, "revenue": 0.0, "cost": 0.0, "quantity": 0}

    for r in records:
        key = _bucket_key(period, r.sold_at)
        if key not in buckets:
            continue
        b = buckets[key]
        b["quantity"] += r.quantity_sold
        b["revenue"] += r.quantity_sold * r.sell_price_at_time
        b["cost"] += r.quantity_sold * r.buy_price_at_time
        b["profit"] += r.quantity_sold * (r.sell_price_at_time - r.buy_price_at_time)

    series = []
    for start, vals in buckets.items():
        series.append({
            "date": start.isoformat(),
            "label": _period_label(period, start),
            "profit": round(vals["profit"], 2),
            "revenue": round(vals["revenue"], 2),
            "cost": round(vals["cost"], 2),
            "quantity": vals["quantity"],
        })

    return jsonify({
        "period": period,
        "points": series,
        "total_profit": round(sum(p["profit"] for p in series), 2),
        "total_revenue": round(sum(p["revenue"] for p in series), 2),
        "total_cost": round(sum(p["cost"] for p in series), 2),
        "total_quantity": sum(p["quantity"] for p in series),
    })


@app.route("/api/analytics/top-products", methods=["GET"])
def analytics_top_products():
    period = request.args.get("period", "all")
    sort_by = request.args.get("sort_by", "quantity")
    try:
        limit = int(request.args.get("limit", 10))
    except (TypeError, ValueError):
        limit = 10
    limit = max(1, min(limit, 100))

    query = SaleRecord.query
    if period != "all":
        if period not in ("daily", "weekly", "monthly", "yearly"):
            return jsonify({"error": "period غير صحيحة"}), 400
        start, end = _period_bounds(period, date.today())
        query = query.filter(SaleRecord.sold_at >= start, SaleRecord.sold_at <= end)

    records = query.all()

    agg = {}
    for r in records:
        pid = r.product_id
        if pid not in agg:
            agg[pid] = {
                "product_id": pid,
                "product_name": r.product.name if r.product else "منتج محذوف",
                "quantity_sold": 0,
                "revenue": 0.0,
                "profit": 0.0,
                "max_sale_qty": 0,
                "min_sale_qty": None,
                "transactions": 0,
            }
        entry = agg[pid]
        entry["quantity_sold"] += r.quantity_sold
        entry["revenue"] += r.quantity_sold * r.sell_price_at_time
        entry["profit"] += r.quantity_sold * (r.sell_price_at_time - r.buy_price_at_time)
        entry["transactions"] += 1
        entry["max_sale_qty"] = max(entry["max_sale_qty"], r.quantity_sold)
        entry["min_sale_qty"] = r.quantity_sold if entry["min_sale_qty"] is None else min(entry["min_sale_qty"], r.quantity_sold)

    items = list(agg.values())
    for it in items:
        it["revenue"] = round(it["revenue"], 2)
        it["profit"] = round(it["profit"], 2)
        if it["min_sale_qty"] is None:
            it["min_sale_qty"] = 0

    sort_key = {"profit": "profit", "revenue": "revenue"}.get(sort_by, "quantity_sold")
    items.sort(key=lambda x: x[sort_key], reverse=True)

    return jsonify({
        "period": period,
        "sort_by": sort_key,
        "items": items[:limit],
    })


@app.route("/api/analytics/product-timeseries", methods=["GET"])
def analytics_product_timeseries():
    product_id = request.args.get("product_id")
    if not product_id:
        return jsonify({"error": "product_id مطلوب"}), 400
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        return jsonify({"error": "product_id غير صحيح"}), 400

    try:
        limit = int(request.args.get("limit", 30))
    except (TypeError, ValueError):
        limit = 30
    limit = max(1, min(limit, 200))

    product = Product.query.get_or_404(product_id)
    records = (
        SaleRecord.query.filter_by(product_id=product_id)
        .order_by(SaleRecord.sold_at.asc(), SaleRecord.id.asc())
        .limit(limit)
        .all()
    )

    points = [{
        "date": r.sold_at.isoformat() if r.sold_at else None,
        "quantity": r.quantity_sold,
        "profit": round(r.quantity_sold * (r.sell_price_at_time - r.buy_price_at_time), 2),
        "revenue": round(r.quantity_sold * r.sell_price_at_time, 2),
        "source": r.source,
    } for r in records]

    qtys = [p["quantity"] for p in points]

    return jsonify({
        "product_id": product_id,
        "product_name": product.name,
        "points": points,
        "max_quantity": max(qtys) if qtys else 0,
        "min_quantity": min(qtys) if qtys else 0,
        "total_quantity": sum(qtys),
        "total_profit": round(sum(p["profit"] for p in points), 2),
    })


# ---------------------------------------------------------------------------
# صحّة الخدمة + تقديم الواجهة الثابتة
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    db_kind = "postgresql (supabase)" if IS_POSTGRES else "sqlite"
    if DB_INIT_ERROR:
        return jsonify({
            "status": "degraded",
            "time": datetime.utcnow().isoformat(),
            "database": db_kind,
            "error": "لا يوجد اتصال بقاعدة البيانات. تحقق من DATABASE_URL (يُفضّل رابط Connection Pooling بالمنفذ 6543 لتفادي مشاكل IPv6).",
        }), 503
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat(), "database": db_kind})


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/manifest.json")
def manifest():
    return send_from_directory(app.static_folder, "manifest.json")


@app.route("/sw.js")
def service_worker():
    return send_from_directory(app.static_folder, "sw.js")


def _run_light_migrations():
    """
    إضافة الأعمدة/الجداول الجديدة لقاعدة بيانات موجودة مسبقًا دون فقدان
    البيانات، لأن create_all لا يعدّل جداولًا موجودة بالفعل. تُنفَّذ بأمان
    (IF NOT EXISTS) وتُتجاهل أي أخطاء بلطف. تعمل فقط على PostgreSQL؛ SQLite
    يعتمد على create_all فقط عند إنشاء قاعدة جديدة.
    """
    if not IS_POSTGRES:
        return
    from sqlalchemy import text
    statements = [
        "ALTER TABLE costs ADD COLUMN IF NOT EXISTS labor_mode VARCHAR(20) DEFAULT 'percent'",
        "ALTER TABLE sale_records ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'manual'",
        "ALTER TABLE sale_records ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
        "ALTER TABLE sale_records ADD COLUMN IF NOT EXISTS stocktake_batch_id INTEGER",
        "ALTER TABLE box_transactions ALTER COLUMN note DROP NOT NULL",
        # جدول cash_counts قد يكون أُنشئ سابقًا بمخطط ناقص (مثلاً من محاولة نشر
        # سابقة توقفت جزئيًا)، لذلك نضيف كل عمود صراحة IF NOT EXISTS بدل
        # الاعتماد فقط على create_all الذي لا يُكمل أعمدة جدول موجود مسبقًا.
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS count_date DATE",
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS expected_cash DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS actual_cash DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS diff DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS daily_total DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS daily_expenses DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS note VARCHAR(300)",
        "ALTER TABLE cash_counts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
        # نفس الاحتياط لجداول الفواتير وسجل تغيّر الأسعار حديثة الإضافة.
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS invoice_date DATE",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS note VARCHAR(300)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
        # جدول invoice_items قد يكون أُنشئ في نسخة سابقة من المشروع بمخطط
        # ناقص (قبل إضافة أعمدة الأسعار)، ولأن create_all لا يُكمل أعمدة
        # جدول موجود مسبقًا، نضيف كل عمود صراحة IF NOT EXISTS. هذا هو سبب
        # خطأ "column buy_price of relation invoice_items does not exist"
        # الذي كان يحدث عند حفظ فاتورة على قاعدة بيانات قديمة على Render.
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS product_name_snapshot VARCHAR(200)",
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS quantity INTEGER",
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS buy_price DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS sell_price DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS prev_buy_price DOUBLE PRECISION",
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS prev_sell_price DOUBLE PRECISION",
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS prev_quantity INTEGER",
        "UPDATE invoice_items SET buy_price = 0 WHERE buy_price IS NULL",
        "UPDATE invoice_items SET sell_price = 0 WHERE sell_price IS NULL",
        # جدول invoice_items قد يحمل أيضًا أعمدة قديمة جدًا من نسخة سابقة من
        # المشروع (buy_price_at_time / sell_price_at_time) بقيد NOT NULL بلا
        # قيمة افتراضية، وهي السبب في خطأ "null value in column
        # buy_price_at_time violates not-null constraint" لأن الكود الحالي
        # لا يكتب فيها إطلاقًا. نُسقط قيد NOT NULL عنها إن وُجدت لتفادي فشل
        # الإدراج، دون حذف العمود نفسه حفاظًا على أي بيانات قديمة بداخله.
        "ALTER TABLE invoice_items ALTER COLUMN buy_price_at_time DROP NOT NULL",
        "ALTER TABLE invoice_items ALTER COLUMN sell_price_at_time DROP NOT NULL",
        "ALTER TABLE price_change_logs ADD COLUMN IF NOT EXISTS invoice_id INTEGER",
        "ALTER TABLE price_change_logs ADD COLUMN IF NOT EXISTS price_field VARCHAR(10)",
        "ALTER TABLE price_change_logs ADD COLUMN IF NOT EXISTS old_price DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE price_change_logs ADD COLUMN IF NOT EXISTS new_price DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE price_change_logs ADD COLUMN IF NOT EXISTS quantity_affected INTEGER DEFAULT 0",
        "ALTER TABLE price_change_logs ADD COLUMN IF NOT EXISTS impact DOUBLE PRECISION DEFAULT 0",
        "ALTER TABLE price_change_logs ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
        # جدول الأصناف (categories) وربط المنتجات به — قد لا يكون موجودًا على
        # قواعد بيانات أُنشئت قبل إضافة ميزة الأصناف، لذلك ننشئه صراحة هنا
        # أيضًا كاحتياط بجانب create_all، ونضيف عمود category_id لجدول
        # المنتجات إن لم يكن موجودًا.
        """
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP
        )
        """,
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES categories(id)",
        # تعبئة أي صفوف قديمة محتملة بقيم افتراضية آمنة بدل NULL، حتى تتوافق
        # مع NOT NULL في النموذج عند القراءة اللاحقة.
        "UPDATE cash_counts SET expected_cash = 0 WHERE expected_cash IS NULL",
        "UPDATE cash_counts SET actual_cash = 0 WHERE actual_cash IS NULL",
        "UPDATE cash_counts SET diff = 0 WHERE diff IS NULL",
        "UPDATE cash_counts SET daily_total = 0 WHERE daily_total IS NULL",
        "UPDATE cash_counts SET daily_expenses = 0 WHERE daily_expenses IS NULL",
        "UPDATE cash_counts SET count_date = CURRENT_DATE WHERE count_date IS NULL",
    ]
    with db.engine.connect() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()


DB_INIT_ERROR = None
with app.app_context():
    try:
        db.create_all()
        _run_light_migrations()
    except Exception as exc:
        # لا نسمح لخطأ اتصال بقاعدة البيانات (شبكة، رابط خاطئ، IPv6 غير
        # مدعوم على Render مع اتصال Supabase المباشر...) بإسقاط العملية
        # بالكامل عند الإقلاع. بدلاً من ذلك نُبقي التطبيق يعمل بحالة
        # "متدهورة" (degraded) ويُظهر السبب عبر /api/health، بحيث تظهر
        # شارة التحذير الحمراء بالواجهة بدل توقف الخدمة بالكامل (نفس مبدأ
        # التعامل مع Supabase/الشبكة في المشروع الأكبر: تعطّل السحابة لا
        # يجب أن يوقف كل شيء).
        DB_INIT_ERROR = str(exc)
        app.logger.error("DB init failed: %s", exc)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
