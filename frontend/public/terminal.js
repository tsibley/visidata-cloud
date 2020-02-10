/* Grab these libraries off the global window object because they aren't built
 * to support browser-native import statements, just out-of-browser build
 * systems like Webpack.
 */
const XTerm = window.Terminal;
const AttachAddon = window.AttachAddon.AttachAddon;
const FitAddon = window.FitAddon.FitAddon;

import {debounce} from "./utils.js";
import {log} from "./logging.js";


const terminalOptions = {
  fontFamily: "'IBM Plex Mono', monospace",
};


export class Terminal extends EventTarget {
  xterm = new XTerm(terminalOptions);
  fitAddon = new FitAddon();

  async init(element) {
    log("terminal.init", {element});

    // XXX TODO: Is this a good idea? It might be a terrible idea.
    await document.fonts.ready;

    this.xterm.open(element);
    this.xterm.focus();

    /* Fit terminal to element now and after any future resize.
     */
    this.xterm.loadAddon(this.fitAddon);
    this.fitAddon.fit();

    window.addEventListener("resize",
      debounce(200, () => {
        log("window.resized");
        this.fitAddon.fit();
      })
    );

    /* VisiData doesn't emit title changes right now, but it'd be nice to make
     * that happen to reflect the current sheet.
     */
    this.xterm.onTitleChange(title => {
      log("title-changed", {title});
      document.title = title;
    });
  }

  attach(container) {
    log("terminal.attach", {container: container.id});

    /* Resize container's TTY to match the terminal's size now and after any
     * future resize.
     */
    container.resizeTty(this.xterm.cols, this.xterm.rows);

    this.xterm.onResize(({cols, rows}) => {
      log("terminal.resized", {cols, rows});
      container.resizeTty(cols, rows);
    });

    /* Attach to the container socket.
     */
    const socket = container.attachSocket();

    socket.addEventListener("close", close => {
      this.dispatchEvent(new CustomEvent("close", {detail:{close}}));
    });

    const attachAddon = new AttachAddon(socket);
    this.xterm.loadAddon(attachAddon);
  }

  write(...args) {
    return this.xterm.write(...args);
  }
}
