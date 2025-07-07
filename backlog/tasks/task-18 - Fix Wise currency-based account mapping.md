---
id: task-18
title: Fix Wise currency-based account mapping
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Bug Fix", "Backend", "High Priority"]
dependencies: []
---

## Description

Fix Wise currency-based account mapping that shows generic 'Wise' instead of currency-specific account names.

## Acceptance Criteria

- [ ] Fix currency mapping warnings: "Currency 'USD' not found in account_mapping for wise"
- [ ] Ensure USD transactions map to 'TransferWise'
- [ ] Ensure EUR transactions map to 'EURO Wise'
- [ ] Ensure HUF transactions map to 'Hungarian'
- [ ] Test with sample Wise transactions in different currencies
- [ ] Run account mapping tests to validate fixes

## Context

From TASKS.md: "Wise Currency-Based Account Mapping Broken - All Wise transactions show Account = 'Wise' instead of currency-specific names"

## Files to Investigate

- `configs/wise*.conf` files
- Account mapping functionality in transformation service