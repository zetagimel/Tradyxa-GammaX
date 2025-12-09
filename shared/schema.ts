import { z } from "zod";

// Verdict component structure
export const verdictComponentSchema = z.object({
  name: z.string(),
  weight: z.number(),
  value: z.number(),
  contribution: z.number(),
});

// Verdict schema - allows both old and new formats
export const verdictSchema = z.object({
  timestamp: z.string(),
  direction: z.enum(["BULLISH", "BEARISH", "NEUTRAL", "UP", "DOWN"]), // Support both old and new values
  points: z.number().optional(),
  score: z.number().optional(),
  error: z.number().optional(),
  confidence: z.number().optional(),
  components: z.union([
    z.array(verdictComponentSchema),
    z.record(z.number()), // Also support object format: { momentum: 1.0, flow: -0.0645, ... }
  ]).optional(),
  explanation: z.string().optional(),
  data_quality: z.enum(["GOOD", "LOW", "INSUFFICIENT"]).optional(),
  n_samples: z.union([
    z.number(),
    z.object({
      slippage: z.number().optional(),
      monte: z.number().optional(),
      features: z.number().optional(),
    })
  ]).optional(),
  ml_enhanced: z.boolean().optional(),
  version: z.string().optional(),
  params: z.record(z.any()).optional(),
}).passthrough(); // Allow extra fields that might be in the data

// OHLCV candle data
export const candleSchema = z.object({
  date: z.string(),
  open: z.number(),
  high: z.number(),
  low: z.number(),
  close: z.number(),
  volume: z.number(),
});

// Volume profile bucket
export const volumeBucketSchema = z.object({
  price: z.number(),
  volume: z.number(),
  buyVolume: z.number(),
  sellVolume: z.number(),
});

// Orderbook level
export const orderbookLevelSchema = z.object({
  price: z.number(),
  bidQty: z.number(),
  askQty: z.number(),
});

// Slippage sample
export const slippageSampleSchema = z.object({
  timestamp: z.string(),
  expected: z.number(),
  actual: z.number(),
  slippage: z.number(),
  volume: z.number(),
});

// Timeline event
export const timelineEventSchema = z.object({
  timestamp: z.string(),
  type: z.enum(["earnings", "dividend", "split", "news", "economic"]),
  title: z.string(),
  impact: z.enum(["positive", "negative", "neutral"]),
});

// Heatmap cell
export const heatmapCellSchema = z.object({
  hour: z.number(),
  dayOfWeek: z.number(),
  value: z.number(),
  count: z.number(),
});

// Monte Carlo simulation result
export const monteCarloResultSchema = z.object({
  percentile: z.number(),
  values: z.array(z.number()),
});

// Bollinger bands data point
export const bollingerDataSchema = z.object({
  date: z.string(),
  close: z.number(),
  upper: z.number(),
  middle: z.number(),
  lower: z.number(),
});

// Rolling average data point
export const rollingDataSchema = z.object({
  date: z.string(),
  value: z.number(),
  ma5: z.number(),
  ma20: z.number(),
  ma50: z.number(),
});

// Absorption flow data
export const absorptionDataSchema = z.object({
  date: z.string(),
  buyFlow: z.number(),
  sellFlow: z.number(),
  netFlow: z.number(),
});

// Meta information
export const metaSchema = z.object({
  ticker: z.string(),
  name: z.string(),
  exchange: z.string(),
  currency: z.string(),
  lastUpdated: z.string(),
  dataQuality: z.enum(["GOOD", "LOW", "INSUFFICIENT"]),
});

// Core metrics
export const metricsSchema = z.object({
  spot_price: z.number().optional(),
  vix_latest: z.number().optional(),
  volatility_latest: z.number().optional(),
  coordinated_flow: z.number().optional(),
  amihud_latest: z.number().optional(),
  lambda_latest: z.number().optional(),
  liquidity_depth_proxy: z.number().optional(),
  mfc_latest: z.number().optional(),
  trade_sizing_multiplier: z.number().optional(),
  ml_regime_label: z.string().optional(),
  ml_regime_prob: z.number().optional(),
  vol_zscore_latest: z.number().optional(),
  verdict: verdictSchema,
  // Legacy camelCase fields (for backward compatibility)
  spotPrice: z.number().optional(),
  spotChange: z.number().optional(),
  spotChangePercent: z.number().optional(),
  vix: z.number().optional(),
  vixChange: z.number().optional(),
  slippageExpectation: z.number().optional(),
  slippageStd: z.number().optional(),
  avgVolume: z.number().optional(),
  volumeChange: z.number().optional(),
  openInterest: z.number().optional(),
  oiChange: z.number().optional(),
  impliedVolatility: z.number().optional(),
  historicalVolatility: z.number().optional(),
});

// Full ticker data
export const tickerDataSchema = z.object({
  meta: metaSchema,
  metrics: metricsSchema,
});

// Extended/full ticker data
export const tickerFullDataSchema = z.object({
  meta: metaSchema,
  metrics: metricsSchema,
  candles: z.array(candleSchema).default([]),
  volumeProfile: z.array(volumeBucketSchema).default([]),
  orderbook: z.array(orderbookLevelSchema).default([]),
  slippageSamples: z.array(slippageSampleSchema).default([]),
  timelineEvents: z.array(timelineEventSchema).default([]),
  heatmap: z.array(heatmapCellSchema).default([]),
  monteCarlo: z.array(monteCarloResultSchema).default([]),
  bollingerBands: z.array(bollingerDataSchema).default([]),
  rollingAverages: z.array(rollingDataSchema).default([]),
  absorptionFlow: z.array(absorptionDataSchema).default([]),
  histogram: z.array(z.object({
    bin: z.number(),
    count: z.number(),
    cumulative: z.number(),
  })).default([]),
  // Allow features_head for backward compatibility
  features_head: z.record(z.any()).optional(),
}).passthrough(); // Allow extra fields that might be in the data

// Simulation job status
export const simulationJobSchema = z.object({
  jobId: z.string(),
  ticker: z.string(),
  status: z.enum(["pending", "running", "completed", "failed"]),
  progress: z.number(),
  message: z.string().optional(),
  result: z.any().optional(),
});

// Type exports
export type VerdictComponent = z.infer<typeof verdictComponentSchema>;
export type Verdict = z.infer<typeof verdictSchema>;
export type Candle = z.infer<typeof candleSchema>;
export type VolumeBucket = z.infer<typeof volumeBucketSchema>;
export type OrderbookLevel = z.infer<typeof orderbookLevelSchema>;
export type SlippageSample = z.infer<typeof slippageSampleSchema>;
export type TimelineEvent = z.infer<typeof timelineEventSchema>;
export type HeatmapCell = z.infer<typeof heatmapCellSchema>;
export type MonteCarloResult = z.infer<typeof monteCarloResultSchema>;
export type BollingerData = z.infer<typeof bollingerDataSchema>;
export type RollingData = z.infer<typeof rollingDataSchema>;
export type AbsorptionData = z.infer<typeof absorptionDataSchema>;
export type Meta = z.infer<typeof metaSchema>;
export type Metrics = z.infer<typeof metricsSchema>;
export type TickerData = z.infer<typeof tickerDataSchema>;
export type TickerFullData = z.infer<typeof tickerFullDataSchema>;
export type SimulationJob = z.infer<typeof simulationJobSchema>;

// Tile explain content
export interface TileExplain {
  title: string;
  description: string;
  simpleExplanation?: string;
  thresholds: {
    green: string;
    amber: string;
    red: string;
  };
  actions: string[];
}

// Cookie consent choices
export interface CookieChoices {
  analytics: boolean;
  ads: boolean;
  accepted_at: string;
}

// Theme type
export type Theme = "dark" | "light";

// Data quality type
export type DataQuality = "GOOD" | "LOW" | "INSUFFICIENT";

// Nifty500 ticker entry
export interface Nifty500Ticker {
  symbol: string;
  name: string;
  sector?: string;
}
