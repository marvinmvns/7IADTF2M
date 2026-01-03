import pytest
from src.genetic_algorithm.chromosome import Chromosome, DeliveryPoint, Vehicle

def test_chromosome_route_splitting():
    # 3 points, 2 vehicles with small capacity
    depot = DeliveryPoint(id=0, name="Depot", x=0, y=0)
    p1 = DeliveryPoint(id=1, name="P1", x=0.1, y=0.1, demand=60)
    p2 = DeliveryPoint(id=2, name="P2", x=0.2, y=0.2, demand=60)
    p3 = DeliveryPoint(id=3, name="P3", x=0.3, y=0.3, demand=20)
    
    delivery_points = [depot, p1, p2, p3]
    # Vehicles with capacity 100
    vehicles = [Vehicle(id=0, capacity=100), Vehicle(id=1, capacity=100)]
    
    # Genes: [1, 2, 3]
    # Expected: Route 1: [P1] (demand 60), Route 2: [P2, P3] (demand 60+20=80) 
    # Or similar depending on how splitting works (usually sequential until capacity reached)
    c = Chromosome(genes=[1, 2, 3], delivery_points=delivery_points, vehicles=vehicles)
    
    routes = c.get_routes()
    
    assert len(routes) <= len(vehicles)
    assert len(routes) >= 1
    
    # Verify all points are covered
    covered_points = []
    for r in routes:
        covered_points.extend([p.id for p in r.points])
    
    assert set(covered_points) == {1, 2, 3}
    
    # Verify capacity constraint
    for r in routes:
        assert r.total_demand <= r.vehicle.capacity

def test_chromosome_speed_consistency():
    # Test if speed_factors are correctly used in routes
    v1 = Vehicle(id=0, speed=10.0)
    v2 = Vehicle(id=1, speed=20.0)
    
    c = Chromosome(genes=[1, 2], vehicles=[v1, v2], speed_factors=[1.5, 0.5])
    
    # In my fitness implementation, I used speed_factors to adjust travel time
    # Let's see if the speed_factors are preserved in the chromosome
    assert c.speed_factors == [1.5, 0.5]
