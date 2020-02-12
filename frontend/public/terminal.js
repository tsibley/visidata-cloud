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

/* This should stay synced with the faces requested in the stylesheet
 * hot-loaded from Google Fonts.  See Terminal.loadFonts() below for more
 * details.
 */
const fontFaces = [
  "400 1em 'IBM Plex Mono'",
  "700 1em 'IBM Plex Mono'",
  "400 italic 1em 'IBM Plex Mono'",
  "700 italic 1em 'IBM Plex Mono'",
];


export class Terminal extends EventTarget {
  xterm = new XTerm(terminalOptions);
  fitAddon = new FitAddon();

  async init(element) {
    log("terminal.init", {element});

    await this.loadFonts();

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

  async loadFonts() {
    /* XXX TODO: Is this a good idea? It might be a terrible idea.
     *
     * The problem is that the webfonts we use *must* be actually loaded, not
     * just configured with CSS, *before* we call xterm.open(). Otherwise,
     * xterm will initialize its internal font handling and character sizing
     * with the fallback font, only to then be fubar when the browser swaps in
     * the webfont some moments later.
     *
     * Normally browsers wait to actually load the font until it is first used
     * in a DOM element, but that doesn't work here because xterm draws
     * characters onto a bitmap canvas instead of using actual DOM elements.
     */
    await Promise.all(fontFaces.map(face => document.fonts.load(face)));
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
