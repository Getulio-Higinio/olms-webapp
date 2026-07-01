from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from datetime import datetime
from olms_app.db.database import Base

class StockOnHand(Base):
    __tablename__ = "stock_on_hand"

    id = Column(Integer, primary_key=True)
    warehouse_code = Column(String, default="MZALPHA1")
    supplier = Column(String)
    invoice_no = Column(String)
    po_number = Column(String)
    eta_pemba_store = Column(Date)

    item_code = Column(String, index=True)
    barcode = Column(String)
    item_name = Column(String)
    item_category = Column(String)
    project_code = Column(String)

    po_qty = Column(Float)
    po_uom = Column(String)
    po_unit_price = Column(Float)

    invoice_qty = Column(Float)
    invoice_uom = Column(String)
    invoice_unit_price = Column(Float)

    conversion_factor = Column(Float)
    physical_stock = Column(Float, default=0)
    stock_uom = Column(String)

    offshore_selection_qty = Column(Float, default=0)
    dnv_container = Column(String)
    balance_after_selection = Column(Float, default=0)

    unit_weight = Column(Float)
    total_weight = Column(Float)

    production_date = Column(Date)
    bbd = Column(Date)
    coo = Column(String)

    shelf_life_percent = Column(Float)
    days_to_expiry = Column(Integer)
    expiry_status = Column(String)

    variance_status = Column(String)
    variance_comments = Column(Text)
    root_cause = Column(Text)
    responsible = Column(String)
    closure_date = Column(Date)
    action_required = Column(Text)
    general_comments = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class POImportPreview(Base):
    __tablename__ = "po_import_preview"

    id = Column(Integer, primary_key=True)
    supplier = Column(String)
    po_number = Column(String)
    item_code = Column(String)
    barcode = Column(String)
    item_name = Column(String)
    po_qty = Column(Float)
    po_uom = Column(String)
    po_unit_price = Column(Float)
    status = Column(String, default="APPROVED")
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class InvoiceImportPreview(Base):
    __tablename__ = "invoice_import_preview"

    id = Column(Integer, primary_key=True)
    supplier = Column(String)
    invoice_no = Column(String)
    po_number = Column(String)
    item_code = Column(String)
    barcode = Column(String)
    invoice_qty = Column(Float)
    invoice_uom = Column(String)
    invoice_unit_price = Column(Float)
    conversion_factor = Column(Float)
    stock_uom = Column(String)
    production_date = Column(Date)
    bbd = Column(Date)
    coo = Column(String)
    status = Column(String, default="APPROVED")
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Loadout(Base):
    __tablename__ = "loadouts"

    id = Column(Integer, primary_key=True)
    loadout_no = Column(String)
    vessel = Column(String)
    etd = Column(Date)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    user = Column(String, default="system")
    action = Column(String)
    entity = Column(String)
    entity_id = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
