from mcp.server.fastmcp import FastMCP

mcp = FastMCP("instrument-fleet")

FLEET = {
    "P-117": {"site": "coastal", "status": "offline", "last_data": "2026-10-18T02:00Z", "firmware": "2.3"},
    "P-204": {"site": "urban", "status": "ok", "last_data": "2026-10-19T09:55Z", "firmware": "2.4"},
}

@mcp.tool()
def get_instrument_status(instrument_id: str) -> dict:
    """Current status of one instrument by id (format 'P-123'): site, status, last data time (UTC), firmware."""
    return FLEET.get(instrument_id, {"error": f"unknown id; known ids: {sorted(FLEET)}"})

@mcp.tool()
def list_instruments(status: str | None = None) -> list[str]:
    """List instrument ids, optionally only those with a given status ('ok', 'degraded', 'offline')."""
    return [i for i, v in FLEET.items() if status is None or v["status"] == status]

@mcp.resource("fleet://firmware-notes")
def firmware_notes() -> str:
    """Release notes for instrument firmware versions."""
    return "2.4: fixes overnight logging stall on cellular modems. 2.3: adds GPS time sync."

if __name__ == "__main__":
    mcp.run()          # speaks MCP over stdin/stdout by default
