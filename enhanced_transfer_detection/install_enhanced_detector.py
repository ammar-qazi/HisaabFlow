"""
Enhanced integration of the new transfer detection system
Replaces the old transfer_detector.py with improved cross-bank and currency conversion support
"""

import os
import shutil
from datetime import datetime

def backup_and_replace_transfer_detector():
    """
    Backup the current transfer detector and replace with enhanced version
    """
    
    backend_dir = "/home/ammar/claude_projects/bank_statement_parser/backend"
    enhanced_dir = "/home/ammar/claude_projects/bank_statement_parser/enhanced_transfer_detection"
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backend_dir}/transfer_detector_backup_{timestamp}.py"
    
    print(f"📦 Creating backup: {backup_file}")
    shutil.copy(f"{backend_dir}/transfer_detector.py", backup_file)
    
    # Copy enhanced version
    print(f"🔄 Replacing with enhanced version...")
    shutil.copy(f"{enhanced_dir}/enhanced_transfer_detector.py", f"{backend_dir}/transfer_detector_enhanced.py")
    
    print(f"✅ Enhanced transfer detector installed!")
    print(f"   Original backed up to: {backup_file}")
    print(f"   Enhanced version at: {backend_dir}/transfer_detector_enhanced.py")
    
    return backup_file

def update_main_py_for_enhanced_detection():
    """
    Update main.py to use the enhanced transfer detector
    """
    
    print(f"🔄 Updating main.py to use enhanced transfer detection...")
    
    # Read current main.py
    with open("/home/ammar/claude_projects/bank_statement_parser/backend/main.py", 'r') as f:
        content = f.read()
    
    # Update import statement
    content = content.replace(
        "from transfer_detector import TransferDetector",
        "from transfer_detector_enhanced import EnhancedTransferDetector as TransferDetector"
    )
    
    # Write updated content
    with open("/home/ammar/claude_projects/bank_statement_parser/backend/main.py", 'w') as f:
        f.write(content)
    
    print(f"✅ main.py updated to use enhanced transfer detection")

if __name__ == "__main__":
    print("🚀 Installing Enhanced Transfer Detection System")
    print("=" * 50)
    
    try:
        # Backup and replace
        backup_file = backup_and_replace_transfer_detector()
        
        # Update main.py
        update_main_py_for_enhanced_detection()
        
        print(f"\n🎉 Enhanced Transfer Detection Successfully Installed!")
        print(f"📊 New Features:")
        print(f"   ✅ Cross-bank transfers (Wise→NayaPay, Wise→Bank Alfalah)")
        print(f"   ✅ Currency conversions (USD→EUR, USD→PKR)")
        print(f"   ✅ Enhanced confidence scoring")
        print(f"   ✅ Better bank pattern recognition")
        print(f"   ✅ Improved matching algorithms")
        
        print(f"\n📁 Files:")
        print(f"   🔄 Enhanced detector: backend/transfer_detector_enhanced.py")
        print(f"   📦 Backup: {backup_file}")
        print(f"   🔧 Updated: backend/main.py")
        
        print(f"\n🚀 Ready to process Wise→NayaPay transfers!")
        
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        import traceback
        print(f"📚 Traceback: {traceback.format_exc()}")
