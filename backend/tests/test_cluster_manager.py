# tests/test_cluster_manager.py
from app.domain.enums import NodeHealth
from app.domain.node import Node
from app.services.cluster_manager import ClusterManager


def test_nearby_nodes_form_one_cluster():
    nodes = [
        Node(id="a", cluster_id="", x=0, y=0),
        Node(id="b", cluster_id="", x=10, y=0),
        Node(id="c", cluster_id="", x=500, y=500),
    ]
    clusters = ClusterManager(communication_radius=50).form_clusters(nodes)

    assert len(clusters) == 2
    assert nodes[0].cluster_id == nodes[1].cluster_id != nodes[2].cluster_id


def test_head_reelected_when_head_dies():
    nodes = [
        Node(id="a", cluster_id="", x=0, y=0, battery=80),
        Node(id="b", cluster_id="", x=5, y=0, battery=60),
    ]
    manager = ClusterManager(communication_radius=50)
    cluster = manager.form_clusters(nodes)[0]
    nodes_by_id = {n.id: n for n in nodes}

    nodes_by_id[cluster.head_node_id].health = NodeHealth.DEAD
    manager.reelect_head_if_needed(cluster, nodes_by_id)

    assert nodes_by_id[cluster.head_node_id].health != NodeHealth.DEAD