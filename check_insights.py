import json

data = json.load(open('public/data/ticker/LEMONTREE.json'))

print("="*60)
print("LEMON TREE - INSIGHTS BASED ON REAL DATA")
print("="*60)

# 1. Slippage Insight
slippage = data['metrics'].get('slippageExpectation', 0)
print(f"\n1. SLIPPAGE: {slippage:.3f}%")
if slippage < 0.02:
    insight = "✓ Easy to buy/sell - Good!"
elif slippage < 0.05:
    insight = "✓ Pretty easy - OK!"
elif slippage < 0.10:
    insight = "⚠ A bit hard to buy/sell"
else:
    insight = "⚠ Very hard to buy/sell - Be careful!"
print(f"   → {insight}")

# 2. Volume Profile Insight
vp = data['volumeProfile']
if vp:
    max_vol = max(vp, key=lambda x: x['volume'])
    peak_price = max_vol['price']
    above = sum(v['volume'] for v in vp if v['price'] > peak_price)
    below = sum(v['volume'] for v in vp if v['price'] < peak_price)
    print(f"\n2. VOLUME PROFILE: Peak at ₹{peak_price}")
    print(f"   Volume above peak: {above:,}")
    print(f"   Volume below peak: {below:,}")
    if above > below * 1.2:
        insight = "📉 People sold LOWER prices before - Market moved UP since then"
    elif below > above * 1.2:
        insight = "📈 People bought LOWER prices - Price climbed UP from there"
    else:
        insight = "➡ People divided on direction - Market stable"
    print(f"   → {insight}")

# 3. Orderbook Insight
ob = data['orderbook']
if ob:
    total_bid = sum(o['bidQty'] for o in ob)
    total_ask = sum(o['askQty'] for o in ob)
    ratio = total_bid / max(total_ask, 1)
    print(f"\n3. ORDERBOOK: Total Bids {total_bid:,} vs Asks {total_ask:,}")
    print(f"   Bid/Ask Ratio: {ratio:.2f}")
    if ratio > 1.3:
        insight = "🟢 More buyers than sellers - Might go UP!"
    elif ratio < 0.7:
        insight = "🔴 More sellers than buyers - Might go DOWN!"
    else:
        insight = "🟡 Equal buyers & sellers - No clear direction"
    print(f"   → {insight}")

# 4. Bollinger Bands Insight
bb = data['bollingerBands']
if bb and len(bb) > 0:
    latest = bb[-1]
    if latest['upper'] and latest['lower']:
        position = (latest['close'] - latest['lower']) / (latest['upper'] - latest['lower'])
        print(f"\n4. BOLLINGER BANDS: Position {position:.0%}")
        print(f"   Price ₹{latest['close']:.2f} (Lower ₹{latest['lower']:.2f}, Upper ₹{latest['upper']:.2f})")
        if position > 0.8:
            insight = "⬆⬆ Price is HIGH - May come down soon"
        elif position < 0.2:
            insight = "⬇⬇ Price is LOW - May go up soon"
        elif position > 0.5:
            insight = "⬆ Price is higher - Might keep going up"
        else:
            insight = "⬇ Price is lower - Might keep going down"
        print(f"   → {insight}")

# 5. Rolling Averages Insight
ra = data['rollingAverages']
if ra and len(ra) > 0:
    latest = ra[-1]
    print(f"\n5. ROLLING AVERAGES:")
    print(f"   MA5: ₹{latest['ma5']}, MA20: ₹{latest['ma20']}, MA50: ₹{latest['ma50']}")
    if latest['ma5'] > latest['ma20'] and latest['ma20'] > latest['ma50']:
        insight = "🟢 GOOD - Everything shows price going UP"
    elif latest['ma5'] < latest['ma20'] and latest['ma20'] < latest['ma50']:
        insight = "🔴 BAD - Everything shows price going DOWN"
    else:
        insight = "🟡 MIXED - Signs are confused"
    print(f"   → {insight}")

# 6. Slippage vs Volume (Scatter) Insight
ss = data['slippageSamples']
if ss:
    avg_vol = sum(s['volume'] for s in ss) / len(ss)
    avg_slip = sum(abs(s['slippage']) for s in ss) / len(ss)
    print(f"\n6. SLIPPAGE vs VOLUME: Avg {avg_slip:.3f}% slippage")
    print(f"   Avg Volume: {avg_vol:,.0f}")
    if avg_slip < 0.03:
        insight = "✓ Easy to trade - Low cost"
    elif avg_slip < 0.07:
        insight = "⚠ Normal - Medium cost"
    else:
        insight = "❌ Hard to trade - High cost"
    print(f"   → {insight}")

# 7. Heatmap Insight
hm = data['heatmap']
if hm:
    peak = max(hm, key=lambda x: x['value'])
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day_name = days[peak['dayOfWeek']]
    print(f"\n7. ACTIVITY HEATMAP: Peak intensity {peak['value']}")
    print(f"   {day_name} at {peak['hour']}:00")
    insight = f"🔥 Most active: {day_name} at {peak['hour']}:00 - Busiest time!"
    print(f"   → {insight}")

# 8. Absorption Flow Insight
af = data['absorptionFlow']
if af and len(af) > 0:
    latest = af[-1]
    total = latest['buyFlow'] + latest['sellFlow']
    buy_pct = latest['buyFlow'] / total * 100 if total > 0 else 50
    print(f"\n8. ABSORPTION FLOW: Latest {latest['date']}")
    print(f"   Buy Flow: {buy_pct:.0f}%, Sell Flow: {100-buy_pct:.0f}%")
    if buy_pct > 55:
        insight = "🟢 More people BUYING - Price might go UP"
    elif buy_pct < 45:
        insight = "🔴 More people SELLING - Price might go DOWN"
    else:
        insight = "🟡 Balanced - No clear direction"
    print(f"   → {insight}")

# 9. Histogram (Returns Distribution) Insight
hist = data['histogram']
if hist:
    # Find dominant range
    total = sum(h['count'] for h in hist)
    small_moves = sum(h['count'] for h in hist if abs(h['bin']) < 1.0)
    print(f"\n9. RETURNS DISTRIBUTION: {small_moves}/{total} days had small moves")
    pct = small_moves / total * 100 if total > 0 else 0
    print(f"   {pct:.0f}% of returns are within ±1.0%")
    if pct > 50:
        insight = "🎯 Price stable - Small moves"
    elif pct > 30:
        insight = "📊 Price moderate - Normal volatility"
    else:
        insight = "⚡ Price volatile - Big swings"
    print(f"   → {insight}")

print("\n" + "="*60)
print("✅ ALL INSIGHTS ADAPT TO REAL DATA!")
print("="*60)
