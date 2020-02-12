import {log, throw_} from "./logging.js";

export class Container {
  constructor(id) {
    this.id = id;
  }

  static async create() {
    log("container.creating");

    const createResponse = await POST("containers/create");
    const createResult = await createResponse.json();

    log("container.created", {container: createResult.Id});

    return new Container(createResult.Id);
  }

  async start() {
    if (!this.id)
      throw "Container.start() called on object with no id";

    await POST(`containers/${this.id}/start`);
    log("container.started", {container: this.id});
  }

  async resizeTty(w, h) {
    if (!this.id)
      throw "Container.resizeTty() called on object with no id";

    await POST(`containers/${this.id}/resize?${queryString({w, h})}`);
    log("container.resized-tty", {container: this.id, cols: w, rows: h});
  }

  attachSocket() {
    const wsProtocol = new Map([["http:", "ws:"], ["https:", "wss:"]]);

    const url = new URL(`containers/${this.id}/attach/ws?logs=1&stream=1&stdin=1&stdout=1&stderr=1`, document.location);
    url.protocol = wsProtocol.get(url.protocol) || throw_(`document.location has unknown protocol: ${url.protocol}`);

    log("socket.opening", {container: this.id, url});
    const socket = new WebSocket(url);

    socket.addEventListener("close", close => {
      log("socket.closed", {container: this.id, code: close.code});
    });

    return socket;
  }
}

async function POST(url, options = {}) {
  const response = await fetch(url, {...options, method: "POST"});

  if (!response.ok) {
    log("request.failed", {response});
    throw `POST ${url} failed`;
  }

  return response;
}

function queryString(kv = {}) {
  return (new URLSearchParams(kv)).toString();
}
