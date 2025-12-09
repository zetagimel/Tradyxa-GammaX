import json

# LEMON
data1 = json.load(open('public/data/ticker/LEMONTREE.json'))
v1 = data1['metrics']['verdict']

print("=== LEMON TREE ===")
print(f"Direction: {v1['direction']}")
print(f"Points: {v1['points']} ± {v1['error']}")
print(f"Confidence: {v1['confidence']*100:.0f}%")
print(f"Explanation: {v1['explanation']}")
print(f"Components: {v1['components']}")

print("\n" + "="*50)

# RELIANCE (synthetic)
data2 = json.load(open('public/data/ticker/RELIANCE.json'))
v2 = data2['metrics']['verdict']

print("\n=== RELIANCE (Synthetic Data) ===")
print(f"Direction: {v2['direction']}")
print(f"Points: {v2['points']} ± {v2['error']}")
print(f"Confidence: {v2['confidence']*100:.0f}%")
print(f"Explanation: {v2['explanation']}")
print(f"Components: {v2['components']}")
