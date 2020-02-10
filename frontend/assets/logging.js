export function log(msg, data = {}) {
  const level = msg.match(/(^|\b)failed(\b|$)/)
    ? "error"
    : "debug";

  // XXX TODO include ...State
  console[level]({...data, msg: `frontend.${msg}`});
}
