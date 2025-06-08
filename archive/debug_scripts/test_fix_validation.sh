#!/bin/bash

echo "🧪 Testing NayaPay Template Categorization Fix"
echo "=============================================="

# Navigate to project directory
cd /home/ammar/claude_projects/bank_statement_parser

echo "📋 Checking template content..."
echo "Template categorization rules:"
cat templates/NayaPay_Enhanced_Template.json | jq '.categorization_rules[] | {rule_name, priority, conditions, actions}' | head -20

echo ""
echo "🔍 Template has Ride Hailing rule?"
cat templates/NayaPay_Enhanced_Template.json | jq '.categorization_rules[] | select(.rule_name == "Ride Hailing Services")'

echo ""
echo "✅ Fix Applied Summary:"
echo "1. Frontend now preserves ALL template properties:"
echo "   - ✅ categorization_rules (previously lost)"
echo "   - ✅ default_category_rules (previously lost)" 
echo "   - ✅ bank_name (previously lost)"
echo "   - ✅ column_mapping (now properly merged)"

echo ""
echo "2. Key changes in MultiCSVApp.js:"
echo "   - Template config merging instead of overwriting"
echo "   - Preservation of categorization rules"
echo "   - Better logging for debugging"
echo "   - Proper column mapping inheritance"

echo ""
echo "🎯 Expected behavior after fix:"
echo "   - Raast Out transactions under -2000 → Travel/Ride Hailing App"
echo "   - Mobile Topup transactions → Bills & Fees/Mobile charge"
echo "   - Transfer transactions → cleaned descriptions"
echo "   - All template rules should now apply correctly"

echo ""
echo "🚀 To test the fix:"
echo "1. Restart frontend: npm start (in frontend directory)"
echo "2. Upload a NayaPay CSV file"
echo "3. Verify template auto-selection and application"
echo "4. Check transformation results for proper categorization"
