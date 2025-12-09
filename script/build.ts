import { build as esbuild } from "esbuild";
import { build as viteBuild } from "vite";
import { rm, readFile, cp } from "fs/promises";
import path from "path";

// server deps to bundle to reduce openat(2) syscalls
// which helps cold start times
const allowlist = [
  "@google/generative-ai",
  "@neondatabase/serverless",
  "axios",
  "connect-pg-simple",
  "cors",
  "date-fns",
  "drizzle-orm",
  "drizzle-zod",
  "express",
  "express-rate-limit",
  "express-session",
  "jsonwebtoken",
  "memorystore",
  "multer",
  "nanoid",
  "nodemailer",
  "openai",
  "passport",
  "passport-local",
  "stripe",
  "uuid",
  "ws",
  "xlsx",
  "zod",
  "zod-validation-error",
];

async function buildAll() {
  // Clean only index.cjs, not entire dist folder (vite needs it)
  try {
    await rm("dist/index.cjs", { force: true });
  } catch (e) {
    // File might not exist, that's okay
  }

  console.log("building client...");
  await viteBuild();

  console.log("copying data files...");
  // Copy public/data folder to dist/ (for serving API data)
  try {
    await cp("public/data", "dist/data", { recursive: true, force: true });
    console.log("✓ Data files copied to dist/data");
  } catch (e) {
    console.warn("⚠ Could not copy data files:", e);
  }

  console.log("copying routing config...");
  // Copy _routes.json for Cloudflare Pages routing
  try {
    await cp("public/_routes.json", "dist/_routes.json", { force: true });
    console.log("✓ Routing config copied");
  } catch (e) {
    console.warn("⚠ Could not copy _routes.json:", e);
  }

  console.log("building server...");
  const pkg = JSON.parse(await readFile("package.json", "utf-8"));
  const allDeps = [
    ...Object.keys(pkg.dependencies || {}),
    ...Object.keys(pkg.devDependencies || {}),
  ];
  const externals = allDeps.filter((dep) => !allowlist.includes(dep));

  await esbuild({
    entryPoints: ["server/index.ts"],
    platform: "node",
    bundle: true,
    format: "cjs",
    outfile: "dist/index.cjs",
    define: {
      "process.env.NODE_ENV": '"production"',
    },
    minify: true,
    external: externals,
    logLevel: "info",
  });
}

buildAll().catch((err) => {
  console.error(err);
  process.exit(1);
});
