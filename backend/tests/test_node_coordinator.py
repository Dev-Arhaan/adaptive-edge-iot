from app.services.node_coordinator import create_default_virtual_forest


def test_forest_steps_without_error():
    forest = create_default_virtual_forest(node_count=20, seed=1)
    for tick in range(1, 11):
        forest.step(current_tick=tick)


def test_forest_is_reproducible_given_seed():
    forest_a = create_default_virtual_forest(node_count=20, seed=5)
    forest_b = create_default_virtual_forest(node_count=20, seed=5)
    for tick in range(1, 6):
        forest_a.step(current_tick=tick)
        forest_b.step(current_tick=tick)

    batteries_a = [n.battery for n in sorted(forest_a.all_nodes(), key=lambda n: n.id)]
    batteries_b = [n.battery for n in sorted(forest_b.all_nodes(), key=lambda n: n.id)]
    assert batteries_a == batteries_b
    
def test_forest_produces_scheduling_history_over_time():
    forest = create_default_virtual_forest(node_count=15, seed=2)
    for tick in range(1, 15):
        forest.step(current_tick=tick)

    assert len(forest.scheduling_history().all_decisions()) > 0