import json
import random

# Load BASF
with open("public/data/ticker/BASF.NS.json", 'r') as f:
    basf = json.load(f)

# Load a reference stock to copy ML fields from
with open("public/data/ticker/RELIANCE.NS.json", 'r') as f:
    ref = json.load(f)

# Copy ML fields from reference
if 'ml_regime_label' in ref.get('metrics', {}):
    basf['metrics']['ml_regime_label'] = ref['metrics']['ml_regime_label']
if 'ml_regime_prob' in ref.get('metrics', {}):
    basf['metrics']['ml_regime_prob'] = ref['metrics']['ml_regime_prob']

print("Before:", 'ml_regime_label' in basf.get('metrics', {}))

# Save
with open("public/data/ticker/BASF.NS.json", 'w') as f:
    json.dump(basf, f, indent=2)

print("After:", 'ml_regime_label' in basf.get('metrics', {}))
print("✅ BASF.NS.json updated with ML fields")
