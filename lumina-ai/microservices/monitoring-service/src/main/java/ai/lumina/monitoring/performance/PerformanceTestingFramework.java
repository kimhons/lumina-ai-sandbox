package ai.lumina.monitoring.performance;

import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

/**
 * Framework for performance testing and load simulation.
 * This class provides utilities for load testing, stress testing, and benchmarking.
 */
@Component
@Slf4j
public class PerformanceTestingFramework {

    /**
     * Run a load test with the specified parameters.
     *
     * @param testName The name of the test
     * @param operation The operation to test
     * @param concurrentUsers The number of concurrent users
     * @param durationSeconds The duration of the test in seconds
     * @return The load test results
     */
    public LoadTestResult runLoadTest(String testName, Supplier<Object> operation, int concurrentUsers, int durationSeconds) {
        log.info("Starting load test: {} with {} concurrent users for {} seconds", testName, concurrentUsers, durationSeconds);
        
        ExecutorService executor = Executors.newFixedThreadPool(concurrentUsers);
        List<CompletableFuture<Void>> futures = new ArrayList<>();
        
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger errorCount = new AtomicInteger(0);
        List<Long> responseTimes = new ArrayList<>();
        
        Instant startTime = Instant.now();
        Instant endTime = startTime.plusSeconds(durationSeconds);
        
        // Start the load test
        for (int i = 0; i < concurrentUsers; i++) {
            futures.add(CompletableFuture.runAsync(() -> {
                while (Instant.now().isBefore(endTime)) {
                    Instant operationStart = Instant.now();
                    try {
                        operation.get();
                        successCount.incrementAndGet();
                    } catch (Exception e) {
                        errorCount.incrementAndGet();
                        log.error("Error during load test: {}", e.getMessage());
                    } finally {
                        long responseTime = Duration.between(operationStart, Instant.now()).toMillis();
                        synchronized (responseTimes) {
                            responseTimes.add(responseTime);
                        }
                    }
                }
            }, executor));
        }
        
        // Wait for all futures to complete
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        executor.shutdown();
        
        // Calculate results
        Instant actualEndTime = Instant.now();
        long totalDurationMs = Duration.between(startTime, actualEndTime).toMillis();
        int totalRequests = successCount.get() + errorCount.get();
        double requestsPerSecond = totalRequests / (totalDurationMs / 1000.0);
        
        // Calculate response time statistics
        long[] sortedResponseTimes = responseTimes.stream().mapToLong(Long::longValue).sorted().toArray();
        long minResponseTime = sortedResponseTimes.length > 0 ? sortedResponseTimes[0] : 0;
        long maxResponseTime = sortedResponseTimes.length > 0 ? sortedResponseTimes[sortedResponseTimes.length - 1] : 0;
        
        double avgResponseTime = responseTimes.stream().mapToLong(Long::longValue).average().orElse(0);
        
        long p50ResponseTime = calculatePercentile(sortedResponseTimes, 50);
        long p90ResponseTime = calculatePercentile(sortedResponseTimes, 90);
        long p95ResponseTime = calculatePercentile(sortedResponseTimes, 95);
        long p99ResponseTime = calculatePercentile(sortedResponseTimes, 99);
        
        LoadTestResult result = LoadTestResult.builder()
                .testName(testName)
                .concurrentUsers(concurrentUsers)
                .durationSeconds(durationSeconds)
                .totalRequests(totalRequests)
                .successCount(successCount.get())
                .errorCount(errorCount.get())
                .requestsPerSecond(requestsPerSecond)
                .minResponseTimeMs(minResponseTime)
                .maxResponseTimeMs(maxResponseTime)
                .avgResponseTimeMs(avgResponseTime)
                .p50ResponseTimeMs(p50ResponseTime)
                .p90ResponseTimeMs(p90ResponseTime)
                .p95ResponseTimeMs(p95ResponseTime)
                .p99ResponseTimeMs(p99ResponseTime)
                .build();
        
        log.info("Load test completed: {}", result);
        return result;
    }
    
    /**
     * Run a stress test with increasing load until failure or max users reached.
     *
     * @param testName The name of the test
     * @param operation The operation to test
     * @param initialUsers The initial number of users
     * @param maxUsers The maximum number of users
     * @param stepSize The number of users to add in each step
     * @param stepDurationSeconds The duration of each step in seconds
     * @param targetSuccessRate The target success rate (0-1)
     * @return The stress test results
     */
    public StressTestResult runStressTest(String testName, Supplier<Object> operation, 
                                         int initialUsers, int maxUsers, int stepSize, 
                                         int stepDurationSeconds, double targetSuccessRate) {
        log.info("Starting stress test: {} with initial users: {}, max users: {}", testName, initialUsers, maxUsers);
        
        List<LoadTestResult> stepResults = new ArrayList<>();
        int breakpointUsers = 0;
        boolean targetReached = false;
        
        for (int users = initialUsers; users <= maxUsers; users += stepSize) {
            LoadTestResult result = runLoadTest(testName + " - Step " + users, operation, users, stepDurationSeconds);
            stepResults.add(result);
            
            double successRate = (double) result.getSuccessCount() / result.getTotalRequests();
            if (successRate < targetSuccessRate && !targetReached) {
                breakpointUsers = users;
                targetReached = true;
                log.info("Stress test breakpoint reached at {} users with success rate: {}", users, successRate);
            }
            
            if (targetReached) {
                // Run one more step to confirm the breakpoint
                if (users == breakpointUsers) {
                    continue;
                } else {
                    break;
                }
            }
        }
        
        if (!targetReached) {
            log.info("Stress test completed without reaching breakpoint. Max users: {}", maxUsers);
            breakpointUsers = maxUsers;
        }
        
        StressTestResult result = StressTestResult.builder()
                .testName(testName)
                .initialUsers(initialUsers)
                .maxUsers(maxUsers)
                .stepSize(stepSize)
                .stepDurationSeconds(stepDurationSeconds)
                .targetSuccessRate(targetSuccessRate)
                .breakpointUsers(breakpointUsers)
                .stepResults(stepResults)
                .build();
        
        log.info("Stress test completed: {}", result);
        return result;
    }
    
    /**
     * Run a benchmark test to compare different implementations.
     *
     * @param testName The name of the test
     * @param implementations The implementations to benchmark
     * @param iterations The number of iterations
     * @param warmupIterations The number of warmup iterations
     * @return The benchmark results
     */
    public BenchmarkResult runBenchmark(String testName, List<NamedImplementation> implementations, 
                                       int iterations, int warmupIterations) {
        log.info("Starting benchmark: {} with {} implementations, {} iterations", 
                testName, implementations.size(), iterations);
        
        List<ImplementationResult> results = new ArrayList<>();
        
        for (NamedImplementation implementation : implementations) {
            log.info("Benchmarking implementation: {}", implementation.getName());
            
            // Warmup
            for (int i = 0; i < warmupIterations; i++) {
                try {
                    implementation.getImplementation().get();
                } catch (Exception e) {
                    log.warn("Error during warmup: {}", e.getMessage());
                }
            }
            
            // Actual benchmark
            List<Long> executionTimes = new ArrayList<>();
            int successCount = 0;
            int errorCount = 0;
            
            for (int i = 0; i < iterations; i++) {
                Instant start = Instant.now();
                try {
                    implementation.getImplementation().get();
                    successCount++;
                } catch (Exception e) {
                    errorCount++;
                    log.error("Error during benchmark: {}", e.getMessage());
                } finally {
                    long executionTime = Duration.between(start, Instant.now()).toMillis();
                    executionTimes.add(executionTime);
                }
            }
            
            // Calculate statistics
            long[] sortedTimes = executionTimes.stream().mapToLong(Long::longValue).sorted().toArray();
            long minTime = sortedTimes.length > 0 ? sortedTimes[0] : 0;
            long maxTime = sortedTimes.length > 0 ? sortedTimes[sortedTimes.length - 1] : 0;
            double avgTime = executionTimes.stream().mapToLong(Long::longValue).average().orElse(0);
            
            ImplementationResult result = ImplementationResult.builder()
                    .implementationName(implementation.getName())
                    .iterations(iterations)
                    .successCount(successCount)
                    .errorCount(errorCount)
                    .minExecutionTimeMs(minTime)
                    .maxExecutionTimeMs(maxTime)
                    .avgExecutionTimeMs(avgTime)
                    .build();
            
            results.add(result);
            log.info("Benchmark for implementation {} completed: {}", implementation.getName(), result);
        }
        
        BenchmarkResult benchmarkResult = BenchmarkResult.builder()
                .testName(testName)
                .iterations(iterations)
                .warmupIterations(warmupIterations)
                .implementationResults(results)
                .build();
        
        log.info("Benchmark completed: {}", benchmarkResult);
        return benchmarkResult;
    }
    
    /**
     * Calculate the percentile value from sorted data.
     *
     * @param sortedData The sorted data
     * @param percentile The percentile to calculate (0-100)
     * @return The percentile value
     */
    private long calculatePercentile(long[] sortedData, int percentile) {
        if (sortedData.length == 0) {
            return 0;
        }
        
        int index = (int) Math.ceil(percentile / 100.0 * sortedData.length) - 1;
        index = Math.max(0, Math.min(sortedData.length - 1, index));
        return sortedData[index];
    }
    
    /**
     * Data class for load test results.
     */
    @Data
    @Builder
    public static class LoadTestResult {
        private String testName;
        private int concurrentUsers;
        private int durationSeconds;
        private int totalRequests;
        private int successCount;
        private int errorCount;
        private double requestsPerSecond;
        private long minResponseTimeMs;
        private long maxResponseTimeMs;
        private double avgResponseTimeMs;
        private long p50ResponseTimeMs;
        private long p90ResponseTimeMs;
        private long p95ResponseTimeMs;
        private long p99ResponseTimeMs;
    }
    
    /**
     * Data class for stress test results.
     */
    @Data
    @Builder
    public static class StressTestResult {
        private String testName;
        private int initialUsers;
        private int maxUsers;
        private int stepSize;
        private int stepDurationSeconds;
        private double targetSuccessRate;
        private int breakpointUsers;
        private List<LoadTestResult> stepResults;
    }
    
    /**
     * Data class for benchmark results.
     */
    @Data
    @Builder
    public static class BenchmarkResult {
        private String testName;
        private int iterations;
        private int warmupIterations;
        private List<ImplementationResult> implementationResults;
    }
    
    /**
     * Data class for implementation results in a benchmark.
     */
    @Data
    @Builder
    public static class ImplementationResult {
        private String implementationName;
        private int iterations;
        private int successCount;
        private int errorCount;
        private long minExecutionTimeMs;
        private long maxExecutionTimeMs;
        private double avgExecutionTimeMs;
    }
    
    /**
     * Data class for a named implementation in a benchmark.
     */
    @Data
    @Builder
    public static class NamedImplementation {
        private String name;
        private Supplier<Object> implementation;
    }
}
