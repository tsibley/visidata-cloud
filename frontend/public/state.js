/* Track simple key=value state in the query string of the URL.
 *
 * StateProxyHandler implements a Proxy "handler" to read/write state from the
 * document location and History API.  The upshot is that state accesses and
 * updates work just like normal property accesses and updates.
 *
 * Note that the "target", an empty Object, is a placeholder that's not used,
 * but is required by the Proxy interface.
 */

class StateProxyHandler {
  static get(_, key) {
    const query = this.query;

    if (key === Symbol.iterator)
      return query[Symbol.iterator].bind(query)
    else
      return query.get(key);
  }

  static has(_, key) {
    return this.query.has(key);
  }

  static deleteProperty(_, key) {
    const query = this.query;
    query.delete(key);
    this.query = query;
    return true;
  }

  static set(_, key, value) {
    const query = this.query;
    query.set(key, value);
    this.query = query;
    return true;
  }

  static ownKeys(_) {
    return [...this.query.keys()];
  }

  static getOwnPropertyDescriptor(_, key) {
    const query = this.query;

    if (key === Symbol.iterator)
      return {
        value: this.get(_, key),
        writable: false,
        configurable: false,
        enumerable: false,
      }

    else if (query.has(key))
      return {
        value: this.get(_, key),
        writable: true,
        configurable: true,
        enumerable: true,
      }

    else
      return undefined;
  }

  static get query() {
    return (new URL(document.location)).searchParams;
  }

  static set query(query) {
    history.replaceState(null, "", `?${query.toString()}`);
  }
}

export const State = new Proxy({}, StateProxyHandler);

window.State = State;
