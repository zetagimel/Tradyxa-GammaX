import json

# Check a sample stock
with open("public/data/ticker/RELIANCE.NS.json", 'r') as f:
    data = json.load(f)

metrics = data.get('metrics', {})
print("Metrics keys:", list(metrics.keys()))
print()
print("Has slippageExpectation:", 'slippageExpectation' in metrics)
print("Has slippageMedian:", 'slippageMedian' in metrics)
print("Has slippageStd:", 'slippageStd' in metrics)
print()
print("Actual values:")
print("  slippageExpectation:", metrics.get('slippageExpectation'))
print("  slippageMedian:", metrics.get('slippageMedian'))
print("  slippageStd:", metrics.get('slippageStd'))
