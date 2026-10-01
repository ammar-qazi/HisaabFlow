/**
 * Development only (npm start / make dev): forward /api to the backend on
 * :8000 so the browser sees a single origin, as it does in Docker.
 * Used instead of package.json "proxy", which breaks CRA 5's dev server on
 * machines without a LAN address.
 */
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function setupProxy(app) {
  app.use('/api', createProxyMiddleware({ target: 'http://127.0.0.1:8000', changeOrigin: true }));
};
