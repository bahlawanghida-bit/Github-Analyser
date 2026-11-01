// A tiny in-memory cache where every entry expires after a fixed time ("TTL" = time to live).
// It lives in the server's memory, so it's empty again whenever the server restarts.

export class TtlCache {
  // "#" makes a field PRIVATE: only code inside this class can read or change it
  #entries = new Map(); // key -> { value, expiresAt }
  #ttlMs;

  constructor(ttlMs) {
    this.#ttlMs = ttlMs;
  }

  /** The stored value, or undefined if there is none or it has expired. */
  get(key) {
    const entry = this.#entries.get(key);
    if (!entry) return undefined;
    if (Date.now() > entry.expiresAt) {
      this.#entries.delete(key); // too old: forget it so the next request fetches fresh data
      return undefined;
    }
    return entry.value;
  }

  /** Store a value; it expires ttlMs milliseconds from now. */
  set(key, value) {
    this.#entries.set(key, { value, expiresAt: Date.now() + this.#ttlMs });
  }

  /** Forget everything (later: an Admin "clear cache" button). */
  clear() {
    this.#entries.clear();
  }

  /** A "getter": read it like a property, cache.size, without parentheses. */
  get size() {
    return this.#entries.size;
  }
}
