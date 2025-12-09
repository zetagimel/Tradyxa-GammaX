#!/usr/bin/env python3
"""
Audit all ticker JSON files and regenerate broken ones
"""

import os
import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tradyxa_pipeline

DATA_DIR = "public/data/ticker"

def check_json_validity(file_path):
    """Check if JSON file is valid"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for NaN in content (invalid JSON)
        if 'NaN' in content or 'Infinity' in content or '-Infinity' in content:
            return False, "Contains NaN or Infinity"
            
        # Try to parse JSON
        json.loads(content)
        return True, "Valid"
        
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {str(e)[:50]}"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

def audit_all_jsons():
    """Audit all JSON files"""
    print("🔍 Auditing all ticker JSON files...\n")
    
    valid_count = 0
    invalid_count = 0
    invalid_files = []
    
    # Get all JSON files
    json_files = list(Path(DATA_DIR).glob("*.json"))
    total = len(json_files)
    
    print(f"Found {total} JSON files\n")
    
    for json_file in json_files:
        ticker = json_file.stem
        is_valid, reason = check_json_validity(json_file)
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            invalid_files.append((ticker, reason))
            print(f"❌ {ticker}: {reason}")
    
    print(f"\n{'='*60}")
    print(f"📊 AUDIT SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Valid:   {valid_count}/{total}")
    print(f"❌ Invalid: {invalid_count}/{total}")
    print(f"{'='*60}\n")
    
    return invalid_files

def fix_invalid_jsons(invalid_files):
    """Regenerate invalid JSON files"""
    if not invalid_files:
        print("✅ No files to fix!")
        return
    
    print(f"🔧 Regenerating {len(invalid_files)} invalid files...\n")
    
    success_count = 0
    failed_count = 0
    
    for ticker, reason in invalid_files:
        try:
            print(f"Fixing {ticker}...", end=" ")
            tradyxa_pipeline.run_pipeline_for_ticker(ticker, use_yf=True)
            
            # Verify fix
            json_path = os.path.join(DATA_DIR, f"{ticker}.json")
            is_valid, _ = check_json_validity(json_path)
            
            if is_valid:
                print("✅ Fixed")
                success_count += 1
            else:
                print("⚠️ Still broken")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Failed: {str(e)[:30]}")
            failed_count += 1
    
    print(f"\n{'='*60}")
    print(f"🔧 FIX SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Fixed:  {success_count}/{len(invalid_files)}")
    print(f"❌ Failed: {failed_count}/{len(invalid_files)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("\n🚀 JSON Audit & Repair Tool\n")
    
    # Audit
    invalid_files = audit_all_jsons()
    
    # Ask to fix
    if invalid_files:
        response = input(f"\n🔧 Regenerate {len(invalid_files)} broken files? (y/n): ")
        if response.lower() == 'y':
            fix_invalid_jsons(invalid_files)
        else:
            print("\n⏭️  Skipped regeneration")
    
    print("\n✅ Done!\n")
