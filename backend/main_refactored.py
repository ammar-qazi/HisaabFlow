"""
Main FastAPI server entry point
Simplified server startup using modular API components
"""
from api import create_app

# Create the FastAPI app using modular components
app = create_app()

if __name__ == "__main__":
    import uvicorn
    print("\n🌟 Starting Enhanced FastAPI server with Modular Architecture...")
    print("   📡 Backend will be available at: http://127.0.0.1:8000")
    print("   📋 API docs available at: http://127.0.0.1:8000/docs")
    print("   🧹 Features: Data cleaning pipeline integrated")
    print("   💱 Features: Automatic currency column addition")
    print("   📊 Features: Numeric amount standardization")
    print("   💱 Features: Enhanced Transfer Detection with Exchange Amount Support")
    print("   🔧 Features: Configuration-based transfer detection")
    print("   ⏹️  Press Ctrl+C to stop")
    print("")
    
    try:
        uvicorn.run(
            "main:app",  # Use import string instead of app object
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("   💡 Try: python main.py")
        print("   💡 Or: uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
