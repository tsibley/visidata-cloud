export function debounce(delay, f) {
  let timeout;

  return function() {
    const f_ = () => f.apply(this, arguments);

    if (timeout)
      clearTimeout(timeout);

    timeout = setTimeout(f_, delay);
  };
}
