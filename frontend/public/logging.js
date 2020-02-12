import {State} from "./state.js";

export function log(msg, data = {}) {
  const level = msg.match(/(^|\b)failed(\b|$)/)
    ? "error"
    : "debug";

  console[level]({
    ...data,
    msg: `frontend.${msg}`,
    state: {...State},
  });
}

/* Function form of throw for use in expressions like:
 *
 *   x = fetchValue() || throw_("oh no");
 *
 * Not necessary, but I like this succinct form of control flow.  It will
 * introduce an extra frame on the callstack and thus some indirection during
 * tracing, but the full stack remains available of course.
 */
export function throw_(msg) {
  throw msg;
}
