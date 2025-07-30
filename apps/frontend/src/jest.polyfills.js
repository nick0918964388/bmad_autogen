// Jest polyfills for import.meta and other modern features

// Mock import.meta for Jest environment
Object.defineProperty(global, 'import', {
  value: {
    meta: {
      env: {
        VITE_BACKEND_API_URL: '/api',
        NODE_ENV: 'test',
        MODE: 'test'
      }
    }
  },
  writable: true
});

// Ensure import.meta is available globally
if (typeof globalThis !== 'undefined') {
  globalThis.import = global.import;
}