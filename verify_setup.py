#!/usr/bin/env python3
"""
BH Worldwide Dashboard Setup Verification Script
Verifies all required files and data are present for deployment
"""

import os
import json
from pathlib import Path

def verify_setup():
    """Verify all required files and directories exist"""
    base_path = Path(__file__).parent
    
    print("🔍 BH Worldwide Dashboard Setup Verification")
    print("=" * 50)
    
    # Required files
    required_files = [
        "app.py",
        "requirements.txt", 
        "README.md"
    ]
    
    # Required data files
    required_data_files = [
        "BH_Worldwide_Logistics/Customer_Data/Airlines/major_customers.json",
        "BH_Worldwide_Logistics/Operations/AOG_Center/active_cases.json",
        "BH_Worldwide_Logistics/Business_Intelligence/Competitors/competitor_analysis.json",
        "BH_Worldwide_Logistics/Operations/Pricing/current_pricing_model.json",
        "BH_Worldwide_Logistics/Business_Intelligence/Pain_Points/current_challenges.json",
        "BH_Worldwide_Logistics/Financial/Lost_Opportunities/monthly_analysis.json",
        "BH_Worldwide_Logistics/Financial/BH_Actual_Financials/financial_summary.json"
    ]
    
    # Check main files
    print("\n📁 Main Files:")
    all_good = True
    for file in required_files:
        file_path = base_path / file
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            print(f"  ✅ {file} ({size:.1f} KB)")
        else:
            print(f"  ❌ {file} - MISSING!")
            all_good = False
    
    # Check data files
    print("\n📊 Data Files:")
    for file in required_data_files:
        file_path = base_path / file
        if file_path.exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)
                size = file_path.stat().st_size / 1024  # KB
                print(f"  ✅ {file} ({size:.1f} KB) - Valid JSON")
            except json.JSONDecodeError:
                print(f"  ⚠️  {file} - Invalid JSON!")
                all_good = False
        else:
            print(f"  ❌ {file} - MISSING!")
            all_good = False
    
    # Check optional enhanced files
    optional_files = [
        "BH_Worldwide_Logistics/Customer_Data/Airlines/extended_customers.json",
        "BH_Worldwide_Logistics/Operations/AOG_Center/extended_aog_cases.json",
        "BH_Worldwide_Logistics/Operations/Inventory/extended_inventory.json"
    ]
    
    print("\n🎁 Optional Enhanced Files:")
    for file in optional_files:
        file_path = base_path / file
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            print(f"  ✅ {file} ({size:.1f} KB)")
        else:
            print(f"  ➖ {file} - Not present (will use fallback)")
    
    # Total size calculation
    total_size = sum(f.stat().st_size for f in base_path.rglob('*') if f.is_file()) / 1024 / 1024  # MB
    
    print(f"\n📏 Total Size: {total_size:.1f} MB")
    
    # Final status
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 Setup verification PASSED!")
        print("✅ Ready for deployment to Streamlit Cloud")
        print("✅ All required files present")
        print("✅ JSON data files valid")
        print("\n🚀 Next steps:")
        print("   1. Upload to GitHub repository")
        print("   2. Deploy to Streamlit Cloud")
        print("   3. Share URL with team in Singapore")
    else:
        print("❌ Setup verification FAILED!")
        print("⚠️  Missing required files - see errors above")
        return False
    
    return all_good

if __name__ == "__main__":
    verify_setup()