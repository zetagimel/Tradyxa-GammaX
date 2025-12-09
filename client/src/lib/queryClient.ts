import { QueryClient, QueryFunction } from "@tanstack/react-query";

async function throwIfResNotOk(res: Response) {
  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }
}

export async function apiRequest(
  method: string,
  url: string,
  data?: unknown | undefined,
): Promise<Response> {
  const res = await fetch(url, {
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
    credentials: "include",
  });

  await throwIfResNotOk(res);
  return res;
}

type UnauthorizedBehavior = "returnNull" | "throw";
export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
  ({ on401: unauthorizedBehavior }) =>
  async ({ queryKey }) => {
    let path = "/" + queryKey.join("/") as string;
    console.log("[QueryClient] Fetching:", path);
    
    // Add cache-busting timestamp for data files to force fresh downloads
    if (path.includes("/data/ticker/")) {
      const timestamp = new Date().getTime();
      path = `${path}?t=${timestamp}`;
    }
    
    // Try to fetch the file
    let res = await fetch(path, {
      credentials: "include",
      cache: "no-store", // Disable HTTP cache
    });

    // If not found and it's a ticker data file, try with .NS suffix
    // Handles: TICKER.json → TICKER.NS.json, TICKER_slippage.json → TICKER.NS_slippage.json, etc.
    if (res.status === 404 && path.includes("/data/ticker/") && !path.includes(".NS")) {
      // Handle query string in path (cache-busting timestamp)
      const [basePath, queryString] = path.split("?");
      const nsPath = basePath.replace(".json", ".NS.json") + (queryString ? `?${queryString}` : "");
      console.log("[QueryClient] Got 404, trying fallback:", nsPath);
      res = await fetch(nsPath, {
        credentials: "include",
        cache: "no-store", // Disable HTTP cache
      });
    }

    if (unauthorizedBehavior === "returnNull" && res.status === 401) {
      console.log("[QueryClient] Got 401, returning null");
      return null;
    }

    if (!res.ok) {
      console.error(`[QueryClient] Request failed: ${res.status} ${res.statusText}`, path);
      const text = (await res.text()) || res.statusText;
      throw new Error(`${res.status}: ${text}`);
    }

    const data = await res.json();
    console.log("[QueryClient] Success, fetched:", path, data);
    
    // Validate that we got real data, not an error page
    if (!data || (typeof data === 'object' && Object.keys(data).length === 0)) {
      console.warn("[QueryClient] Got empty response from:", path);
    }
    
    return data;
  };

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});
