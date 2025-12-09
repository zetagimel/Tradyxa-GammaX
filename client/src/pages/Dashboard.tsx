import { useState, useEffect, useCallback } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { getSlippageInsight } from "@/lib/chartInsights";
import { LeftRail } from "@/components/LeftRail";
import { RefreshButton } from "@/components/RefreshButton";
import { VerdictTile } from "@/components/VerdictTile";
import { NumericCard } from "@/components/NumericCard";
import { HowToTile } from "@/components/HowToTile";
import { OtherProductsTile } from "@/components/OtherProductsTile";
import { Footer } from "@/components/Footer";
import { InspectorPanel } from "@/components/InspectorPanel";
import { ShareButtons } from "@/components/ShareButtons";
import { DisclaimerModal, shouldShowDisclaimer } from "@/components/DisclaimerModal";
import { CookieConsentModal, shouldShowCookieConsent } from "@/components/CookieConsentModal";
import { ExplainModal, TILE_EXPLAINS } from "@/components/ExplainModal";
import {
  GaugeTile,
  HistogramTile,
  HeatmapTile,
  CandlesWithBands,
  BarWithRolling,
  ScatterSlippage,
  TimelineEvents,
  StackedAreaAbsorption,
  VolumeProfile,
  OrderbookDepth,
} from "@/components/charts";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Menu, X, PanelLeft } from "lucide-react";
import type { TickerData, TickerFullData, TileExplain } from "@shared/schema";
import { cn } from "@/lib/utils";
import { tickerFullDataSchema } from "@shared/schema";
import { AdsterraBanner320x50 } from "@/components/AdsterraBanner320x50";
import { AdsterraNativeBanner } from "@/components/AdsterraNativeBanner";

export default function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState("NIFTY");
  const [notional, setNotional] = useState(1000000);
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [showCookieConsent, setShowCookieConsent] = useState(false);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [inspectorTileId, setInspectorTileId] = useState<string | null>(null);
  const [inspectorData, setInspectorData] = useState<unknown>(null);
  const [explainOpen, setExplainOpen] = useState(false);
  const [explainTile, setExplainTile] = useState<TileExplain | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [liveVix, setLiveVix] = useState<number | null>(null);
  const [liveSpotPrice, setLiveSpotPrice] = useState<number | null>(null);
  const [liveSpotChange, setLiveSpotChange] = useState<number | null>(null);
  const [slippageExpectation, setSlippageExpectation] = useState<number>(0);

  useEffect(() => {
    if (shouldShowDisclaimer()) {
      setShowDisclaimer(true);
    } else if (shouldShowCookieConsent()) {
      setShowCookieConsent(true);
    }

    // Fetch live VIX from spot_prices.json
    const fetchLiveVix = async () => {
      try {
        const response = await fetch('/data/live/spot_prices.json', { cache: 'no-store' });
        if (response.ok) {
          const data = await response.json();
          if (data.india_vix && typeof data.india_vix.vix === 'number' && data.india_vix.vix > 0) {
            setLiveVix(data.india_vix.vix);
            console.log('[Dashboard] Live VIX fetched:', data.india_vix.vix);
          } else {
            console.warn('[Dashboard] Invalid VIX data:', data.india_vix);
          }
        } else {
          console.warn('[Dashboard] Failed to fetch live VIX, status:', response.status);
        }
      } catch (error) {
        console.error('[Dashboard] Failed to fetch live VIX:', error);
      }
    };

    fetchLiveVix();

    // Poll for VIX updates every 30 seconds
    const vixInterval = setInterval(fetchLiveVix, 30000);
    return () => clearInterval(vixInterval);
  }, []);

  // Fetch live spot price for selected ticker from spot_prices.json
  useEffect(() => {
    const fetchLiveSpotPrice = async () => {
      try {
        const response = await fetch('/data/live/spot_prices.json', { cache: 'no-store' });
        if (response.ok) {
          const data = await response.json();
          // Map dashboard ticker to Yahoo symbol
          let ySymbol = selectedTicker;
          if (selectedTicker === 'NIFTY') ySymbol = '^NSEI';
          else if (selectedTicker === 'BANKNIFTY') ySymbol = '^NSEBANK';
          else if (!selectedTicker.endsWith('.NS')) ySymbol = `${selectedTicker}.NS`;

          const tickerData = data.spot_prices?.[ySymbol];
          if (tickerData && typeof tickerData.spot_price === 'number' && tickerData.spot_price > 0) {
            setLiveSpotPrice(tickerData.spot_price);
            setLiveSpotChange(tickerData.change_percent || 0);
            console.log('[Dashboard] Live spot price fetched:', ySymbol, tickerData.spot_price);
          } else {
            // Fallback to null so we use JSON file value
            setLiveSpotPrice(null);
            setLiveSpotChange(null);
          }
        }
      } catch (error) {
        console.error('[Dashboard] Failed to fetch live spot price:', error);
        setLiveSpotPrice(null);
        setLiveSpotChange(null);
      }
    };

    fetchLiveSpotPrice();

    // Poll for spot price updates every 30 seconds
    const spotInterval = setInterval(fetchLiveSpotPrice, 30000);
    return () => clearInterval(spotInterval);
  }, [selectedTicker]);

  // Fetch slippage expectation from _slippage.json file
  useEffect(() => {
    const fetchSlippage = async () => {
      try {
        const cleanTicker = selectedTicker.toUpperCase();
        // Try direct ticker first, then with .NS suffix
        let slippageFile = `/data/ticker/${cleanTicker}_slippage.json`;
        let response = await fetch(slippageFile, { cache: 'no-store' });

        if (response.status === 404 && !cleanTicker.endsWith('.NS')) {
          slippageFile = `/data/ticker/${cleanTicker}.NS_slippage.json`;
          response = await fetch(slippageFile, { cache: 'no-store' });
        }

        if (response.ok) {
          const slippageData = await response.json();
          // Calculate median slippage across all volume levels
          const allMedians: number[] = [];
          for (const volumeKey in slippageData) {
            const volData = slippageData[volumeKey];
            if (volData && typeof volData.median === 'number') {
              allMedians.push(volData.median * 100); // Convert to percentage
            }
          }

          if (allMedians.length > 0) {
            allMedians.sort((a, b) => a - b);
            const mid = Math.floor(allMedians.length / 2);
            const median = allMedians.length % 2 === 0
              ? (allMedians[mid - 1] + allMedians[mid]) / 2
              : allMedians[mid];
            setSlippageExpectation(Number(median.toFixed(3)));
          }
        }
      } catch (error) {
        console.error('Failed to fetch slippage:', error);
      }
    };

    fetchSlippage();
  }, [selectedTicker]);

  const handleDisclaimerAccept = () => {
    setShowDisclaimer(false);
    if (shouldShowCookieConsent()) {
      setShowCookieConsent(true);
    }
  };

  // Use a single query for full data - it contains both metrics and computed fields
  const { data: fullData, isLoading: isLoadingFull, refetch: refetchFull } = useQuery<TickerFullData>({
    queryKey: ["data", "ticker", `${selectedTicker}.json`],
    refetchInterval: 30000, // Poll every 30 seconds for live spot prices
  });

  // Extract metrics from fullData for backward compatibility
  const tickerData = fullData ? { meta: fullData.meta, metrics: fullData.metrics } : undefined;
  const isLoadingTicker = isLoadingFull;
  const refetchTicker = refetchFull;

  const simulationMutation = useMutation({
    mutationFn: async () => {
      return apiRequest("POST", "/api/run_simulation", { ticker: selectedTicker });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["data", "ticker", `${selectedTicker}.json`] });
    },
  });

  const openSmartLink = () => {
    window.open('https://www.effectivegatecpm.com/zedg80yp?key=bae7f179fef2418576ccc1fe6728fcd5', '_blank');
  };

  const handleRefresh = useCallback(async () => {
    openSmartLink(); // Trigger smartlink on refresh
    queryClient.invalidateQueries({ queryKey: ["data", "ticker", `${selectedTicker}.json`] });
    await refetchFull();
  }, [selectedTicker, refetchFull]);

  const openInspector = (tileId: string, data: unknown) => {
    setInspectorTileId(tileId);
    setInspectorData(data);
    setInspectorOpen(true);
  };

  const openExplain = (tileKey: string) => {
    const tile = TILE_EXPLAINS[tileKey];
    if (tile) {
      setExplainTile(tile);
      setExplainOpen(true);
    }
  };

  const isLoading = isLoadingTicker || isLoadingFull;
  const metrics = tickerData?.metrics;
  const quality = tickerData?.meta?.dataQuality || "GOOD";

  useEffect(() => {
    if (fullData) {
      try {
        tickerFullDataSchema.parse(fullData);
        console.log("Validated fullData:", fullData);
      } catch (error) {
        console.error("Validation error in fullData:", error);
      }
    }
  }, [fullData]);

  return (
    <div className="flex min-h-screen bg-background">
      <div
        className={cn(
          "fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden",
          mobileMenuOpen ? "block" : "hidden"
        )}
        onClick={() => setMobileMenuOpen(false)}
      />
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 transform transition-all duration-300 ease-in-out lg:relative lg:translate-x-0 overflow-hidden border-r",
          mobileMenuOpen ? "translate-x-0 w-80" : "-translate-x-full lg:translate-x-0",
          sidebarOpen ? "lg:w-80" : "lg:w-0 lg:border-r-0"
        )}
      >
        <div className="w-80 h-full">
          <LeftRail
            selectedTicker={selectedTicker}
            onTickerChange={(ticker) => {
              setSelectedTicker(ticker);
              setMobileMenuOpen(false);
            }}
            notional={notional}
            onNotionalChange={setNotional}
            verdictMultiplier={metrics?.trade_sizing_multiplier || 0}
          />
        </div>
      </div>

      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex-1 w-full">
          <header className="relative z-30 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b px-4 py-2 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                data-testid="button-mobile-menu"
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="hidden lg:flex"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                title={sidebarOpen ? "Collapse Sidebar" : "Open sidebar to change ticker"}
              >
                <PanelLeft className="h-5 w-5" />
              </Button>
              <div className="flex flex-col">
                <h1 className="font-mono text-xl sm:text-3xl font-bold text-primary tracking-tight">
                  Tradyxa Aztryx
                </h1>
                <div className="hidden md:block">
                  <p className="text-sm sm:text-base font-medium text-muted-foreground">
                    Nifty, BankNifty & Nifty 500 Stocks Intelligence
                  </p>
                  <p className="text-sm text-muted-foreground/80 max-w-2xl">
                    Trained ML models for next-day index moves, slippage forecasting and execution guidance across NIFTY universes.
                    <span
                      className="ml-2 cursor-pointer text-cyan-400 hover:text-cyan-300 transition-colors drop-shadow-[0_0_2px_rgba(34,211,238,0.8)]"
                      onClick={() => {
                        openSmartLink();
                        setSidebarOpen(true);
                      }}
                    >
                      (Click here to Change the Stock Ticker)
                    </span>
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <RefreshButton
                isLoading={isLoading}
                onClick={handleRefresh}
              />
            </div>
          </header>

          <main className="p-2 sm:p-3 md:p-6 max-w-7xl mx-auto">

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-3 md:gap-6">
              {/* ... existing numeric and chart tiles ... */}
              <NumericCard
                title="Spot Price"
                value={liveSpotPrice !== null ? liveSpotPrice : (metrics?.spot_price || metrics?.spotPrice || 0)}
                change={metrics?.spotChange}
                changePercent={liveSpotChange !== null ? liveSpotChange : metrics?.spotChangePercent}
                prefix="₹"
                quality={quality}
                isLoading={isLoadingTicker && liveSpotPrice === null}
                onHelpClick={() => openExplain("spotPrice")}
                onClick={() => openInspector("spotPrice", { spotPrice: liveSpotPrice || metrics?.spot_price || metrics?.spotPrice, spotChange: liveSpotChange || metrics?.spotChange })}
                testId="tile-spot-price"
              />

              <GaugeTile
                title="India VIX"
                value={liveVix !== null && liveVix > 0 ? liveVix : (metrics?.vix_latest || metrics?.vix || 0)}
                min={0}
                max={50}
                thresholds={{ low: 15, high: 25 }}
                quality={quality}
                isLoading={isLoadingTicker && liveVix === null}
                onHelpClick={() => openExplain("indiaVix")}
                onClick={() => openInspector("indiaVix", { vix: liveVix !== null && liveVix > 0 ? liveVix : (metrics?.vix_latest || metrics?.vix), vixChange: metrics?.vixChange })}
                testId="tile-india-vix"
              />

              <NumericCard
                title="Slippage Expectation"
                value={metrics?.slippageExpectation !== undefined ? metrics.slippageExpectation : slippageExpectation}
                suffix="%"
                quality={quality}
                isLoading={isLoadingTicker}
                onHelpClick={() => openExplain("slippage")}
                onClick={() => openInspector("slippage", { slippage: metrics?.slippageExpectation !== undefined ? metrics.slippageExpectation : slippageExpectation, std: metrics?.slippageStd })}
                testId="tile-slippage"
                insight={getSlippageInsight({ median: metrics?.slippageExpectation !== undefined ? metrics.slippageExpectation : slippageExpectation })}
              />

              <VolumeProfile
                title="Volume Profile"
                data={fullData?.volumeProfile || []}
                currentPrice={metrics?.spot_price || metrics?.spotPrice}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("volume")}
                onClick={() => openInspector("volume", fullData?.volumeProfile)}
                testId="tile-volume-profile"
              />

              <OrderbookDepth
                title="Orderbook Depth"
                data={fullData?.orderbook || []}
                midPrice={metrics?.spot_price || metrics?.spotPrice}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("orderbook")}
                onClick={() => openInspector("orderbook", fullData?.orderbook)}
                testId="tile-orderbook"
              />

              <CandlesWithBands
                title="Candles with Bollinger Bands"
                data={fullData?.bollingerBands || []}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("bollinger")}
                onClick={() => openInspector("bollinger", fullData?.bollingerBands)}
                testId="tile-bollinger"
              />

              <BarWithRolling
                title="Price with Rolling Averages"
                data={fullData?.rollingAverages || []}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("rolling")}
                onClick={() => openInspector("rolling", fullData?.rollingAverages)}
                testId="tile-rolling"
              />

              <ScatterSlippage
                title="Slippage vs Volume"
                data={fullData?.slippageSamples || []}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("scatter")}
                onClick={() => openInspector("scatter", fullData?.slippageSamples)}
                onRunSimulation={() => simulationMutation.mutate()}
                testId="tile-scatter"
              />

              <TimelineEvents
                title="Timeline Events"
                data={fullData?.timelineEvents || []}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("timeline")}
                onClick={() => openInspector("timeline", fullData?.timelineEvents)}
                testId="tile-timeline"
              />

              <HeatmapTile
                title="Activity Heatmap"
                data={fullData?.heatmap || []}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("heatmap")}
                onClick={() => openInspector("heatmap", fullData?.heatmap)}
                testId="tile-heatmap"
              />

              <StackedAreaAbsorption
                title="Order Flow Absorption"
                data={fullData?.absorptionFlow || []}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("absorption")}
                onClick={() => openInspector("absorption", fullData?.absorptionFlow)}
                testId="tile-absorption"
              />

              <HistogramTile
                title="Returns Distribution"
                data={fullData?.histogram || []}
                quality={quality}
                isLoading={isLoadingFull}
                onHelpClick={() => openExplain("histogram")}
                onClick={() => openInspector("histogram", fullData?.histogram)}
                testId="tile-histogram"
              />
            </div>

            <div className="mt-4 sm:mt-6 mb-4 sm:mb-6">
              {/* Adsterra 320x50 Banner above Verdict */}
              <AdsterraBanner320x50 />

              <VerdictTile
                ticker={selectedTicker}
                verdict={metrics?.verdict || null}
                notional={notional}
                multiplier={metrics?.trade_sizing_multiplier || 0}
                isLoading={isLoadingTicker}
                onHelpClick={() => openExplain("verdict")}
                onClick={() => openInspector("verdict", metrics?.verdict)}
              />
            </div>

            <div className="mt-4 sm:mt-6">
              <HowToTile
                onLearnMore={(key) => {
                  openSmartLink();
                  openExplain(key);
                }}
                onTileClick={openSmartLink}
              />
              {/* Adsterra Native Banner below HowToTile */}
              <AdsterraNativeBanner />
            </div>

            <div className="mt-4 sm:mt-6">
              <OtherProductsTile />
            </div>
          </main>

          <Footer />
        </div>
      </div>

      <InspectorPanel
        isOpen={inspectorOpen}
        onClose={() => setInspectorOpen(false)}
        tileId={inspectorTileId}
        data={inspectorData}
        ticker={selectedTicker}
      />

      <DisclaimerModal
        isOpen={showDisclaimer}
        onAccept={handleDisclaimerAccept}
      />

      <CookieConsentModal
        isOpen={showCookieConsent}
        onClose={() => setShowCookieConsent(false)}
      />

      <ExplainModal
        isOpen={explainOpen}
        onClose={() => setExplainOpen(false)}
        tile={explainTile}
      />
    </div>
  );
}
