import type { Verdict } from "@shared/schema";

/**
 * Generate a simple, trader-friendly explanation of the verdict
 */
export function getSimpleVerdictExplanation(verdict: Verdict): string {
    const direction = verdict.direction.toLowerCase();
    const isUp = verdict.direction === "BULLISH";
    const isDown = verdict.direction === "BEARISH";
    const isNeutral = verdict.direction === "NEUTRAL";

    // Determine strength
    const absScore = Math.abs(verdict.score);
    let strength = "";
    if (absScore < 0.2) strength = "very gentle";
    else if (absScore < 0.5) strength = "gentle";
    else if (absScore < 0.8) strength = "moderate";
    else strength = "strong";

    // Build simple explanation
    let explanation = "We looked at price movement and buying/selling activity. ";

    if (isNeutral) {
        explanation += "Signals don't clearly point UP or DOWN. Market is unclear right now. ";
    } else {
        const dirText = isUp ? "going UP" : "going DOWN";
        explanation += `Signals point ${strength === "very gentle" ? "very slightly" : strength === "gentle" ? "slightly" : strength} toward price ${dirText}. `;
    }

    // Parse recommendation from explanation
    const origExplanation = verdict.explanation.toLowerCase();
    if (origExplanation.includes("twap")) {
        const twapMatch = origExplanation.match(/(\d+)\s*twap/i);
        const numTwaps = twapMatch ? twapMatch[1] : "3";
        explanation += `Don't buy/sell all at once - split your trade into ${numTwaps} smaller pieces over time to be safe.`;
    } else if (origExplanation.includes("reduce size") || origExplanation.includes("wait")) {
        explanation += "Consider using less money or waiting for a better time to trade.";
    } else if (origExplanation.includes("full size")) {
        explanation += "Market conditions look good - you can trade confidently, just split into 2 parts to be safe.";
    } else {
        explanation += "Be cautious with your trades.";
    }

    return explanation;
}

/**
 * Get component breakdown in simple terms
 */
export function getComponentBreakdown(verdict: Verdict): string[] {
    const breakdown: string[] = [];

    // Find components
    const comp = verdict.components;

    if (typeof comp === 'object' && !Array.isArray(comp)) {
        // It's an object with named components
        const momentum = comp.momentum || 0;
        const flow = comp.flow || 0;
        const liquidity = comp.liquidity || 0;
        const impactCost = comp.impact_cost || comp.impactCost || 0;

        // Momentum
        if (momentum > 0.1) breakdown.push("📈 Momentum = Price is trending UP lately");
        else if (momentum < -0.1) breakdown.push("📉 Momentum = Price is trending DOWN lately");
        else breakdown.push("➡️ Momentum = Price is moving sideways");

        // Flow
        if (flow > 0.1) breakdown.push("🟢 Flow = More people are BUYING");
        else if (flow < -0.1) breakdown.push("🔴 Flow = More people are SELLING");
        else breakdown.push("🟡 Flow = Buying and selling are balanced");

        // Liquidity
        if (liquidity > 0.1) breakdown.push("💧 Liquidity = Easy to trade this stock");
        else if (liquidity < -0.1) breakdown.push("⚠️ Liquidity = Hard to trade, be careful");
        else breakdown.push("💧 Liquidity = Normal trading conditions");

        // Impact Cost
        if (impactCost > -0.05) breakdown.push("💰 Cost = Trading fees are low");
        else if (impactCost < -0.15) breakdown.push("💰 Cost = Trading fees are HIGH");
        else breakdown.push("💰 Cost = Trading fees are medium");
    }

    return breakdown;
}

/**
 * Get TWAP explanation
 */
export function getTWAPExplanation(verdict: Verdict): string {
    const explanation = verdict.explanation.toLowerCase();

    if (explanation.includes("3 twap")) {
        return "Split ₹10 lakh → three ₹3.33 lakh trades";
    } else if (explanation.includes("2 twap")) {
        return "Split ₹10 lakh → two ₹5 lakh trades";
    } else if (explanation.includes("reduce size")) {
        return "Trade less money than usual";
    } else if (explanation.includes("wait")) {
        return "Maybe don't trade right now";
    }

    return "Follow the recommendation above";
}
