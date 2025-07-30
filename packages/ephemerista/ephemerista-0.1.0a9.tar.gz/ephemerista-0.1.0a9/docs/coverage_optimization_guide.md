# Coverage Analysis Optimization Guide

This guide explains how to use the benchmark and snapshot testing framework for optimizing coverage analysis performance while maintaining correctness.

## Overview

The coverage analysis optimization framework consists of:

1. **Benchmark Tests** (`tests/test_coverage_benchmarks.py`) - Performance measurement using pytest-benchmark
2. **Snapshot Tests** (`tests/test_coverage_snapshots.py`) - Functional correctness validation  
3. **Benchmark Script** (`scripts/run_coverage_benchmarks.py`) - Convenient benchmark runner with comparison features

## Usage

### Running Benchmarks with pytest-benchmark

The framework uses [pytest-benchmark](https://pytest-benchmark.readthedocs.io/) for professional-grade performance measurement with statistical analysis.

#### Basic Usage

```bash
# Run fast benchmarks only (recommended for development)
python scripts/run_coverage_benchmarks.py

# Run all benchmarks including slow ones (for comprehensive testing)
python scripts/run_coverage_benchmarks.py --include-slow

# Run with pytest directly
uv run pytest tests/test_coverage_benchmarks.py --benchmark-only -v
```

#### Creating Performance Baselines

```bash
# Save current performance as baseline
python scripts/run_coverage_benchmarks.py --save baseline

# Save optimized version for comparison
python scripts/run_coverage_benchmarks.py --save optimized

# Compare optimized vs baseline
python scripts/run_coverage_benchmarks.py --compare baseline --save optimized
```

#### Advanced Benchmark Features

```bash
# Group results by test type
python scripts/run_coverage_benchmarks.py --group-by group

# Generate JSON output for automated processing
python scripts/run_coverage_benchmarks.py --format json

# Run specific benchmark group only
uv run pytest tests/test_coverage_benchmarks.py -k "single_sat" --benchmark-only

# Generate performance histograms
uv run pytest tests/test_coverage_benchmarks.py --benchmark-only --benchmark-histogram
```

### Running Snapshot Tests

To verify functional correctness:

```bash
# Run snapshot tests
uv run pytest tests/test_coverage_snapshots.py -v

# Test deterministic behavior
uv run pytest tests/test_coverage_snapshots.py::TestCoverageSnapshots::test_snapshot_deterministic_results -v
```

## Benchmark Output and Analysis

### Understanding pytest-benchmark Output

pytest-benchmark provides comprehensive performance statistics:

- **Min/Max/Mean/StdDev**: Statistical measures of execution time
- **Median/IQR**: Robust statistics less affected by outliers  
- **OPS (Operations Per Second)**: Throughput measurement
- **Rounds**: Number of benchmark iterations performed

### Benchmark Files

Results are automatically saved in the `.benchmarks/` directory:

- `.benchmarks/*/benchmark.json` - Detailed JSON results for automation
- `.benchmarks/*/*.svg` - Performance histograms (with --benchmark-histogram)
- Comparison reports when using --compare option

## Benchmark Scenarios

The framework includes representative scenarios from the notebooks:

### Single Satellite Scenarios
- **Small AOI**: Single satellite over Europe-sized region (baseline test)
- **Large AOI**: Single satellite over half-earth region (stress test)

### Constellation Scenarios  
- **Walker Star**: 18 satellites in 6 planes over large AOI
- **Iridium Short**: 66 satellites, 2-hour duration
- **Iridium Long**: 66 satellites, 24-hour duration (most demanding)

## Performance Targets

The benchmark scenarios are designed to represent different scales of coverage analysis:

| Scenario | Test Type | Assets | Duration | Typical Use Case |
|----------|-----------|--------|----------|------------------|
| Single Sat Small AOI | Baseline | 1 | 24h | Development/testing |
| Single Sat Medium AOI | Standard | 1 | 12h | Regional analysis |
| Single Sat Large AOI | Stress | 1 | 6h | Global coverage |
| Small Walker Star | Standard | 6 | 6h | Small constellation |
| Walker Star | Advanced | 18 | 6h | Medium constellation |
| Iridium Short | Stress | 66 | 2h | Large constellation (short) |
| Iridium Long | Maximum | 66 | 12h | Large constellation (long) |

Benchmark durations are optimized for practical testing while maintaining representativeness.

## Optimization Workflow

### 1. Establish Baseline
```bash
# Create initial performance baseline
python scripts/run_coverage_benchmarks.py --save baseline

# Run snapshot tests to capture expected results
uv run pytest tests/test_coverage_snapshots.py -v
```

### 2. Implement Optimizations
- Focus on bottlenecks identified in profiling
- Preserve public API compatibility
- Maintain deterministic behavior

### 3. Validate Changes
```bash
# Verify functional correctness
uv run pytest tests/test_coverage_snapshots.py -v

# Measure performance improvement with comparison  
python scripts/run_coverage_benchmarks.py --save optimized --compare baseline

# Check that existing tests still pass
just test
```

### 4. Analyze Results
```bash
# Review benchmark comparison output
# Look for statistically significant improvements
# Check for performance regressions in any scenarios

# Generate detailed analysis with histograms
python scripts/run_coverage_benchmarks.py --save final --compare baseline --format json
```

## Key Metrics

### Performance Metrics
- **Total execution time** - Primary optimization target
- **Memory usage** - Secondary consideration
- **Scaling behavior** - How performance changes with problem size

### Functional Metrics
- **Coverage percentages** - Must remain identical
- **Time gaps** - Must remain identical  
- **Revisit times** - Must remain identical
- **Result hash** - Quick deterministic check

## Optimization Areas

Based on the current implementation, potential optimization areas include:

1. **Interval Merging** - Currently using pandas DataFrames
2. **Ground Point Processing** - Nested loops over ground locations
3. **Polygon Statistics** - Sequential processing of polygons
4. **Data Structures** - List-heavy operations
5. **Time Conversions** - Repeated Time object creation

## Guidelines

### Do's
- ✅ Use benchmark tests to measure improvements
- ✅ Use snapshot tests to verify correctness
- ✅ Profile before optimizing to identify bottlenecks
- ✅ Preserve exact numerical results
- ✅ Maintain API compatibility

### Don'ts  
- ❌ Optimize without benchmarks
- ❌ Change results for performance gains
- ❌ Break existing functionality
- ❌ Assume performance improvements
- ❌ Skip validation tests

## Example Optimization Process

```python
# 1. Identify bottleneck through profiling
# 2. Create focused test case
def test_interval_merging_performance():
    intervals = generate_test_intervals(n=1000)
    
    start = time.perf_counter()
    result = _merge_time_intervals(intervals)
    duration = time.perf_counter() - start
    
    assert duration < 0.1  # Performance target
    return result

# 3. Implement optimization
def _merge_time_intervals_optimized(intervals):
    # New optimized implementation
    pass

# 4. Verify correctness
def test_merge_intervals_correctness():
    intervals = generate_test_intervals(n=100)
    
    old_result = _merge_time_intervals(intervals)
    new_result = _merge_time_intervals_optimized(intervals)
    
    assert_results_identical(old_result, new_result)

# 5. Measure improvement in full benchmarks
```

This framework ensures that optimizations provide measurable performance benefits while maintaining the correctness and reliability of coverage analysis results.