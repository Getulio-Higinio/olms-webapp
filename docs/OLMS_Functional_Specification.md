# OLMS Functional Specification

## Purpose
OLMS controls procurement, receiving, stock on hand, offshore selection, container planning, variance management, loadout reporting and loadout closure.

## Core rules
1. PO data creates procurement records but physical stock remains zero.
2. Invoice data creates physical stock using Invoice Qty × Conversion Factor.
3. If an item exists with Physical Stock = 0, reuse/update that line.
4. If an item exists with Physical Stock > 0, create a new transaction record.
5. Close Loadout clears zero-balance transactional fields while keeping item master fields.

## Production roadmap
1. Add role-based login.
2. Migrate SQLite to PostgreSQL.
3. Add PDF extraction service with preview validation.
4. Add attachment storage for POs, invoices and loadout documents.
5. Add approval workflows and electronic sign-off.
