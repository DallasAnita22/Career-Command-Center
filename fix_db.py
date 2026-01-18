import os

db_path = os.path.abspath(os.path.join("src", "resume_tool", "portfolio.db"))
print(f"Targeting DB at: {db_path}")

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("✅ Database cleared successfully.")
    except PermissionError:
        print("❌ Error: Database is locked. Please stop the Streamlit app.")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("ℹ️ Database file not found (already clean).")
