import type { NodeState } from "@/lib/api";
import { NodeCard } from "./NodeCard";

export function NodeCardGrid({ nodes }: { nodes: NodeState[] }) {
  return (
    <div className="grid grid-cols-2 gap-2 overflow-y-auto md:grid-cols-3 xl:grid-cols-4">
      {nodes.map((node) => <NodeCard key={node.id} node={node} />)}
    </div>
  );
}