import type { NodeEvent, SchedulingDecision } from "@/lib/api";

type LogEntry = { tick: number; label: string; detail: string; tone: "warn" | "danger" };

export function EventLog({ events, decisions }: { events: NodeEvent[]; decisions: SchedulingDecision[] }) {
  const emergencyEntries: LogEntry[] = decisions
    .filter((d) => d.triggered_by === "emergency_broadcast")
    .map((d) => ({ tick: d.tick, label: `Emergency broadcast — ${d.node_id}`, detail: d.reason, tone: "danger" }));

  const nodeEntries: LogEntry[] = events.map((e) => ({
    tick: e.tick, label: e.event_type === "died" ? `${e.node_id} went offline` : `${e.node_id} degraded`,
    detail: e.detail, tone: e.event_type === "died" ? "danger" : "warn",
  }));

  const merged = [...emergencyEntries, ...nodeEntries].sort((a, b) => b.tick - a.tick).slice(0, 50);
  const toneColor: Record<LogEntry["tone"], string> = { danger: "#E4572E", warn: "#D9A441" };

  return (
    <div className="rounded border border-panel-border bg-panel p-3">
      <h3 className="mb-2 font-display text-sm text-bone">Event log</h3>
      <ul className="flex max-h-[70vh] flex-col gap-1 overflow-y-auto font-data text-xs">
        {merged.length === 0 && <li className="text-muted">No events yet.</li>}
        {merged.map((entry, index) => (
          <li key={index} className="flex flex-wrap items-baseline gap-2 border-b border-panel-border/50 py-1">
            <span className="text-muted">t={entry.tick}</span>
            <span style={{ color: toneColor[entry.tone] }}>{entry.label}</span>
            <span className="text-muted">— {entry.detail}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}