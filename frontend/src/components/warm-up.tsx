"use client";

import { useEffect } from "react";

/**
 * Fires one request at /api/warm when the page loads, so the API is awake by the
 * time the visitor reaches a page that needs it.
 *
 * Renders nothing, and failure is ignored - this is an optimisation, and a visitor
 * should never see it fail.
 */
export function WarmUp() {
  useEffect(() => {
    // keepalive lets the request finish even if the visitor navigates away first.
    void fetch("/api/warm", { keepalive: true }).catch(() => {});
  }, []);

  return null;
}
