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

    // 构建后端请求 URL（后端地址已包含 /api 或不包含，直接拼接完整路径）
    // 前端请求 /api/xxx，后端期望接收 /api/xxx
    const targetUrl = `${backendUrl}${url.pathname}`;

    // 复制请求头，移除 hop-by-hop 头
    const headers = new Headers(request.headers);
    headers.delete("host");
    headers.delete("content-length");

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
      headers: {
        ...Object.fromEntries(headers),
      },
      body: request.method !== "GET" && request.method !== "HEAD" ? request.body : undefined,
    });

    // 复制响应头和状态码
    const responseHeaders = new Headers(response.headers);
    responseHeaders.set("Access-Control-Allow-Origin", "*");

    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("API proxy error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to proxy request to backend" }),
      {
        status: 502,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
};
