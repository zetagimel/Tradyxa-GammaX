import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { HelpCircle, TrendingUp, TrendingDown, Minus, ArrowRight } from "lucide-react";
import { DataQualityBadge } from "./DataQualityBadge";
import type { Verdict, VerdictComponent } from "@shared/schema";
import { cn } from "@/lib/utils";

interface VerdictTileProps {
  ticker: string;
  verdict: Verdict | null;
  notional?: number;
  multiplier?: number;
  isLoading?: boolean;
  onHelpClick?: () => void;
  onClick?: () => void;
}

function ContributorBar({ component }: { component: VerdictComponent }) {
  const maxContribution = 100;
  const width = Math.min(Math.abs(component.contribution) / maxContribution * 100, 100);
  const isPositive = component.contribution >= 0;

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-24 truncate text-muted-foreground font-medium">
        {component.name}
      </span>
      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all",
            isPositive ? "bg-success" : "bg-danger"
          )}
          style={{ width: `${width}%` }}
        />
      </div>
      <span className={cn(
        "w-12 text-right font-mono",
        isPositive ? "text-success" : "text-danger"
      )}>
        {isPositive ? "+" : ""}{component.contribution.toFixed(1)}
      </span>
    </div>
  );
}

export function VerdictTile({
  ticker,
  verdict,
  notional = 1000000,
  multiplier = 1.0,
  isLoading = false,
  onHelpClick,
  onClick,
}: VerdictTileProps) {
  if (isLoading) {
    return (
      <Card className="col-span-full hover-elevate cursor-pointer min-h-[240px] sm:min-h-[280px]">
        <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2 px-3 sm:px-4 py-2 sm:py-3">
          <Skeleton className="h-5 sm:h-6 w-28 sm:w-32" />
          <Skeleton className="h-5 sm:h-6 w-14 sm:w-16" />
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-6 sm:py-8 px-3 sm:px-4">
          <Skeleton className="h-12 sm:h-16 w-56 sm:w-64 mb-3 sm:mb-4" />
          <Skeleton className="h-3 sm:h-4 w-44 sm:w-48 mb-4 sm:mb-6" />
          <Skeleton className="h-2 w-full max-w-md mb-6 sm:mb-8" />
          <Skeleton className="h-28 sm:h-32 w-full max-w-lg" />
        </CardContent>
      </Card>
    );
  }

  if (!verdict) {
    return (
      <Card className="col-span-full hover-elevate cursor-pointer min-h-[240px] sm:min-h-[280px]" onClick={onClick}>
        <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2 px-3 sm:px-4 py-2 sm:py-3">
          <CardTitle className="text-base sm:text-lg font-semibold">Verdict</CardTitle>
          <DataQualityBadge quality="INSUFFICIENT" />
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-8 sm:py-12 px-3 sm:px-4">
          <p className="text-xs sm:text-sm text-muted-foreground text-center mb-4">
            Insufficient data to generate verdict. Run simulation or wait for more data.
          </p>
        </CardContent>
      </Card>
    );
  }

  const DirectionIcon = verdict.direction === "BULLISH"
    ? TrendingUp
    : verdict.direction === "BEARISH"
      ? TrendingDown
      : Minus;

  const directionColor = verdict.direction === "BULLISH"
    ? "text-success"
    : verdict.direction === "BEARISH"
      ? "text-danger"
      : "text-muted-foreground";

  const roundedPoints = verdict.confidence < 0.4
    ? Math.round(verdict.points / 5) * 5
    : verdict.points;

  return (
    <div className="col-span-full flex justify-center px-2 sm:px-4">
      <Card
        className="w-full max-w-4xl hover-elevate active-elevate-2 cursor-pointer transition-colors"
        onClick={onClick}
        data-testid="tile-verdict"
      >
        <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2 px-4 sm:px-6 py-2 sm:py-3">
          <CardTitle className="text-base sm:text-lg font-semibold flex items-center gap-1 sm:gap-2 flex-wrap">
            Verdict
            <Badge variant="outline" className="font-mono text-xs">
              {new Date(verdict.timestamp).toLocaleTimeString()}
            </Badge>
          </CardTitle>
          <div className="flex items-center gap-1 sm:gap-2">
            <DataQualityBadge quality={verdict.data_quality} />
            {onHelpClick && (
              <Button
                size="icon"
                variant="ghost"
                className="h-6 w-6"
                onClick={(e) => {
                  e.stopPropagation();
                  onHelpClick();
                }}
                aria-label="Help for Verdict"
                data-testid="button-help-verdict"
              >
                <HelpCircle className="h-4 w-4 text-muted-foreground" />
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex flex-col items-center py-4 sm:py-6 px-4 sm:px-6">
          <div className="flex items-center gap-2 sm:gap-4 mb-4 flex-wrap justify-center">
            <span className="text-xl sm:text-3xl font-bold font-mono text-muted-foreground">
              {ticker}
            </span>
            <ArrowRight className="h-5 w-5 sm:h-6 sm:w-6 text-muted-foreground" />
            <div className={cn("flex items-center gap-1 sm:gap-2", directionColor)}>
              <DirectionIcon className="h-6 w-6 sm:h-8 sm:w-8 md:h-10 md:w-10" />
              <span className="text-2xl sm:text-4xl md:text-5xl font-bold font-mono">
                {verdict.direction}
              </span>
            </div>
          </div>

          <div className="flex items-baseline gap-2 mb-2">
            <span className={cn("text-4xl md:text-5xl font-bold font-mono", directionColor)}>
              {verdict.direction === "BULLISH" ? "+" : verdict.direction === "BEARISH" ? "-" : ""}
              {Math.abs(roundedPoints).toFixed(0)}
            </span>
            <span className="text-lg text-muted-foreground font-mono">
              pts
            </span>
            <span className="text-lg text-muted-foreground font-mono">
              ({"\u00B1"}{verdict.error.toFixed(1)})
            </span>
          </div>

          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-muted-foreground">Confidence</span>
            <span className="text-lg font-bold font-mono">
              {(verdict.confidence * 100).toFixed(0)}%
            </span>
          </div>

          <div className="flex items-center gap-2 mb-4 bg-muted/50 px-3 py-1 rounded-md">
            <span className="text-xs text-muted-foreground uppercase">💰 Invest THIS MUCH</span>
            <span className="text-sm font-bold font-mono">
              ₹{((notional * multiplier).toLocaleString('en-IN', { maximumFractionDigits: 0 }))}
            </span>
            <span className="text-xs text-muted-foreground">
              ({(multiplier * 100).toFixed(0)}%)
            </span>
          </div>

          <Progress
            value={verdict.confidence * 100}
            className="w-full max-w-md h-2 mb-6"
          />

          {/* Technical Explanation */}
          <div className="w-full max-w-2xl mb-4">
            <p className="text-sm font-semibold text-muted-foreground mb-1">
              Technical Analysis:
            </p>
            <p className="text-center text-muted-foreground text-sm">
              {verdict.explanation}
            </p>
          </div>

          {/* Simple Explanation */}
          <div className="w-full max-w-2xl mb-6 bg-blue-500/10 dark:bg-blue-400/10 border border-blue-500/20 rounded-lg p-4">
            <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 mb-2">
              📖 Simple Explanation:
            </p>
            <p className="text-sm text-foreground mb-3">
              {(() => {
                const absPoints = Math.abs(verdict.points);
                const conf = verdict.confidence;
                let strength = "";
                if (absPoints < 5 || conf < 0.3) strength = "very slightly";
                else if (absPoints < 15 || conf < 0.5) strength = "slightly";
                else if (absPoints < 30 || conf < 0.7) strength = "moderately";
                else strength = "strongly";

                let explanation = "We looked at price movement and buying/selling activity. ";

                if (verdict.direction === "NEUTRAL") {
                  explanation += "Signals don't clearly point UP or DOWN. Market is unclear right now. ";
                } else {
                  const dirText = verdict.direction === "BULLISH" ? "going UP" : "going DOWN";
                  explanation += `Signals point ${strength} toward price ${dirText}. `;
                }

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
              })()}
            </p>

            {/* Component Breakdown */}
            <div className="text-xs text-foreground/80 space-y-1 mt-3 pt-3 border-t border-blue-500/20">
              <p className="font-semibold text-blue-600 dark:text-blue-400 mb-1">What These Mean:</p>
              {(() => {
                const breakdown: string[] = [];

                // Try to extract momentum/flow if available  
                if (verdict.explanation.includes("momentum") || verdict.explanation.includes("flow")) {
                  if (verdict.direction === "BULLISH") {
                    breakdown.push("📈 Momentum + Flow = Price trending UP, more BUYING");
                  } else if (verdict.direction === "BEARISH") {
                    breakdown.push("📉 Momentum + Flow = Price trending DOWN, more SELLING");
                  } else {
                    breakdown.push("➡️ Momentum + Flow = Unclear direction");
                  }
                }

                if (verdict.explanation.includes("TWAP")) {
                  const twapMatch = verdict.explanation.match(/(\d+)\s*TWAP/i);
                  if (twapMatch) {
                    const num = twapMatch[1];
                    const perPiece = (10 / parseInt(num)).toFixed(2);
                    breakdown.push(`💡 ${num} TWAPs = Split ₹10 lakh into ${num} pieces of ₹${perPiece} lakh each`);
                  }
                }

                return breakdown.map((item, idx) => (
                  <p key={idx}>{item}</p>
                ));
              })()}
            </div>
          </div>

          {/* Disclaimer */}
          <p className="text-[9px] text-muted-foreground/60 text-center max-w-2xl leading-tight mb-4">
            This analysis is for educational and informational purposes only. It does not constitute financial advice, investment recommendations, or an offer to buy or sell any securities. Trading involves substantial risk of loss. The site owner and operators are not responsible for any trading decisions made based on this information. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.
          </p>

          {verdict.components.length > 0 && (
            <div className="w-full max-w-lg space-y-2">
              <h4 className="text-sm font-semibold mb-3">Contributors</h4>
              {verdict.components.slice(0, 5).map((component, idx) => (
                <ContributorBar key={idx} component={component} />
              ))}
            </div>
          )}

          <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground">
            <span>
              Samples: {typeof verdict.n_samples === 'object'
                ? verdict.n_samples.features
                : verdict.n_samples}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
