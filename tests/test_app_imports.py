"""Quick sanity check for app imports and data loader initialization"""
import sys
import os

# Suppress Streamlit warnings during import
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

def test_data_loader_import():
    """Test that data_loader imports correctly"""
    try:
        from src.data_loader import get_data_loader, MktDataLoader
        print("✅ src.data_loader imports successfully")
        print(f"   get_data_loader: {get_data_loader}")
        print(f"   MktDataLoader: {MktDataLoader}")
        return True
    except Exception as e:
        print(f"❌ Failed to import src.data_loader: {e}")
        return False

def test_fundinvestigator_app_import():
    """Test that fundinvestigator_app imports correctly"""
    try:
        # This will import but won't execute the app
        import fundinvestigator_app
        print("✅ fundinvestigator_app.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import fundinvestigator_app: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wip_app_import():
    """Test that wip/app imports correctly"""
    try:
        # This will import but won't execute the app
        import wip.app
        print("✅ wip/app.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import wip.app: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fund_deepdive_import():
    """Test that fund_deepdive page imports correctly"""
    try:
        import app_pages.fund_deepdive
        print("✅ app_pages/fund_deepdive.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import app_pages.fund_deepdive: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loader_initialization():
    """Test that data loader can be initialized"""
    try:
        from src.data_loader import get_data_loader
        loader = get_data_loader()
        print("✅ Data loader initialized successfully")
        print(f"   Type: {type(loader).__name__}")

        # Test connection
        success, message = loader.test_connection()
        if success:
            print(f"✅ Data loader connection test: {message}")
        else:
            print(f"⚠️  Data loader connection test: {message}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize data loader: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("APP IMPORT SANITY CHECKS")
    print("="*70 + "\n")

    results = []
    results.append(("Data Loader Import", test_data_loader_import()))
    results.append(("Fund Deepdive Import", test_fund_deepdive_import()))
    results.append(("FundInvestigator App Import", test_fundinvestigator_app_import()))
    results.append(("WIP App Import", test_wip_app_import()))
    results.append(("Data Loader Initialization", test_data_loader_initialization()))

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n✅ All import checks passed!")
    else:
        print("\n❌ Some import checks failed")
        sys.exit(1)
