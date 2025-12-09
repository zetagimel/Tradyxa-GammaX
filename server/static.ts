import express, { type Express } from "express";
import fs from "fs";
import path from "path";

export function serveStatic(app: Express) {
  const distPath = path.resolve(__dirname, "public");
  const dataPath = path.resolve(__dirname, "data");
  
  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`,
    );
  }

  // Serve static assets from the dist folder
  app.use(express.static(distPath));
  
  // Serve data files from the data folder (but NOT /data/ticker/* which is handled by routes)
  // This allows other data files (like /data/live/*) to be served statically
  if (fs.existsSync(dataPath)) {
    // Only serve non-ticker data files statically
    // The /data/ticker/* route is handled in routes.ts with .NS fallback
    app.use("/data/live", express.static(path.join(dataPath, "live")));
    app.use("/data/raw", express.static(path.join(dataPath, "raw")));
  }

  // Fall through to index.html if the file doesn't exist (SPA routing)
  // BUT NOT for /data requests, those should return 404
  app.use("*", (_req, res) => {
    res.sendFile(path.resolve(distPath, "index.html"));
  });
}
