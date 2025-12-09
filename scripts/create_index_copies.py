#!/usr/bin/env python3
"""
Create friendly name copies of index JSON files.
Dashboard expects NIFTY.json and BANKNIFTY.json, but pipeline saves ^NSEI.json and ^NSEBANK.json
"""
import json
import shutil
import os

DATA_DIR = os.path.join("public", "data", "ticker")

INDEX_MAP = {
    "^NSEI": "NIFTY",
    "^NSEBANK": "BANKNIFTY"
}

def create_index_copies():
    """Create friendly name copies of index files"""
    for yf_symbol, friendly_name in INDEX_MAP.items():
        # Main JSON file
        src = os.path.join(DATA_DIR, f"{yf_symbol}.json")
        dst = os.path.join(DATA_DIR, f"{friendly_name}.json")
        
        if os.path.exists(src):
            # Read and update meta ticker field
            with open(src, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update meta ticker to friendly name
            if 'meta' in data:
                data['meta']['ticker'] = friendly_name
            
            # Write copy with friendly name
            with open(dst, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"✅ Created {friendly_name}.json")
        else:
            print(f"⚠️  Source not found: {src}")
        
        # Slippage files
        for suffix in ["_slippage.json", "_monte_slippage.json"]:
            src_slip = os.path.join(DATA_DIR, f"{yf_symbol}{suffix}")
            dst_slip = os.path.join(DATA_DIR, f"{friendly_name}{suffix}")
            
            if os.path.exists(src_slip):
                shutil.copy2(src_slip, dst_slip)
                print(f"✅ Created {friendly_name}{suffix}")
            else:
                print(f"⚠️  Source not found: {src_slip}")

if __name__ == "__main__":
    create_index_copies()
    print("\n✅ Index file copies created!")

