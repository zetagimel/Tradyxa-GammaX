import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { generateSyntheticData, generateFullSyntheticData } from "./syntheticData";
import fs from "fs";
import path from "path";

const tickerCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 60000; // 1 minute

const simulationJobs = new Map<string, { status: string; progress: number; ticker: string }>();

// Determine data directory (works in both dev and production)
const getDataDir = () => {
  // In production (after build), files are in dist/data/
  const prodPath = path.join(process.cwd(), "data");
  if (fs.existsSync(prodPath)) return prodPath;
  // In development, files are in public/data/
  return path.join(process.cwd(), "public", "data");
};

const DATA_DIR = getDataDir();

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {

  // Helper to read JSON file safely
  const readJsonFile = async (filePath: string) => {
    try {
      if (!fs.existsSync(filePath)) return null;
      const content = await fs.promises.readFile(filePath, 'utf-8');
      if (!content || content.trim() === '') return null;
      return JSON.parse(content);
    } catch (error) {
      console.error(`Error reading JSON file ${filePath}:`, error);
      return null;
    }
  };

  // Helper to get live spot price
  const getLiveSpotPrice = async (ticker: string) => {
    try {
      const liveData = await readJsonFile(path.join(DATA_DIR, 'live', 'spot_prices.json'));

      // Map frontend tickers to yfinance tickers
      let searchTicker = ticker;
      if (ticker === 'NIFTY') searchTicker = '^NSEI';
      else if (ticker === 'BANKNIFTY') searchTicker = '^NSEBANK';
      else if (!ticker.endsWith('.NS')) searchTicker = `${ticker}.NS`;

      if (liveData && liveData.spot_prices && liveData.spot_prices[searchTicker]) {
        return liveData.spot_prices[searchTicker];
      }
      return null;
    } catch (error) {
      return null;
    }
  };

  // Get ticker basic data
  app.get("/api/ticker/:ticker", async (req, res) => {
    try {
      const { ticker } = req.params;
      const cleanTicker = ticker.toUpperCase();

      // Try to read real data first
      let filePath = path.join(DATA_DIR, 'ticker', `${cleanTicker}.json`);
      let data = await readJsonFile(filePath);

      // If not found, try appending .NS (common for Nifty 500 tickers)
      let actualTicker = cleanTicker;
      if (!data && !cleanTicker.endsWith('.NS')) {
        actualTicker = `${cleanTicker}.NS`;
        filePath = path.join(DATA_DIR, 'ticker', `${actualTicker}.json`);
        data = await readJsonFile(filePath);
      }

      // Get live spot price and VIX
      const liveSpot = await getLiveSpotPrice(cleanTicker);
      const liveData = await readJsonFile(path.join(DATA_DIR, 'live', 'spot_prices.json'));

      if (!data) {
        // If no ticker file exists, create minimal structure from spot price only
        console.log(`No data file found for ${cleanTicker}, using spot price data only`);
        if (!liveSpot) {
          return res.status(404).json({ error: `No data available for ${cleanTicker}` });
        }

        // Create minimal response with just spot price data
        data = {
          ticker: cleanTicker,
          metrics: {
            spotPrice: Number(liveSpot.spot_price) || 0,
            spotChangePercent: Number(liveSpot.change_percent) || 0,
            spotChange: (Number(liveSpot.spot_price) * Number(liveSpot.change_percent)) / 100,
            vix: liveData?.india_vix?.vix || 0,
            slippageExpectation: 0,
          },
          verdict: null,
          analysis: null
        };
      } else {
        // Real file exists - compute slippage expectation from _slippage.json
        const slippageFile = path.join(DATA_DIR, 'ticker', `${actualTicker}_slippage.json`);
        const slippageData = await readJsonFile(slippageFile);

        let slippageExpectation = 0;
        if (slippageData) {
          // Calculate median slippage across all volume levels
          const allMedians: number[] = [];
          for (const volumeKey in slippageData) {
            const volData = slippageData[volumeKey];
            if (volData && typeof volData.median === 'number') {
              allMedians.push(volData.median * 100); // Convert to percentage
            }
          }
          if (allMedians.length > 0) {
            // Use median of medians as slippage expectation
            allMedians.sort((a, b) => a - b);
            const mid = Math.floor(allMedians.length / 2);
            slippageExpectation = allMedians.length % 2 === 0
              ? (allMedians[mid - 1] + allMedians[mid]) / 2
              : allMedians[mid];
          }
        }

        // Add slippageExpectation to metrics
        if (!data.metrics) data.metrics = {};
        data.metrics.slippageExpectation = Number(slippageExpectation.toFixed(3));

        // Overlay live spot price if available
        if (liveSpot && data.metrics) {
          data.metrics.spotPrice = Number(liveSpot.spot_price) || 0;
          data.metrics.spotChangePercent = Number(liveSpot.change_percent) || 0;
          data.metrics.spotChange = (data.metrics.spotPrice * data.metrics.spotChangePercent) / 100;
        }

        // Overlay India VIX if available (prioritize live VIX over hardcoded value)
        if (liveData && liveData.india_vix && data.metrics) {
          data.metrics.vix = liveData.india_vix.vix;
          data.metrics.vix_latest = liveData.india_vix.vix; // Also update vix_latest
        }
      }

      res.json(data);
    } catch (error) {
      console.error("Error fetching ticker data:", error);
      res.status(500).json({ error: "Failed to fetch ticker data" });
    }
  });

  // Get ticker full data
  app.get("/api/ticker/:ticker/full", async (req, res) => {
    try {
      const { ticker } = req.params;
      const cleanTicker = ticker.toUpperCase();

      // Try to read real data first
      const filePath = path.join(DATA_DIR, 'ticker', `${cleanTicker}.json`);
      let data = await readJsonFile(filePath);

      if (!data) {
        console.log(`No full data file found for ${cleanTicker}, using synthetic`);
        data = generateFullSyntheticData(cleanTicker);
      } else {
        // Real file exists - use it but augment missing fields with synthetic
        const synthetic = generateFullSyntheticData(cleanTicker);
        
        // Keep real data fields, only fill in missing ones from synthetic
        data = {
          meta: data.meta || synthetic.meta,
          metrics: data.metrics || synthetic.metrics,
          features_head: data.features_head || synthetic.features_head,
          // Real market microstructure data
          volumeProfile: data.volumeProfile && data.volumeProfile.length > 0 ? data.volumeProfile : synthetic.volumeProfile,
          candles: data.candles && data.candles.length > 0 ? data.candles : synthetic.candles,
          bollingerBands: data.bollingerBands && data.bollingerBands.length > 0 ? data.bollingerBands : synthetic.bollingerBands,
          orderbook: data.orderbook && data.orderbook.length > 0 ? data.orderbook : synthetic.orderbook,
          rollingAverages: data.rollingAverages && data.rollingAverages.length > 0 ? data.rollingAverages : synthetic.rollingAverages,
          absorptionFlow: data.absorptionFlow && data.absorptionFlow.length > 0 ? data.absorptionFlow : synthetic.absorptionFlow,
          heatmap: data.heatmap && data.heatmap.length > 0 ? data.heatmap : synthetic.heatmap,
          histogram: data.histogram && data.histogram.length > 0 ? data.histogram : synthetic.histogram,
          slippageSamples: data.slippageSamples && data.slippageSamples.length > 0 ? data.slippageSamples : synthetic.slippageSamples,
          // Keep synthetic for timeline (no market data source)
          timelineEvents: synthetic.timelineEvents
        };
      }

      res.json(data);
    } catch (error) {
      console.error("Error fetching full ticker data:", error);
      res.status(500).json({ error: "Failed to fetch full ticker data" });
    }
  });

  // Run simulation
  app.post("/api/run_simulation", async (req, res) => {
    try {
      const { ticker } = req.body;
      if (!ticker) {
        return res.status(400).json({ error: "Ticker is required" });
      }

      const jobId = `sim_${ticker}_${Date.now()}`;
      simulationJobs.set(jobId, { status: "running", progress: 0, ticker });

      // Simulate async processing
      setTimeout(() => {
        simulationJobs.set(jobId, { status: "running", progress: 50, ticker });
      }, 500);

      setTimeout(() => {
        // Clear cache to force refresh with new data
        tickerCache.delete(`basic_${ticker}`);
        tickerCache.delete(`full_${ticker}`);
        simulationJobs.set(jobId, { status: "completed", progress: 100, ticker });
      }, 1000);

      res.json({ jobId, status: "running", message: "Simulation started" });
    } catch (error) {
      console.error("Error running simulation:", error);
      res.status(500).json({ error: "Failed to run simulation" });
    }
  });

  // Get simulation status
  app.get("/api/simulation/:jobId", async (req, res) => {
    try {
      const { jobId } = req.params;
      const job = simulationJobs.get(jobId);

      if (!job) {
        return res.status(404).json({ error: "Job not found" });
      }

      res.json(job);
    } catch (error) {
      console.error("Error fetching simulation status:", error);
      res.status(500).json({ error: "Failed to fetch simulation status" });
    }
  });

  // Serve JSON files from /data/ticker/ with .NS fallback support
  // This allows the queryClient to fetch files directly
  // IMPORTANT: Overlays live spot prices and VIX on the static JSON data
  app.get("/data/ticker/:filename", async (req, res) => {
    try {
      const { filename } = req.params;
      
      // Map friendly index names to yfinance symbols
      const INDEX_MAP: Record<string, string> = {
        "NIFTY.json": "^NSEI.json",
        "BANKNIFTY.json": "^NSEBANK.json"
      };
      
      // Try to read the file as requested
      let filePath = path.join(DATA_DIR, 'ticker', filename);
      let data = await readJsonFile(filePath);

      // If not found, try index mapping (NIFTY.json → ^NSEI.json)
      let actualTicker = filename.replace('.json', '');
      if (!data && filename in INDEX_MAP) {
        const mappedFilename = INDEX_MAP[filename];
        filePath = path.join(DATA_DIR, 'ticker', mappedFilename);
        data = await readJsonFile(filePath);
        if (data) {
          actualTicker = mappedFilename.replace('.json', '');
        }
      }

      // If still not found and filename doesn't have .NS, try with .NS suffix
      if (!data && !filename.includes('.NS') && !filename.startsWith('^')) {
        const nsFilename = filename.replace('.json', '.NS.json');
        filePath = path.join(DATA_DIR, 'ticker', nsFilename);
        data = await readJsonFile(filePath);
        if (data) {
          actualTicker = nsFilename.replace('.json', '');
        }
      }

      if (!data) {
        return res.status(404).json({ error: `File not found: ${filename}` });
      }

      // OVERLAY LIVE DATA: Get live spot prices and VIX
      // Map friendly names back to yfinance symbols for live data lookup
      let cleanTicker = actualTicker.replace('.NS', '').toUpperCase();
      // If it's an index file (^NSEI.json), use the yfinance symbol for live data lookup
      let liveDataTicker = cleanTicker;
      if (actualTicker.startsWith('^')) {
        liveDataTicker = actualTicker; // Use ^NSEI or ^NSEBANK as-is
      } else if (cleanTicker === 'NIFTY') {
        liveDataTicker = '^NSEI';
      } else if (cleanTicker === 'BANKNIFTY') {
        liveDataTicker = '^NSEBANK';
      }
      
      const liveSpot = await getLiveSpotPrice(liveDataTicker);
      const liveData = await readJsonFile(path.join(DATA_DIR, 'live', 'spot_prices.json'));

      // Overlay live spot price if available
      if (liveSpot && data.metrics) {
        data.metrics.spot_price = Number(liveSpot.spot_price) || data.metrics.spot_price || 0;
        data.metrics.spotPrice = data.metrics.spot_price; // Also set camelCase version
        data.metrics.spotChangePercent = Number(liveSpot.change_percent) || 0;
        data.metrics.spotChange = (data.metrics.spot_price * data.metrics.spotChangePercent) / 100;
      }

      // Overlay live India VIX if available (prioritize over hardcoded 15.0)
      if (liveData && liveData.india_vix && data.metrics) {
        const liveVix = liveData.india_vix.vix;
        if (liveVix && liveVix > 0) {
          data.metrics.vix = liveVix;
          data.metrics.vix_latest = liveVix;
        }
      }

      // Compute slippage expectation from _slippage.json if not already present
      if (data.metrics && !data.metrics.slippageExpectation) {
        const slippageFile = path.join(DATA_DIR, 'ticker', `${actualTicker}_slippage.json`);
        const slippageData = await readJsonFile(slippageFile);
        if (slippageData) {
          const allMedians: number[] = [];
          for (const volumeKey in slippageData) {
            const volData = slippageData[volumeKey];
            if (volData && typeof volData.median === 'number') {
              allMedians.push(volData.median * 100);
            }
          }
          if (allMedians.length > 0) {
            allMedians.sort((a, b) => a - b);
            const mid = Math.floor(allMedians.length / 2);
            const slippageExpectation = allMedians.length % 2 === 0
              ? (allMedians[mid - 1] + allMedians[mid]) / 2
              : allMedians[mid];
            data.metrics.slippageExpectation = Number(slippageExpectation.toFixed(3));
          }
        }
      }

      // Set proper headers for JSON
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
      res.json(data);
    } catch (error) {
      console.error(`Error serving ticker file ${req.params.filename}:`, error);
      res.status(500).json({ error: "Failed to serve file" });
    }
  });

  return httpServer;
}
