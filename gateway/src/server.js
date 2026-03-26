const express = require("express");
const morgan = require("morgan");
const jwt = require("jsonwebtoken");
const { createProxyMiddleware } = require("http-proxy-middleware");

const app = express();

const PORT = Number(process.env.PORT || 8080);
const SECRET_KEY = process.env.SECRET_KEY || "supersecretkey123";
const ALGORITHM = process.env.ALGORITHM || "HS256";

const serviceTargets = {
  "/api/users": process.env.USER_SERVICE_URL || "http://user-service:8000",
  "/api/bookings-service": process.env.BOOKING_SERVICE_URL || "http://booking-service:8002",
  "/api/events-service": process.env.EVENT_SERVICE_URL || "http://event-service:8001",
  "/api/activity-service": process.env.ACTIVITY_SERVICE_URL || "http://activity-service:8000"
};

const publicRoutes = new Set([
  "POST /api/users/register",
  "POST /api/users/login",
  "GET /health",
  "GET /api/gateway/health"
]);

app.disable("x-powered-by");
app.use(morgan("dev"));

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "gateway" });
});

app.get("/api/gateway/health", (_req, res) => {
  res.json({
    status: "ok",
    service: "gateway",
    routes: Object.keys(serviceTargets)
  });
});

function isPublicRoute(req) {
  return publicRoutes.has(`${req.method.toUpperCase()} ${req.path}`);
}

function authenticateRequest(req, res, next) {
  if (isPublicRoute(req)) {
    next();
    return;
  }

  const authorization = req.headers.authorization;
  if (!authorization) {
    res.status(401).json({ detail: "Missing Authorization header" });
    return;
  }

  const [scheme, token] = authorization.split(" ");
  if (scheme !== "Bearer" || !token) {
    res.status(401).json({ detail: "Authorization header must use Bearer token" });
    return;
  }

  try {
    const payload = jwt.verify(token, SECRET_KEY, { algorithms: [ALGORITHM] });
    req.user = payload;
    req.headers["x-authenticated-user-email"] = payload.email || "";
    req.headers["x-authenticated-user-role"] = payload.role || "";
    req.headers["x-authenticated-user-id"] = payload.user_id ? String(payload.user_id) : "";
    next();
  } catch (error) {
    res.status(401).json({ detail: "Could not validate credentials" });
  }
}

function resolveServiceTarget(pathname) {
  return Object.entries(serviceTargets).find(([prefix]) => pathname.startsWith(prefix));
}

app.use(authenticateRequest);

for (const [prefix, target] of Object.entries(serviceTargets)) {
  app.use(
    prefix,
    createProxyMiddleware({
      target,
      changeOrigin: true,
      xfwd: true,
      proxyTimeout: 30000,
      timeout: 30000,
      logLevel: "warn"
    })
  );
}

app.use((req, res) => {
  const serviceMatch = resolveServiceTarget(req.path);
  if (!serviceMatch) {
    res.status(404).json({
      detail: "No gateway route configured for this path"
    });
    return;
  }

  res.status(502).json({
    detail: `Gateway could not reach upstream service for prefix ${serviceMatch[0]}`
  });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Gateway listening on port ${PORT}`);
});
