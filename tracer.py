import time
import json
import os

class Tracer:
    def __init__(self, session_id="review_1720000000", repo="default/repo"):
        self.session_id = session_id
        self.repo = repo
        self.started_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.stages = {}
        self._active_stages = {}

    def start_stage(self, name):
        self._active_stages[name] = time.time()

    def end_stage(self, name, meta=None):
        if name in self._active_stages:
            duration = round(time.time() - self._active_stages[name], 2)
            self.stages[name] = {
                "duration": duration,
                "metadata": meta or {}
            }
            del self._active_stages[name]

    def get_bottlenecks(self):
        # Sort stages slowest to fastest
        return sorted(
            [{"stage": k, "duration": v["duration"]} for k, v in self.stages.items()],
            key=lambda x: x["duration"],
            reverse=True
        )

    def print_bottleneck_report(self):
        total_duration = sum(v["duration"] for v in self.stages.values())
        print("\nStage                          Duration  Share")
        print("─" * 45)
        for b in self.get_bottlenecks():
            share = (b['duration'] / total_duration * 100) if total_duration else 0
            bar = "█" * int(share / 5)
            print(f"{b['stage']:30} {b['duration']:6.2f}s  {share:5.1f}% {bar}")
        
        bottlenecks = self.get_bottlenecks()
        if bottlenecks:
            print(f"\n🐢 Biggest bottleneck: '{bottlenecks[0]['stage']}' ({bottlenecks[0]['duration']}s)")

    def save(self):
        os.makedirs("traces", exist_ok=True)
        report = {
            "session_id": self.session_id,
            "repo": self.repo,
            "started_at": self.started_at,
            "total_duration": round(sum(v["duration"] for v in self.stages.values()), 2),
            "stages": self.stages,
            "bottlenecks": self.get_bottlenecks()
        }
        filepath = f"traces/{self.session_id}.json"
        with open(filepath, "w") as f:
            json.dump(report, f, indent=4)
        return filepath