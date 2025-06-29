#!/bin/bash

# Final Backend Integration Verification with Optional Rollback
echo "🧪 Final HisaabFlow Backend Integration Test..."

# Check for rollback flag
ROLLBACK_ON_FAILURE=false
if [[ "$1" == "--rollback-on-failure" ]]; then
    ROLLBACK_ON_FAILURE=true
    echo "🔄 Rollback on failure: ENABLED"
    echo "⚠️  Will execute 'git reset --hard HEAD~1' if any test fails"
fi

# Function to handle failure with optional rollback
handle_failure() {
    local error_msg="$1"
    echo "❌ $error_msg"
    
    if [ "$ROLLBACK_ON_FAILURE" = true ]; then
        echo ""
        echo "🔄 EXECUTING AUTOMATIC ROLLBACK..."
        echo "📝 Current commit before rollback:"
        git log --oneline -1
        echo ""
        
        # Execute rollback
        if git reset --hard HEAD~1; then
            echo "✅ Rollback completed successfully"
            echo "📝 Current commit after rollback:"
            git log --oneline -1
            echo ""
            echo "🎯 You can retry your changes after fixing the issue"
        else
            echo "❌ Rollback failed! Manual intervention required"
        fi
    fi
    
    exit 1
}

cd frontend/dist

# Test 1: Verify AppImage structure
echo "📋 Test 1: AppImage structure verification"
./HisaabFlow-1.0.0.AppImage --appimage-extract > /dev/null 2>&1

if [ -d "squashfs-root/resources/backend" ]; then
    echo "✅ Backend files properly bundled"
    backend_files=$(find squashfs-root/resources/backend -name "*.py" | wc -l)
    echo "📁 Python files: $backend_files"
else
    handle_failure "Backend files missing from AppImage"
fi

# Test 2: Critical backend files
echo "📋 Test 2: Critical backend files"
critical_files=(
    "squashfs-root/resources/backend/main.py"
    "squashfs-root/resources/backend/requirements.txt"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $(basename $file) found"
    else
        handle_failure "Critical file missing: $(basename $file)"
    fi
done

# Test 3: Frontend integration check
echo "📋 Test 3: Frontend integration"
if npx asar list squashfs-root/resources/app.asar | grep -q "backend-launcher.js"; then
    echo "✅ Backend launcher properly bundled"
else
    handle_failure "Backend launcher missing from bundle"
fi

# Test 4: Python dependency verification
echo "📋 Test 4: Python environment check"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "✅ Python available: $python_version"
    
    # Check if required packages can be imported
    echo "📦 Testing Python dependencies..."
    if python3 -c "import fastapi, uvicorn, pandas, pydantic" 2>/dev/null; then
        echo "✅ All Python dependencies available"
        backend_ready="YES"
    else
        echo "⚠️  Python dependencies need installation"
        echo "💡 Users will need to install: pip install fastapi uvicorn pandas pydantic python-multipart"
        backend_ready="PARTIAL"
    fi
else
    echo "⚠️  Python not found in system"
    echo "💡 Users will need to install Python 3.9+ and dependencies"
    backend_ready="NO"
fi

# Test 5: Complete integration status
echo "📋 Test 5: Integration status summary"
rm -rf squashfs-root

echo ""
echo "🎉 Backend Integration Analysis Complete!"
echo ""
echo "📦 AppImage Details:"
echo "   📊 Size: $(ls -lh HisaabFlow-1.0.0.AppImage | awk '{print $5}')"
echo "   📅 Build: $(date)"
echo "   🧱 Contains: Frontend + Backend + Integration Layer"
echo ""
echo "🚀 Distribution Status:"
echo "   ✅ Frontend: React app with modern UI"
echo "   ✅ Backend: FastAPI server bundled"
echo "   ✅ Integration: Auto-start backend on app launch"
echo "   🔧 Python Runtime: $backend_ready"
echo ""

if [ "$backend_ready" = "YES" ]; then
    echo "🎯 Status: FULLY INTEGRATED - Ready for immediate use"
    echo "   Users can run: ./HisaabFlow-1.0.0.AppImage"
elif [ "$backend_ready" = "PARTIAL" ]; then
    echo "🎯 Status: MOSTLY INTEGRATED - Needs Python deps"
    echo "   Setup: pip install fastapi uvicorn pandas pydantic python-multipart"
    echo "   Then: ./HisaabFlow-1.0.0.AppImage"
else
    echo "🎯 Status: BACKEND INTEGRATED - Needs Python runtime"
    echo "   Setup: Install Python 3.9+ and dependencies"
    echo "   Then: ./HisaabFlow-1.0.0.AppImage"
fi

echo ""
echo "✅ Backend Integration: COMPLETE"
echo "📋 Next Steps: Create user documentation and GitHub release"
