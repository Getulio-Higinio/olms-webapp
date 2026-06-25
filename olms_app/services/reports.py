import pandas as pd
from olms_app.db.models import StockOnHand

def stock_dataframe(session):
    rows = session.query(StockOnHand).all()
    return pd.DataFrame([{
        "ID": r.id,
        "Warehouse Code": r.warehouse_code,
        "Supplier": r.supplier,
        "Invoice No": r.invoice_no,
        "PO Number": r.po_number,
        "Item Code": r.item_code,
        "Barcode": r.barcode,
        "Item Name": r.item_name,
        "Item Category": r.item_category,
        "Project Code": r.project_code,
        "PO Qty": r.po_qty,
        "PO UOM": r.po_uom,
        "PO Unit Price": r.po_unit_price,
        "Invoice Qty": r.invoice_qty,
        "Invoice UOM": r.invoice_uom,
        "Invoice Unit Price": r.invoice_unit_price,
        "Conversion Factor": r.conversion_factor,
        "Physical Stock": r.physical_stock,
        "Stock UOM": r.stock_uom,
        "Offshore Selection Qty": r.offshore_selection_qty,
        "DNV Container": r.dnv_container,
        "Balance After Selection": r.balance_after_selection,
        "BBD": r.bbd,
        "COO": r.coo,
        "Expiry Status": r.expiry_status,
        "Variance Status": r.variance_status,
    } for r in rows])

def variance_dataframe(session):
    df = stock_dataframe(session)
    if df.empty:
        return df
    df["Qty Variance"] = df["Invoice Qty"].fillna(0) - df["PO Qty"].fillna(0)
    df["Price Variance"] = df["Invoice Unit Price"].fillna(0) - df["PO Unit Price"].fillna(0)
    df["Variance Value"] = df["Qty Variance"] * df["Invoice Unit Price"].fillna(0)
    df["Variance Status"] = df["Qty Variance"].apply(lambda x: "MATCH" if x == 0 else ("OVER INVOICED" if x > 0 else "UNDER INVOICED"))
    return df
