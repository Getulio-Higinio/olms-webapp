import pandas as pd
from olms_app.config import DEFAULT_WAREHOUSE
from olms_app.db.models import StockOnHand, POImportPreview, InvoiceImportPreview
from olms_app.services.utils import safe_float, safe_date, expiry_status
from olms_app.services.audit import log_action

PO_COLUMNS = [
    "Supplier", "PO Number", "Item Code", "Barcode", "Item Name",
    "PO Qty", "PO UOM", "PO Unit Price", "Status", "Comments"
]

INVOICE_COLUMNS = [
    "Supplier", "Invoice No", "PO Number", "Item Code", "Barcode",
    "Invoice Qty", "Invoice UOM", "Invoice Unit Price",
    "Conversion Factor", "Stock UOM", "Production Date", "BBD", "COO",
    "Status", "Comments"
]

def read_excel(file, required_columns):
    df = pd.read_excel(file)
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return df

def load_po_preview(session, df):
    count = 0
    session.query(POImportPreview).delete()
    for _, row in df.iterrows():
        status = str(row.get("Status", "APPROVED") or "APPROVED").upper()
        session.add(POImportPreview(
            supplier=str(row.get("Supplier", "")).strip(),
            po_number=str(row.get("PO Number", "")).strip(),
            item_code=str(row.get("Item Code", "")).strip(),
            barcode=str(row.get("Barcode", "")).strip(),
            item_name=str(row.get("Item Name", "")).strip(),
            po_qty=safe_float(row.get("PO Qty")),
            po_uom=str(row.get("PO UOM", "")).strip(),
            po_unit_price=safe_float(row.get("PO Unit Price")),
            status=status,
            comments=str(row.get("Comments", "") or "")
        ))
        count += 1
    session.commit()
    log_action(session, "LOAD_PO_PREVIEW", "POImportPreview", details=f"{count} rows loaded")
    return count

def find_target_stock_row(session, item_code, barcode):
    rows = session.query(StockOnHand).filter(StockOnHand.item_code == item_code).order_by(StockOnHand.id).all()
    for row in rows:
        if barcode and row.barcode and str(row.barcode) != str(barcode):
            continue
        if not row.physical_stock or row.physical_stock == 0:
            return row
    return None

def confirm_po_import(session):
    approved = session.query(POImportPreview).filter(POImportPreview.status == "APPROVED").all()
    imported = 0
    for p in approved:
        target = find_target_stock_row(session, p.item_code, p.barcode)
        if target is None:
            target = StockOnHand()
            session.add(target)

        target.warehouse_code = DEFAULT_WAREHOUSE
        target.supplier = p.supplier
        target.invoice_no = None
        target.po_number = p.po_number
        target.item_code = p.item_code
        target.barcode = p.barcode
        target.item_name = p.item_name
        target.po_qty = p.po_qty
        target.po_uom = p.po_uom
        target.po_unit_price = p.po_unit_price
        target.physical_stock = 0
        target.offshore_selection_qty = 0
        target.balance_after_selection = 0
        imported += 1

    session.commit()
    log_action(session, "CONFIRM_PO_IMPORT", "StockOnHand", details=f"{imported} rows imported")
    return imported

def load_invoice_preview(session, df):
    count = 0
    session.query(InvoiceImportPreview).delete()
    for _, row in df.iterrows():
        status = str(row.get("Status", "APPROVED") or "APPROVED").upper()
        session.add(InvoiceImportPreview(
            supplier=str(row.get("Supplier", "")).strip(),
            invoice_no=str(row.get("Invoice No", "")).strip(),
            po_number=str(row.get("PO Number", "")).strip(),
            item_code=str(row.get("Item Code", "")).strip(),
            barcode=str(row.get("Barcode", "")).strip(),
            invoice_qty=safe_float(row.get("Invoice Qty")),
            invoice_uom=str(row.get("Invoice UOM", "")).strip(),
            invoice_unit_price=safe_float(row.get("Invoice Unit Price")),
            conversion_factor=safe_float(row.get("Conversion Factor")),
            stock_uom=str(row.get("Stock UOM", "")).strip(),
            production_date=safe_date(row.get("Production Date")),
            bbd=safe_date(row.get("BBD")),
            coo=str(row.get("COO", "")).strip(),
            status=status,
            comments=str(row.get("Comments", "") or "")
        ))
        count += 1
    session.commit()
    log_action(session, "LOAD_INVOICE_PREVIEW", "InvoiceImportPreview", details=f"{count} rows loaded")
    return count

def confirm_invoice_import(session):
    approved = session.query(InvoiceImportPreview).filter(InvoiceImportPreview.status == "APPROVED").all()
    updated = 0
    for inv in approved:
        target = find_target_stock_row(session, inv.item_code, inv.barcode)
        if target is None:
            target = StockOnHand()
            session.add(target)

        target.supplier = inv.supplier or target.supplier
        target.invoice_no = inv.invoice_no
        target.po_number = inv.po_number or target.po_number
        target.item_code = inv.item_code
        target.barcode = inv.barcode
        target.invoice_qty = inv.invoice_qty
        target.invoice_uom = inv.invoice_uom
        target.invoice_unit_price = inv.invoice_unit_price
        target.conversion_factor = inv.conversion_factor or 1
        target.physical_stock = (inv.invoice_qty or 0) * (target.conversion_factor or 1)
        target.stock_uom = inv.stock_uom
        target.production_date = inv.production_date
        target.bbd = inv.bbd
        target.coo = inv.coo
        target.days_to_expiry = (inv.bbd - pd.Timestamp.today().date()).days if inv.bbd else None
        target.expiry_status = expiry_status(inv.bbd)
        target.balance_after_selection = (target.physical_stock or 0) - (target.offshore_selection_qty or 0)
        updated += 1

    session.commit()
    log_action(session, "CONFIRM_INVOICE_IMPORT", "StockOnHand", details=f"{updated} rows updated")
    return updated
