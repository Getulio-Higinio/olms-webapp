import streamlit as st
import pandas as pd
import plotly.express as px
from olms_app.config import APP_NAME
from olms_app.db.init_db import init_db
from olms_app.db.database import get_session
from olms_app.db.models import POImportPreview, InvoiceImportPreview, StockOnHand, AuditLog
from olms_app.services.importers import (
    PO_COLUMNS, INVOICE_COLUMNS, read_excel, load_po_preview,
    confirm_po_import, load_invoice_preview, confirm_invoice_import
)
from olms_app.services.reports import stock_dataframe, variance_dataframe

init_db()
session = get_session()

st.set_page_config(page_title="OLMS Web App", layout="wide")
st.title(APP_NAME)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Stock On Hand",
        "PO Import Preview",
        "PO Import",
        "Invoice Import",
        "Offshore Selection",
        "PO Variance Report",
        "Loadout Summary",
        "Administration",
    ],
)

if menu == "Dashboard":
    st.header("Dashboard")
    df = stock_dataframe(session)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stock Lines", len(df))
    c2.metric("Physical Stock Total", round(df["Physical Stock"].fillna(0).sum(), 2) if not df.empty else 0)
    c3.metric("Open Expiry Alerts", int((df["Expiry Status"].isin(["CRITICAL", "EXPIRED"])).sum()) if not df.empty else 0)
    c4.metric("Open Variance Lines", int((variance_dataframe(session)["Variance Status"] != "MATCH").sum()) if not df.empty else 0)
    if not df.empty:
        chart_df = df.groupby("Item Category", dropna=False)["Physical Stock"].sum().reset_index()
        st.plotly_chart(px.bar(chart_df, x="Item Category", y="Physical Stock", title="Stock by Category"), use_container_width=True)
        st.dataframe(df, use_container_width=True)

elif menu == "Stock On Hand":
    st.header("Stock On Hand")
    df = stock_dataframe(session)
    st.dataframe(df, use_container_width=True)
    st.download_button("Download Stock On Hand CSV", df.to_csv(index=False), "stock_on_hand.csv")

elif menu == "PO Import Preview":
    st.header("PO Import Preview")
    rows = session.query(POImportPreview).all()
    df = pd.DataFrame([{
        "Supplier": r.supplier,
        "PO Number": r.po_number,
        "Item Code": r.item_code,
        "Barcode": r.barcode,
        "Item Name": r.item_name,
        "PO Qty": r.po_qty,
        "PO UOM": r.po_uom,
        "PO Unit Price": r.po_unit_price,
        "Status": r.status,
        "Comments": r.comments,
    } for r in rows])
    st.dataframe(df, use_container_width=True)
    col1, col2 = st.columns(2)
    if col1.button("CONFIRM PO IMPORT"):
        count = confirm_po_import(session)
        st.success(f"{count} PO line(s) imported to Stock On Hand.")
        st.rerun()
    if col2.button("CLEAR PREVIEW"):
        session.query(POImportPreview).delete()
        session.commit()
        st.success("PO preview cleared.")
        st.rerun()

elif menu == "PO Import":
    st.header("PO Import")
    st.write("Upload Excel file with these columns:")
    st.code(", ".join(PO_COLUMNS))
    sample = pd.DataFrame(columns=PO_COLUMNS)
    st.download_button("Download PO Import Template", sample.to_csv(index=False), "po_import_template.csv")
    file = st.file_uploader("Upload PO Excel", type=["xlsx", "xlsm", "xls"])
    if file and st.button("Load PO Preview"):
        try:
            df = read_excel(file, PO_COLUMNS)
            count = load_po_preview(session, df)
            st.success(f"{count} PO line(s) loaded into preview.")
        except Exception as e:
            st.error(str(e))

elif menu == "Invoice Import":
    st.header("Invoice Import")
    st.write("Upload Excel file with these columns:")
    st.code(", ".join(INVOICE_COLUMNS))
    sample = pd.DataFrame(columns=INVOICE_COLUMNS)
    st.download_button("Download Invoice Import Template", sample.to_csv(index=False), "invoice_import_template.csv")
    file = st.file_uploader("Upload Invoice Excel", type=["xlsx", "xlsm", "xls"])
    if file and st.button("Load Invoice Preview"):
        try:
            df = read_excel(file, INVOICE_COLUMNS)
            count = load_invoice_preview(session, df)
            st.success(f"{count} invoice line(s) loaded into preview.")
        except Exception as e:
            st.error(str(e))

    rows = session.query(InvoiceImportPreview).all()
    if rows:
        df = pd.DataFrame([{
            "Supplier": r.supplier, "Invoice No": r.invoice_no, "PO Number": r.po_number,
            "Item Code": r.item_code, "Invoice Qty": r.invoice_qty, "Invoice UOM": r.invoice_uom,
            "Conversion Factor": r.conversion_factor, "Stock UOM": r.stock_uom, "BBD": r.bbd,
            "Status": r.status
        } for r in rows])
        st.subheader("Invoice Preview")
        st.dataframe(df, use_container_width=True)
        if st.button("CONFIRM INVOICE IMPORT"):
            count = confirm_invoice_import(session)
            st.success(f"{count} invoice line(s) confirmed into Stock On Hand.")
            st.rerun()

elif menu == "Offshore Selection":
    st.header("Offshore Selection")
    df = stock_dataframe(session)
    if df.empty:
        st.info("No stock available.")
    else:
        st.dataframe(df[["ID", "Item Code", "Item Name", "Physical Stock", "Stock UOM", "Offshore Selection Qty", "Balance After Selection", "DNV Container"]], use_container_width=True)
        with st.form("selection_form"):
            item_id = st.number_input("Stock Line ID", min_value=1, step=1)
            qty = st.number_input("Offshore Selection Qty", min_value=0.0, step=1.0)
            container = st.text_input("DNV Container")
            submitted = st.form_submit_button("Update Selection")
            if submitted:
                row = session.query(StockOnHand).filter(StockOnHand.id == item_id).first()
                if row:
                    row.offshore_selection_qty = qty
                    row.dnv_container = container
                    row.balance_after_selection = (row.physical_stock or 0) - qty
                    session.commit()
                    st.success("Selection updated.")
                    st.rerun()
                else:
                    st.error("Stock line not found.")

elif menu == "PO Variance Report":
    st.header("PO Variance Report")
    df = variance_dataframe(session)
    st.dataframe(df, use_container_width=True)
    st.download_button("Download PO Variance CSV", df.to_csv(index=False), "po_variance_report.csv")

elif menu == "Loadout Summary":
    st.header("Loadout Summary")
    df = stock_dataframe(session)
    if df.empty:
        st.info("No data available.")
    else:
        selected = df[df["Offshore Selection Qty"].fillna(0) > 0]
        st.metric("Selected Lines", len(selected))
        st.metric("Total Selected Qty", round(selected["Offshore Selection Qty"].fillna(0).sum(), 2))
        st.dataframe(selected, use_container_width=True)
        if st.button("Close Loadout - Clear Zero Balances"):
            rows = session.query(StockOnHand).all()
            cleared = 0
            for r in rows:
                if (r.balance_after_selection or 0) == 0 and (r.physical_stock or 0) > 0:
                    r.supplier = None
                    r.invoice_no = None
                    r.po_number = None
                    r.eta_pemba_store = None
                    r.po_qty = None
                    r.po_uom = None
                    r.po_unit_price = None
                    r.invoice_qty = None
                    r.invoice_uom = None
                    r.invoice_unit_price = None
                    r.conversion_factor = None
                    r.physical_stock = 0
                    r.offshore_selection_qty = 0
                    r.dnv_container = None
                    r.balance_after_selection = 0
                    r.production_date = None
                    r.bbd = None
                    r.coo = None
                    r.shelf_life_percent = None
                    r.days_to_expiry = None
                    r.expiry_status = None
                    r.variance_status = None
                    r.variance_comments = None
                    r.root_cause = None
                    r.responsible = None
                    r.closure_date = None
                    r.action_required = None
                    r.general_comments = None
                    cleared += 1
            session.commit()
            st.success(f"{cleared} zero-balance line(s) cleared and made reusable.")
            st.rerun()

elif menu == "Administration":
    st.header("Administration")
    st.subheader("Audit Log")
    logs = session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
    df = pd.DataFrame([{
        "Date": l.created_at,
        "User": l.user,
        "Action": l.action,
        "Entity": l.entity,
        "Entity ID": l.entity_id,
        "Details": l.details,
    } for l in logs])
    st.dataframe(df, use_container_width=True)
