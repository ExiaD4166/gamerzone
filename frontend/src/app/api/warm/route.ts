import { api } from "@/lib/api";

/**
 * Nudges the API awake.
 *
 * Free hosting puts an idle service to sleep, and waking it takes the better part
 * of a minute. The pages a visitor sees first - home and about - need no API at
 * all, so the wait would land on whoever clicks Downloads or Sign in.
 *
 * Calling this while the home page renders spends that minute during the reading
 * rather than after the click. It only fires on a real visit, so an idle site
 * still sleeps.
 *
 * The browser cannot call the API directly - API_URL is deliberately server-side
 * only - so this route stands in the middle.
 */
export async function GET() {
  await api("/api/v1/health");

  // The result is irrelevant: the point was making the request at all.
  return new Response(null, { status: 204 });
}
