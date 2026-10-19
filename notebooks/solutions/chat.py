import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(max_retries=3)
MODEL = "claude-sonnet-5-5"
PRICE_IN, PRICE_OUT = 3.0, 15.0          # per million tokens: set to your provider's current prices
MAX_HISTORY_CHARS = 80_000                # about 20k tokens

system = "You are a friendly, precise tutor for an AI engineering course."
history: list[dict] = []
spent_in = spent_out = 0

def trim(history):
    while sum(len(m["content"]) for m in history) > MAX_HISTORY_CHARS and len(history) > 2:
        history.pop(0); history.pop(0)     # drop the oldest user/assistant pair
    return history

while True:
    try:
        user = input("\nyou> ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not user:
        continue
    if user == "/quit":
        break
    if user == "/reset":
        history.clear(); print("history cleared"); continue
    if user.startswith("/system "):
        system = user[len("/system "):]; print("system prompt updated"); continue

    history.append({"role": "user", "content": user})
    trim(history)
    print("bot> ", end="", flush=True)
    try:
        with client.messages.stream(model=MODEL, max_tokens=1000, system=system,
                                    messages=history) as stream:
            parts = []
            for piece in stream.text_stream:
                print(piece, end="", flush=True)
                parts.append(piece)
            final = stream.get_final_message()
        reply = "".join(parts)
    except anthropic.APIError as e:
        history.pop()                      # remove the unanswered user turn so history stays valid
        print(f"\n[request failed: {e.__class__.__name__}; your conversation is intact, try again]")
        continue
    history.append({"role": "assistant", "content": reply})
    spent_in += final.usage.input_tokens
    spent_out += final.usage.output_tokens
    cost = spent_in / 1e6 * PRICE_IN + spent_out / 1e6 * PRICE_OUT
    print(f"\n[{final.usage.input_tokens} in / {final.usage.output_tokens} out; session ≈ {cost:.4f} USD]")
