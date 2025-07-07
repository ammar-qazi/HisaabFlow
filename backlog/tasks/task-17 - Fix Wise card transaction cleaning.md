---
id: task-17
title: Fix Wise card transaction cleaning
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Bug Fix", "Backend", "High Priority"]
dependencies: []
---

## Description

Fix Wise card transaction description cleaning that is not working properly.

## Acceptance Criteria

- [ ] Investigate why transactions like "Card transaction of 155.00 EUR issued by Revolut**0540* Dublin" are not being cleaned
- [ ] Fix the config pattern: `card_transaction_cleanup = Card transaction of [\d,.]+ \w{3} issued by ([^|]+)|\1`
- [ ] Ensure cleaned transactions show merchant name only
- [ ] Test with sample Wise card transactions
- [ ] Run description cleaning tests to validate fixes

## Context

From TASKS.md: "Wise Card Transaction Cleaning Not Working - Transactions like 'Card transaction of 155.00 EUR issued by Revolut**0540* Dublin' not being cleaned"

## Files to Investigate

- `configs/wise*.conf` files
- Description cleaning functionality in unified config service