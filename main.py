from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Simple VM Simulator API")

# --- Pydantic Models for Data Structure ---


class PageTableEntry(BaseModel):
    """Represents an entry in a process's Page Table."""
    vpn: int
    pfn: Optional[int] = None
    present: bool = False
    timestamp: int = 0  # Used for both FIFO (arrival) and LRU (last accessed)


class ProcessModel(BaseModel):
    """Represents a running process."""
    pid: str
    size: int
    page_table: List[PageTableEntry]
    color: Optional[str] = None


class Frame(BaseModel):
    """Represents a Physical Frame in Main Memory."""
    id: int
    pid: Optional[str] = None
    vpn: Optional[int] = None
    last_accessed: int = 0
    arrival_time: int = 0
    is_filled: bool = False


class InitConfig(BaseModel):
    frames: int = 8
    algorithm: str = "FIFO"


class AccessRequest(BaseModel):
    pid: str
    vpn: int


# --- Simulator Core Logic ---


class Simulator:
    """Manages the virtual memory state and replacement logic."""

    def __init__(self):
        self.frames: List[Frame] = []
        self.processes: Dict[str, ProcessModel] = {}
        self.frame_capacity = 0
        self.algorithm = "FIFO"
        self.clock = 0
        self.total_accesses = 0
        self.page_hits = 0
        self.page_faults = 0

    def init(self, frames: int, algorithm: str):
        """Initializes or resets the memory state."""
        self.frame_capacity = frames
        self.frames = [Frame(id=i) for i in range(frames)]
        self.algorithm = algorithm.upper()
        self.clock = 0
        self.total_accesses = 0
        self.page_hits = 0
        self.page_faults = 0
        self.processes = {}
        return self._state_snapshot()

    def create_process(self, pid: str, size: int, color: Optional[str] = None):
        """Creates a new process and its initial Page Table."""
        if pid in self.processes:
            raise ValueError("PID already exists")

        page_table = [PageTableEntry(vpn=i) for i in range(size)]
        self.processes[pid] = ProcessModel(
            pid=pid,
            size=size,
            page_table=page_table,
            color=color,
        )
        return self.processes[pid]

    def access(self, pid: str, vpn: int) -> Dict[str, Any]:
        """Simulates accessing a virtual page, handling hits and faults."""
        if pid not in self.processes:
            raise ValueError("Unknown pid")
        process = self.processes[pid]
        if vpn < 0 or vpn >= process.size:
            raise ValueError("VPN out of range for process size")

        self.clock += 1
        self.total_accesses += 1
        entry = process.page_table[vpn]
        event = {"time": self.clock, "pid": pid, "vpn": vpn}

        # Page Hit
        if entry.present and entry.pfn is not None:
            self.page_hits += 1
            pfn = entry.pfn
            entry.timestamp = self.clock  # LRU metric
            self.frames[pfn].last_accessed = self.clock
            event.update({"result": "hit", "pfn": pfn})
            return event

        # Page Fault
        self.page_faults += 1

        # find free frame
        free_index = next((i for i, fr in enumerate(self.frames) if not fr.is_filled), None)
        if free_index is not None:
            self._load_into_frame(pid, vpn, free_index)
            event.update({"result": "loaded", "pfn": free_index})
            return event

        # no free frame → replacement
        victim = self._select_victim()
        victim_frame = self.frames[victim]

        if victim_frame.pid and victim_frame.vpn is not None:
            vp_entry = self.processes[victim_frame.pid].page_table[victim_frame.vpn]
            vp_entry.present = False
            vp_entry.pfn = None
            vp_entry.timestamp = 0

        self._load_into_frame(pid, vpn, victim)
        event.update(
            {
                "result": "replaced",
                "pfn": victim,
                "evicted": {"pid": victim_frame.pid, "vpn": victim_frame.vpn},
            }
        )
        return event

    def _load_into_frame(self, pid: str, vpn: int, pfn: int):
        """Loads the given page into the specified physical frame."""
        frame = self.frames[pfn]
        frame.pid = pid
        frame.vpn = vpn
        frame.is_filled = True
        frame.last_accessed = self.clock

        if self.algorithm == "FIFO":
            frame.arrival_time = self.clock

        pe = self.processes[pid].page_table[vpn]
        pe.present = True
        pe.pfn = pfn
        pe.timestamp = frame.arrival_time if self.algorithm == "FIFO" else frame.last_accessed

    def _select_victim(self) -> int:
        """Selects the frame to be replaced based on the current algorithm."""
        if self.algorithm == "FIFO":
            key = lambda f: f.arrival_time
        elif self.algorithm == "LRU":
            key = lambda f: f.last_accessed
        else:
            key = lambda f: f.arrival_time

        victim_frame = min(self.frames, key=key)
        return victim_frame.id

    def _state_snapshot(self):
        """Returns a snapshot of the current simulator state for API responses."""
        return {
            "frames": [fr.dict() for fr in self.frames],
            "processes": {pid: proc.dict() for pid, proc in self.processes.items()},
            "metrics": {
                "clock": self.clock,
                "total_accesses": self.total_accesses,
                "page_hits": self.page_hits,
                "page_faults": self.page_faults,
                "hit_ratio": (self.page_hits / self.total_accesses)
                if self.total_accesses > 0
                else 0.0,
            },
            "algorithm": self.algorithm,
        }


sim = Simulator()

# ---------- HTTP API ----------


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serve the frontend HTML so you can open http://localhost:8000/."""
    index_path = Path(__file__).parent / "index.html"
    return index_path.read_text(encoding="utf-8")


@app.post("/api/init")
def api_init(config: InitConfig):
    """Initializes the simulation with frame count and replacement algorithm."""
    snapshot = sim.init(frames=config.frames, algorithm=config.algorithm)
    return JSONResponse(content={"status": "ok", "state": snapshot})


@app.post("/api/process")
def api_create_process(payload: Dict[str, Any]):
    """Creates a new virtual process."""
    pid = payload.get("pid")
    size = int(payload.get("size", 1))
    color = payload.get("color")
    try:
        proc = sim.create_process(pid, size, color)
        return JSONResponse(content={"status": "ok", "process": proc.dict()})
    except Exception as e:
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=400)


@app.post("/api/access")
def api_access(access: AccessRequest):
    """Accesses a virtual page and triggers page fault/replacement logic."""
    try:
        ev = sim.access(access.pid, access.vpn)
        return JSONResponse(
            content={"status": "ok", "event": ev, "state": sim._state_snapshot()}
        )
    except Exception as e:
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=400)


@app.get("/api/state")
def api_state():
    """Gets the current state of memory, processes, and metrics."""
    return JSONResponse(content={"status": "ok", "state": sim._state_snapshot()})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
