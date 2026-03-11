import { Handler } from "@cloudflare/workers-types";

// Cloudflare Pages Function 处理所有 /api/* 请求
// 需要设置环境变量 BACKEND_URL 指向你的后端地址
export const onRequest: Handler = async (context) => {
  const backendUrl = context.env.BACKEND_URL;

  if (!backendUrl) {
    return new Response(
      JSON.stringify({ error: "BACKEND_URL environment variable not set" }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" }
      }
    );
  }

  try {
    const { request } = context;
    const url = new URL(request.url);

    // 移除 BACKEND_URL 尾部斜杠，避免拼接出双斜杠
    const baseUrl = backendUrl.endsWith('/') ? backendUrl.slice(0, -1) : backendUrl;

    // 构建后端请求 URL，包含 pathname 和 search 参数
    const targetUrl = `${baseUrl}${url.pathname}${url.search}`;

    // 复制请求头，移除 hop-by-hop 头
    const headers = new Headers(request.headers);
    headers.delete("host");
    headers.delete("content-length");
    headers.delete("connection");
    headers.delete("keep-alive");
    headers.delete("upgrade");
    headers.delete("te");

    // 添加转发信息，便于后端记录真实客户端 IP
    const clientIP = request.headers.get("CF-Connecting-IP") || "";
    headers.set("X-Forwarded-For", clientIP);
    headers.set("X-Forwarded-Host", url.host);
    headers.set("X-Forwarded-Proto", url.protocol.slice(0, -1));

    // 添加 CORS 头
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };

    // 处理 OPTIONS 预检请求
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: corsHeaders,
      });
    }

    // 转发请求到后端
    const response = await fetch(targetUrl, {
      method: request.method,
      headers,
      body: request.body,
    });

    // 复制响应头，保留原始响应头
    const responseHeaders = new Headers(response.headers);

    // 设置 CORS 头（覆盖可能存在的冲突头）
    responseHeaders.set("Access-Control-Allow-Origin", "*");
    responseHeaders.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    responseHeaders.set("Access-Control-Allow-Headers", "Content-Type, Authorization");

    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    const { request } = context;
    const url = new URL(request.url);

    console.error("API proxy error:", {
      method: request.method,
      path: `${url.pathname}${url.search}`,
      error: error instanceof Error ? error.message : String(error)
    });

    return new Response(
      JSON.stringify({ error: "Failed to proxy request to backend" }),
      {
        status: 502,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
};
