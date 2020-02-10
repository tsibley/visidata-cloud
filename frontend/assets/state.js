/* Track simple key=value state in the query string of the URL.
 *
 * StateProxyHandler implements a Proxy "handler" to read/write state from the
 * document location and History API.  The upshot is that state accesses and
 * updates work just like normal property accesses and updates.
 */

class StateProxyHandler {
  static get(_, key) {
    return this.query.get(key);
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

  static get query() {
    return (new URL(document.location)).searchParams;
  }

  static set query(query) {
    history.replaceState(null, "", `?${query.toString()}`);
  }
}

export const State = new Proxy(new Map(), StateProxyHandler);
