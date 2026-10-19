import json, logging, time, uuid
import anthropic
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

MODEL = "claude-sonnet-5-5"
log = logging.getLogger("app")
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI(title="Instrument assistant")
client = anthropic.AsyncAnthropic(max_retries=3, timeout=60)

class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask(req: AskRequest):
    t0 = time.perf_counter()
    r = await client.messages.create(model=MODEL, max_tokens=800,
                                     messages=[{"role": "user", "content": req.question}])
    log.info(json.dumps({"event": "ask", "latency_s": round(time.perf_counter() - t0, 3),
                         "in": r.usage.input_tokens, "out": r.usage.output_tokens}))
    return {"answer": r.content[0].text}

@app.post("/ask/stream")
async def ask_stream(req: AskRequest, request: Request):
    request_id = str(uuid.uuid4())

    async def events():
        t0, first = time.perf_counter(), None
        try:
            async with client.messages.stream(model=MODEL, max_tokens=800,
                                              messages=[{"role": "user", "content": req.question}]) as stream:
                async for text in stream.text_stream:
                    if await request.is_disconnected():          # user left: stop generating and paying
                        return
                    first = first or time.perf_counter()
                    yield f"data: {json.dumps({'text': text})}\n\n"   # server-sent events format
                final = await stream.get_final_message()
            yield f"data: {json.dumps({'done': True})}\n\n"
            log.info(json.dumps({"event": "ask_stream", "id": request_id,
                                 "ttft_s": round((first or time.perf_counter()) - t0, 3),
                                 "total_s": round(time.perf_counter() - t0, 3),
                                 "in": final.usage.input_tokens, "out": final.usage.output_tokens}))
        except anthropic.APIError as e:
            log.error(json.dumps({"event": "upstream_error", "id": request_id, "error": repr(e)}))
            yield f"data: {json.dumps({'error': 'The model service is busy. Please try again.'})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
