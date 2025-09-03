from database import SessionLocal
import models, random, datetime
from sqlalchemy.orm import Session

def run_seed():
    db: Session = SessionLocal()
    # quick check
    if db.query(models.Vendor).count() > 0:
        print("Already seeded")
        return
    today = datetime.date.today()
    vendors = [models.Vendor(name=f"Vendor {i}", email=f"v{i}@example.com", phone=f"+100{i}", address="Addr {i}") for i in range(1,11)]
    customers = [models.Customer(name=f"Customer {i}", email=f"c{i}@example.com", phone=f"+200{i}", address="Addr {i}") for i in range(1,11)]
    products = [models.Product(sku=f"SKU{i:03}", name=f"Product {i}", description="Sample", price=50+i, cost=30+i, uom="EA") for i in range(1,21)]
    warehouses = [models.Warehouse(name=f"WH {i}", location=f"City {i}") for i in range(1,4)]
    db.add_all(vendors+customers+products+warehouses); db.commit()

    # Inventory sample
    for p in db.scalars(models.Product.__table__.select()).all():
        for w in db.scalars(models.Warehouse.__table__.select()).all():
            db.add(models.Inventory(product_id=p.id, warehouse_id=w.id, quantity=random.randint(10,200)))
    db.commit()

    # Purchase Orders and lines
    for i in range(1,11):
        v = random.choice(vendors)
        po = models.PurchaseOrder(vendor_id=v.id, order_date=today - datetime.timedelta(days=random.randint(1,90)), status="Open", total_amount=random.randint(500,5000))
        db.add(po); db.commit()
        # create lines
        for _ in range(1,4):
            prod = random.choice(products)
            db.add(models.PurchaseOrderLine(po_id=po.id, product_id=prod.id, quantity=random.randint(1,20), unit_cost=float(prod.cost)))
        db.commit()

    # Sales Orders and lines
    for i in range(1,11):
        c = random.choice(customers)
        so = models.SalesOrder(customer_id=c.id, order_date=today - datetime.timedelta(days=random.randint(1,90)), status="Open", total_amount=random.randint(500,7000))
        db.add(so); db.commit()
        for _ in range(1,4):
            prod = random.choice(products)
            db.add(models.SalesOrderLine(so_id=so.id, product_id=prod.id, quantity=random.randint(1,10), unit_price=float(prod.price)))
        db.commit()

    # GL Accounts
    gls = [models.GLAccount(code="1000", name="Cash", type="Asset"),
           models.GLAccount(code="1100", name="AR", type="Asset"),
           models.GLAccount(code="2000", name="AP", type="Liability"),
           models.GLAccount(code="4000", name="Sales Revenue", type="Revenue"),
           models.GLAccount(code="5000", name="COGS", type="Expense")]
    db.add_all(gls); db.commit()

    # Journal entries and lines (simulate sales and cogs)
    for i in range(1,31):
        je = models.JournalEntry(date=today - datetime.timedelta(days=random.randint(1,60)), description="Sale posting", posted=True)
        db.add(je); db.commit()
        # revenue line
        db.add(models.JournalEntryLine(journal_id=je.id, account_code="4000", description="Sale", debit=0, credit=random.randint(100,1000)))
        # cogs line
        db.add(models.JournalEntryLine(journal_id=je.id, account_code="5000", description="COGS", debit=random.randint(50,700), credit=0))
        db.commit()

    # AR and AP
    for i in range(1,21):
        cust = random.choice(customers)
        vend = random.choice(vendors)
        d = today - datetime.timedelta(days=random.randint(1,120))
        db.add(models.AccountsReceivable(customer_id=cust.id, invoice_number=f"AR{i:04}", invoice_date=d, due_date=d + datetime.timedelta(days=30), amount=random.randint(100,1500), status="Open"))
        db.add(models.AccountsPayable(vendor_id=vend.id, invoice_number=f"AP{i:04}", invoice_date=d, due_date=d + datetime.timedelta(days=30), amount=random.randint(100,1500), status="Open"))
    db.commit()

    # Forecasts sample
    for m in ["net_sales","net_profit"]:
        for i in range(0,6):
            period = (today - datetime.timedelta(days=i*30)).strftime("%Y-%m")
            db.add(models.Forecast(period=period, metric=m, value=random.randint(1000,10000)))
    db.commit()

    # Calendar events
    db.add(models.CalendarEvent(title="Monthly Close", start=datetime.datetime.combine(today, datetime.time(9,0)), end=datetime.datetime.combine(today, datetime.time(10,0)), type="reminder", description="Prepare close"))
    db.commit()
    print("Seed complete")

if __name__ == "__main__":
    run_seed()
