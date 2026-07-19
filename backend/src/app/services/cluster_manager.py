import math

from app.domain.cluster import Cluster
from app.domain.enums import NodeHealth
from app.domain.node import Node


class _UnionFind:
    def __init__(self, ids: list[str]):
        self._parent = {i: i for i in ids}

    def find(self, i: str) -> str:
        while self._parent[i] != i:
            self._parent[i] = self._parent[self._parent[i]]
            i = self._parent[i]
        return i

    def union(self, a: str, b: str) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self._parent[root_b] = root_a


class ClusterManager:
    """Proximity-based clustering in the spirit of the original DTC
    protocol's communication-range clusters, reworked to be simulation-
    friendly: two nodes are directly connected if within
    communication_radius, and clusters are the resulting connected
    components — closer to how a real range-based protocol forms groups
    than a centrally-computed k-means partition would be.

    O(n^2) pairwise distance check, deliberately: simple and deterministic,
    fine for hundreds of nodes. Swap for a spatial index if experiments
    move to thousands — not worth building speculatively now.

    Nodes are assumed stationary, so form_clusters runs once at setup.
    reelect_head_if_needed handles the one thing that changes at runtime:
    a cluster head dying.
    """

    def __init__(self, communication_radius: float):
        self._communication_radius = communication_radius

    def form_clusters(self, nodes: list[Node]) -> list[Cluster]:
        if not nodes:
            return []

        uf = _UnionFind([n.id for n in nodes])
        for i, a in enumerate(nodes):
            for b in nodes[i + 1 :]:
                if math.hypot(a.x - b.x, a.y - b.y) <= self._communication_radius:
                    uf.union(a.id, b.id)

        groups: dict[str, list[Node]] = {}
        for node in nodes:
            groups.setdefault(uf.find(node.id), []).append(node)

        clusters = []
        for root, members in groups.items():
            cluster = self._build_cluster(root, members)
            for member in members:
                member.cluster_id = cluster.id
            clusters.append(cluster)
        return clusters

    def reelect_head_if_needed(self, cluster: Cluster, nodes_by_id: dict[str, Node]) -> None:
        """Promotes the healthiest, highest-battery surviving member when
        the current head is dead — the resilience behaviour a distributed
        protocol needs and a single fixed head wouldn't demonstrate."""
        current_head = nodes_by_id.get(cluster.head_node_id) if cluster.head_node_id else None
        if current_head and current_head.health != NodeHealth.DEAD:
            return

        survivors = [
            nodes_by_id[nid] for nid in cluster.node_ids if nodes_by_id[nid].health != NodeHealth.DEAD
        ]
        cluster.head_node_id = max(survivors, key=lambda n: n.battery).id if survivors else None

    def _build_cluster(self, cluster_id: str, members: list[Node]) -> Cluster:
        center_x = sum(n.x for n in members) / len(members)
        center_y = sum(n.y for n in members) / len(members)
        head = min(members, key=lambda n: math.hypot(n.x - center_x, n.y - center_y))
        return Cluster(
            id=f"cluster-{cluster_id}",
            center_x=center_x,
            center_y=center_y,
            node_ids=[n.id for n in members],
            head_node_id=head.id,
        )