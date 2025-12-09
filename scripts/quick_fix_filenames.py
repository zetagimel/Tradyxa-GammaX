
import os
import json
import shutil
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("fix_filenames")

DATA_DIR = os.path.join("public", "data", "ticker")

def fix_filenames():
    if not os.path.exists(DATA_DIR):
        log.error(f"Directory not found: {DATA_DIR}")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".NS.json")]
    log.info(f"Found {len(files)} .NS.json files to process.")

    for filename in files:
        friendly_name = filename.replace(".NS.json", "")
        src_path = os.path.join(DATA_DIR, filename)
        dst_path = os.path.join(DATA_DIR, f"{friendly_name}.json")

        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update internal ticker name
            if 'meta' in data:
                data['meta']['ticker'] = friendly_name
            
            # Write friendly copy
            with open(dst_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            log.info(f"✅ Created: {friendly_name}.json matches {filename}")

            # Also copy slippage files if they exist
            for suffix in ["_slippage.json", "_monte_slippage.json"]:
                src_slip = os.path.join(DATA_DIR, f"{filename.replace('.json', '')}{suffix}")
                dst_slip = os.path.join(DATA_DIR, f"{friendly_name}{suffix}")
                if os.path.exists(src_slip):
                    shutil.copy2(src_slip, dst_slip)
                    log.info(f"   - Copied {suffix}")

        except Exception as e:
            log.error(f"❌ Failed to process {filename}: {e}")

if __name__ == "__main__":
    print("starting filename fix...")
    fix_filenames()
    print("Done")
