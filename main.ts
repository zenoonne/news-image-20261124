// Entry point for the news-image-20261124 entry.
// The page itself is pre-rendered at build time into entry.png next to this
// file; here we just publish that PNG into the grader's output directory,
// which is /output unless MAKEFUN_OUTPUT_DIR points somewhere else.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
