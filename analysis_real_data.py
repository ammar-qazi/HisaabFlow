# Let's analyze what your actual data looks like from the log:

Real transactions from your log:
- Transfer to Ammar Qazi Meezan Bank (-23000) - Large transfer ✓
- Transfer to Usman Siddique easypaisa Bank (-400) - Small P2P transfer  
- Transfer to Muhammad Riafat easypaisa Bank (-750) - Small P2P transfer
- Transfer to Ghulam Asghar easypaisa Bank (-650) - Small P2P transfer
- Transfer to Muhammad Sajid easypaisa Bank (-1500) - Small P2P transfer
- Transfer to Ali Abbas Khan MCB Bank (-13000) - Large transfer ✓
- Mobile top-up purchased|Zong (-2000) - Mobile recharge ✅

# The issue is that your REAL data shows:
# 1. Mobile top-ups → Bills & Fees ✅ (working)
# 2. Large transfers (>-2000) → Transfer ✅ (working) 
# 3. Small transfers to PEOPLE → These are P2P transfers, should stay as Transfer

# Your original request was wrong - you said "ride hailing and bills & fees for small Raast Out"
# But your actual data shows small Raast Out = person-to-person transfers to individuals
# These SHOULD be categorized as Transfer, not Bills & Fees

print("🔍 ANALYSIS: Your actual data breakdown:")
print("✅ Mobile recharges: 'Mobile top-up purchased' → Bills & Fees (WORKING)")
print("✅ Large transfers: -23000, -13000 → Transfer (WORKING)")  
print("✅ Small P2P transfers: -400 to -1500 to people → Transfer (WORKING)")
print("")
print("❓ Question: Do you have ANY actual ride-hailing or utility bill payments?")
print("   If yes, what do those transaction titles look like?")
print("   If no, then the current categorization is CORRECT!")
