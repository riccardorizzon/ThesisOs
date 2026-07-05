import { defineConfig, devices } from "@playwright/test";

const frontendPort = Number(process.env.PLAYWRIGHT_PORT ?? 3001);
const backendPort = Number(process.env.PLAYWRIGHT_API_PORT ?? 8001);
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${frontendPort}`;
const apiBase = process.env.E2E_API_BASE_URL ?? `http://127.0.0.1:${backendPort}`;
const repoRoot = `${__dirname}/../..`;
const frontendDir = `${repoRoot}/frontend`;
const backendDir = `${repoRoot}/backend`;

process.env.PLAYWRIGHT_BASE_URL = baseURL;
process.env.E2E_API_BASE_URL = apiBase;

export default defineConfig({
  testDir: ".",
  testMatch: "*.spec.ts",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "./evidence/playwright-report" }],
  ],
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: process.env.PLAYWRIGHT_SKIP_WEBSERVER
    ? undefined
    : [
        {
          command: `"${backendDir}/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port ${backendPort}`,
          cwd: backendDir,
          url: `${apiBase}/health`,
          reuseExistingServer: false,
          timeout: 120_000,
          env: {
            ...process.env,
            DATABASE_URL:
              process.env.DATABASE_URL ??
              "postgresql+psycopg://thesisos:thesisos@127.0.0.1:5432/thesisos",
            APP_ENV: "local",
          },
        },
        {
          command: `npm run dev -- -p ${frontendPort}`,
          cwd: frontendDir,
          url: baseURL,
          reuseExistingServer: false,
          timeout: 120_000,
          env: {
            ...process.env,
            PORT: String(frontendPort),
            NEXT_PUBLIC_API_BASE_URL: apiBase,
          },
        },
      ],
});
