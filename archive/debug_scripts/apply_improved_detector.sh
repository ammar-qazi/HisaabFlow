#!/bin/bash
# Apply improved transfer detector to main.py

echo "🔧 Applying improved transfer detector patch..."

# Create backup
cp /home/ammar/claude_projects/bank_statement_parser/backend/main.py /home/ammar/claude_projects/bank_statement_parser/backend/main.py.backup

# Add import for improved transfer detector
sed -i '/from transfer_detector import TransferDetector/a from transfer_detector_improved import ImprovedTransferDetector' /home/ammar/claude_projects/bank_statement_parser/backend/main.py

# Replace transfer detector usage in the multi-csv transform function
sed -i 's/transfer_detector = TransferDetector(/# OLD: transfer_detector = TransferDetector(/g' /home/ammar/claude_projects/bank_statement_parser/backend/main.py
sed -i '/# OLD: transfer_detector = TransferDetector(/a \                # NEW: Use improved transfer detector with better person-to-person matching\
                transfer_detector = ImprovedTransferDetector(' /home/ammar/claude_projects/bank_statement_parser/backend/main.py

echo "✅ Patch applied successfully!"
echo "📁 Backup saved as main.py.backup"
echo ""
echo "🔍 Changes made:"
echo "   ✅ Added ImprovedTransferDetector import"  
echo "   ✅ Updated transfer detector instantiation"
echo "   ✅ Better person-to-person transfer matching"
echo ""
echo "🚀 The improved algorithm should now detect:"
echo "   👤 Person-to-person transfers (Ammar Qazi)"
echo "   💱 Currency conversions (USD/EUR)"
echo "   📊 All with enhanced logging"
