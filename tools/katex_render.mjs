// Reads a JSON array of {tex, display} from stdin and writes a JSON array of rendered HTML strings.
// Called by build.py; keep it dependency-free apart from KaTeX itself.
import katex from "katex";

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  const items = JSON.parse(input);
  const out = items.map(({ tex, display }) => {
    try {
      return { html: katex.renderToString(tex, { displayMode: display, throwOnError: true, output: "htmlAndMathml" }) };
    } catch (e) {
      return { error: String(e.message || e) };
    }
  });
  process.stdout.write(JSON.stringify(out));
});
