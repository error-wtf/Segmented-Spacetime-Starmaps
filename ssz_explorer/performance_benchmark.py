#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Benchmark - Sprint Task 5

Test performance with different data sizes.
"""

import os
import sys
import time
import psutil
import numpy as np

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

print("="*70)
print("PERFORMANCE BENCHMARK - Task 5")
print("="*70)
print()

# Get current process for memory tracking
process = psutil.Process()

def format_time(seconds):
    """Format time in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    else:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"

def get_memory_mb():
    """Get current memory usage in MB."""
    return process.memory_info().rss / 1024 / 1024

def benchmark_data_loading(catalog, level, limit, use_real):
    """Benchmark data loading."""
    
    print(f"\n  Testing: {level} level ({limit} objects, real={use_real})")
    
    mem_before = get_memory_mb()
    start_time = time.time()
    
    try:
        from data_manager import DataManager
        
        dm = DataManager()
        data = dm.load_catalog(
            catalog=catalog,
            level=level,
            limit=limit,
            use_real_data=use_real
        )
        
        load_time = time.time() - start_time
        mem_after = get_memory_mb()
        mem_used = mem_after - mem_before
        
        # Get data info
        n_objects = len(data)
        is_real = data.attrs.get('real_data', False)
        source = data.attrs.get('data_source', 'unknown')
        
        # Calculate SSZ params time (if not already computed)
        if 'Xi' not in data.columns:
            ssz_start = time.time()
            data = dm._compute_ssz_parameters(data)
            ssz_time = time.time() - ssz_start
        else:
            ssz_time = 0
        
        print(f"    [OK] Loaded {n_objects} objects")
        print(f"    Source: {source} (real={is_real})")
        print(f"    Load time: {format_time(load_time)}")
        if ssz_time > 0:
            print(f"    SSZ time: {format_time(ssz_time)}")
        print(f"    Memory: +{mem_used:.1f} MB")
        print(f"    Time/object: {load_time/n_objects*1000:.2f} ms")
        
        return {
            'level': level,
            'n_objects': n_objects,
            'load_time': load_time,
            'ssz_time': ssz_time,
            'memory_mb': mem_used,
            'source': source,
            'is_real': is_real
        }
        
    except Exception as e:
        print(f"    [FAIL] Error: {e}")
        return None

def benchmark_ssz_calculation(n_objects_list):
    """Benchmark pure SSZ calculation speed."""
    
    print(f"\n  Testing SSZ calculation speed...")
    
    from data_manager import DataManager
    import pandas as pd
    
    dm = DataManager()
    
    for n in n_objects_list:
        # Generate simple test data
        data = pd.DataFrame({
            'mass_msun': np.random.uniform(0.5, 2.0, n),
            'distance_pc': np.random.uniform(100, 10000, n)
        })
        
        start_time = time.time()
        result = dm._compute_ssz_parameters(data)
        calc_time = time.time() - start_time
        
        print(f"    {n:6d} objects: {format_time(calc_time)} ({calc_time/n*1e6:.1f} µs/object)")

# Test 1: Synthetic Data Performance
print("[Test 1/5] Synthetic Data Loading")
print("-" * 70)

synthetic_tests = [
    ('preview', 1000),
    ('preview', 5000),
    ('preview', 10000),
]

synthetic_results = []
for level, limit in synthetic_tests:
    result = benchmark_data_loading('gaia', level, limit, use_real=False)
    if result:
        synthetic_results.append(result)

# Test 2: Real Data Performance (if available)
print("\n[Test 2/5] Real GAIA Data Loading")
print("-" * 70)

real_tests = [
    ('preview', 100),
    ('preview', 500),
    ('preview', 1000),
]

real_results = []
for level, limit in real_tests:
    result = benchmark_data_loading('gaia', level, limit, use_real=True)
    if result:
        real_results.append(result)

# Test 3: SSZ Calculation Speed
print("\n[Test 3/5] SSZ Calculation Performance")
print("-" * 70)

benchmark_ssz_calculation([100, 1000, 10000, 100000])

# Test 4: Cone Search Performance
print("\n[Test 4/5] Cone Search Performance")
print("-" * 70)

try:
    from data_manager import DataManager
    
    dm = DataManager()
    
    # Test different radii
    test_cases = [
        (266.4, -29.0, 0.1, 100),
        (266.4, -29.0, 0.5, 500),
        (266.4, -29.0, 1.0, 1000),
    ]
    
    for ra, dec, radius, max_src in test_cases:
        print(f"\n  Cone: RA={ra}, DEC={dec}, radius={radius} deg")
        
        start_time = time.time()
        data = dm.cone_search(ra, dec, radius, level='preview')
        query_time = time.time() - start_time
        
        print(f"    Found: {len(data)} objects")
        print(f"    Time: {format_time(query_time)}")
        
except Exception as e:
    print(f"  [SKIP] Cone search test failed: {e}")

# Test 5: Cache Performance
print("\n[Test 5/5] Cache Performance")
print("-" * 70)

print("\n  First load (no cache):")
start_time = time.time()
result1 = benchmark_data_loading('gaia', 'preview', 1000, use_real=False)
first_time = time.time() - start_time

print("\n  Second load (with cache):")
start_time = time.time()
result2 = benchmark_data_loading('gaia', 'preview', 1000, use_real=False)
cached_time = time.time() - start_time

if first_time > 0 and cached_time > 0:
    speedup = first_time / cached_time
    print(f"\n  Cache speedup: {speedup:.1f}x faster")

# Summary
print("\n" + "="*70)
print("PERFORMANCE SUMMARY")
print("="*70)

if synthetic_results:
    print("\nSynthetic Data:")
    for r in synthetic_results:
        print(f"  {r['n_objects']:6d} objects: {format_time(r['load_time'])} " +
              f"({r['memory_mb']:.1f} MB)")

if real_results:
    print("\nReal GAIA Data:")
    for r in real_results:
        if r['is_real']:
            print(f"  {r['n_objects']:6d} objects: {format_time(r['load_time'])} " +
                  f"({r['memory_mb']:.1f} MB)")

# Performance targets
print("\n" + "="*70)
print("TARGET VALIDATION")
print("="*70)

targets = {
    '1k stars': (1, 5),      # 1-5 seconds
    '10k stars': (5, 30),    # 5-30 seconds
    '100k stars': (30, 120)  # 30-120 seconds
}

print("\nTargets:")
for desc, (min_s, max_s) in targets.items():
    print(f"  {desc:20s} {format_time(min_s)} - {format_time(max_s)}")

# Check if we met targets
print("\nActual Performance:")
test_points = [
    (1000, synthetic_results),
    (10000, synthetic_results),
]

for target_n, results in test_points:
    matches = [r for r in results if r['n_objects'] == target_n]
    if matches:
        r = matches[0]
        target_range = targets.get(f'{target_n//1000}k stars')
        if target_range:
            min_s, max_s = target_range
            if r['load_time'] <= max_s:
                status = "[OK]"
            else:
                status = "[SLOW]"
            print(f"  {target_n:6d} objects: {format_time(r['load_time'])} {status}")

print()
print("="*70)
print("[OK] PERFORMANCE BENCHMARK COMPLETE")
print("="*70)
print()
