import "@testing-library/jest-dom/vitest";

class ResizeObserverMock {
  callback?: ResizeObserverCallback;

  constructor(callback?: ResizeObserverCallback) {
    this.callback = callback;
  }

  observe(target: Element) {
    this.callback?.(
      [
        {
          target,
          contentRect: target.getBoundingClientRect(),
        } as ResizeObserverEntry,
      ],
      this as unknown as ResizeObserver,
    );
  }
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverMock;

Object.defineProperty(HTMLElement.prototype, "offsetWidth", {
  configurable: true,
  value: 1024,
});

Object.defineProperty(HTMLElement.prototype, "offsetHeight", {
  configurable: true,
  value: 768,
});

HTMLElement.prototype.getBoundingClientRect = function () {
  return {
    x: 0,
    y: 0,
    width: 1024,
    height: 768,
    top: 0,
    right: 1024,
    bottom: 768,
    left: 0,
    toJSON: () => {},
  };
};
