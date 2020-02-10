import {Container} from "./container.js";
import {log} from "./logging.js";
import {State} from "./state.js";
import {Terminal} from "./terminal.js";

launch()
  .catch(error => log("launch.failed", {error}));

async function launch() {
  log("launch");

  const term = new Terminal();
  await term.init(document.getElementById("terminal"));
  term.write("ATM0DT17607067425\r\n");

  let container;

  if (State.container) {
    log("launch.existing", {container: State.container});
    container = new Container(State.container);
  } else {
    log("launch.new");
    container = await Container.create();
    await container.start();
  }

  State.container = container.id;

  term.addEventListener("close", close => {
    term.write("NO CARRIER\r\n");
    delete State.container;
  });

  term.attach(container);
}
