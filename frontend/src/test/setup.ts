import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';
import '@testing-library/jest-dom/vitest';

// @testing-library/react doesn't auto-register DOM cleanup unless it detects
// Jest's globals; register it explicitly so each test starts with a fresh DOM.
afterEach(() => {
  cleanup();
});

// jsdom doesn't implement matchMedia; framer-motion's `useReducedMotion` (used
// by several animated components under test) calls it during render.
if (!window.matchMedia) {
  window.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })) as unknown as typeof window.matchMedia;
}
