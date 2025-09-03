from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Numeric, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class EventType(enum.Enum):
    reminder = "reminder"
    due = "due"
    meeting = "meeting"

# Master Data
class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255))
    phone = Column(String(100))
    address = Column(Text)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255))
    phone = Column(String(100))
    address = Column(Text)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(14,2), default=0)
    cost = Column(Numeric(14,2), default=0)
    uom = Column(String(50), default="EA")

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))

# Supply Chain
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    order_date = Column(Date)
    status = Column(String(50))
    total_amount = Column(Numeric(14,2), default=0)
    vendor = relationship("Vendor", lazy="joined")

class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Numeric(14,2))
    unit_cost = Column(Numeric(14,2))

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_date = Column(Date)
    status = Column(String(50))
    total_amount = Column(Numeric(14,2), default=0)
    customer = relationship("Customer", lazy="joined")

class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"
    id = Column(Integer, primary_key=True, index=True)
    so_id = Column(Integer, ForeignKey("sales_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Numeric(14,2))
    unit_price = Column(Numeric(14,2))

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    quantity = Column(Numeric(14,2), default=0)

class PurchaseRequisition(Base):
    __tablename__ = "purchase_requisitions"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Numeric(14,2), default=0)
    status = Column(String(50))
    needed_by = Column(Date)

class SupplierContract(Base):
    __tablename__ = "supplier_contracts"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    terms = Column(Text)

# Finance
class GLAccount(Base):
    __tablename__ = "gl_accounts"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True)
    name = Column(String(255))
    type = Column(String(50))  # Asset/Liability/Equity/Revenue/Expense

class AccountsPayable(Base):
    __tablename__ = "accounts_payable"
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    invoice_number = Column(String(100))
    invoice_date = Column(Date)
    due_date = Column(Date)
    amount = Column(Numeric(14,2))
    status = Column(String(50))
    vendor = relationship("Vendor", lazy="joined")

class AccountsReceivable(Base):
    __tablename__ = "accounts_receivable"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    invoice_number = Column(String(100))
    invoice_date = Column(Date)
    due_date = Column(Date)
    amount = Column(Numeric(14,2))
    status = Column(String(50))
    customer = relationship("Customer", lazy="joined")

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    cost_center = Column(String(100))
    year = Column(Integer)
    amount = Column(Numeric(14,2))

class FixedAsset(Base):
    __tablename__ = "fixed_assets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    purchase_date = Column(Date)
    purchase_value = Column(Numeric(14,2))
    useful_life_years = Column(Integer)

class FXRate(Base):
    __tablename__ = "fx_rates"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(10))
    rate = Column(Numeric(14,6))
    date = Column(Date)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    description = Column(String(255))
    posted = Column(Boolean, default=False)

class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"
    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_code = Column(String(100))
    description = Column(String(255))
    debit = Column(Numeric(14,2), default=0)
    credit = Column(Numeric(14,2), default=0)
    cost_center = Column(String(100))

class CostCenter(Base):
    __tablename__ = "cost_centers"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True)
    name = Column(String(255))

class TaxLedger(Base):
    __tablename__ = "tax_ledger"
    id = Column(Integer, primary_key=True, index=True)
    tax_type = Column(String(100))
    reference = Column(String(100))
    date = Column(Date)
    amount = Column(Numeric(14,2))

class CashFlow(Base):
    __tablename__ = "cash_flow"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    category = Column(String(100))  # Operating/Investing/Financing
    description = Column(String(255))
    amount = Column(Numeric(14,2))

class Reconciliation(Base):
    __tablename__ = "reconciliation"
    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String(100))
    period = Column(String(20))
    status = Column(String(50))
    notes = Column(Text)

# Forecasts (for Actual vs Forecast)
class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(20))  # '2025-08'
    metric = Column(String(100))  # 'net_sales', 'net_profit', etc.
    value = Column(Numeric(14,2))
    notes = Column(Text)

# Calendar events for dashboard
class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    start = Column(DateTime)
    end = Column(DateTime)
    type = Column(String(50))
    description = Column(Text)
