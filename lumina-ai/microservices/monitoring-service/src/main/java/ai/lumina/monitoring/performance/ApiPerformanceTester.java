package ai.lumina.monitoring.performance;

import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Supplier;

/**
 * Utility for API performance testing and reporting.
 * This class provides methods to test API endpoints and generate performance reports.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ApiPerformanceTester {

    private final PerformanceTestingFramework performanceTestingFramework;

    /**
     * Test the performance of multiple API endpoints.
     *
     * @param endpoints The API endpoints to test
     * @param concurrentUsers The number of concurrent users
     * @param durationSeconds The duration of each test in seconds
     * @return The API test results
     */
    public ApiTestResult testApiEndpoints(List<ApiEndpoint> endpoints, int concurrentUsers, int durationSeconds) {
        log.info("Testing {} API endpoints with {} concurrent users for {} seconds each", 
                endpoints.size(), concurrentUsers, durationSeconds);
        
        List<EndpointTestResult> results = new ArrayList<>();
        
        for (ApiEndpoint endpoint : endpoints) {
            log.info("Testing endpoint: {} {}", endpoint.getMethod(), endpoint.getPath());
            
            PerformanceTestingFramework.LoadTestResult loadTestResult = 
                    performanceTestingFramework.runLoadTest(
                            endpoint.getMethod() + " " + endpoint.getPath(),
                            endpoint.getOperation(),
                            concurrentUsers,
                            durationSeconds);
            
            EndpointTestResult result = EndpointTestResult.builder()
                    .method(endpoint.getMethod())
                    .path(endpoint.getPath())
                    .description(endpoint.getDescription())
                    .concurrentUsers(concurrentUsers)
                    .durationSeconds(durationSeconds)
                    .totalRequests(loadTestResult.getTotalRequests())
                    .successCount(loadTestResult.getSuccessCount())
                    .errorCount(loadTestResult.getErrorCount())
                    .requestsPerSecond(loadTestResult.getRequestsPerSecond())
                    .minResponseTimeMs(loadTestResult.getMinResponseTimeMs())
                    .maxResponseTimeMs(loadTestResult.getMaxResponseTimeMs())
                    .avgResponseTimeMs(loadTestResult.getAvgResponseTimeMs())
                    .p50ResponseTimeMs(loadTestResult.getP50ResponseTimeMs())
                    .p90ResponseTimeMs(loadTestResult.getP90ResponseTimeMs())
                    .p95ResponseTimeMs(loadTestResult.getP95ResponseTimeMs())
                    .p99ResponseTimeMs(loadTestResult.getP99ResponseTimeMs())
                    .build();
            
            results.add(result);
            log.info("Endpoint test completed: {}", result);
        }
        
        ApiTestResult apiTestResult = ApiTestResult.builder()
                .testTime(LocalDateTime.now())
                .concurrentUsers(concurrentUsers)
                .durationSeconds(durationSeconds)
                .endpointResults(results)
                .build();
        
        log.info("API test completed: {}", apiTestResult);
        return apiTestResult;
    }
    
    /**
     * Compare the performance of API endpoints across different versions or environments.
     *
     * @param baselineEndpoints The baseline API endpoints
     * @param comparisonEndpoints The comparison API endpoints
     * @param concurrentUsers The number of concurrent users
     * @param durationSeconds The duration of each test in seconds
     * @return The API comparison results
     */
    public ApiComparisonResult compareApiPerformance(
            List<ApiEndpoint> baselineEndpoints, 
            List<ApiEndpoint> comparisonEndpoints,
            int concurrentUsers, 
            int durationSeconds) {
        
        log.info("Comparing API performance between baseline and comparison endpoints");
        
        ApiTestResult baselineResults = testApiEndpoints(baselineEndpoints, concurrentUsers, durationSeconds);
        ApiTestResult comparisonResults = testApiEndpoints(comparisonEndpoints, concurrentUsers, durationSeconds);
        
        List<EndpointComparisonResult> endpointComparisons = new ArrayList<>();
        
        // Match endpoints by path and method
        Map<String, EndpointTestResult> baselineMap = new HashMap<>();
        for (EndpointTestResult result : baselineResults.getEndpointResults()) {
            String key = result.getMethod() + " " + result.getPath();
            baselineMap.put(key, result);
        }
        
        for (EndpointTestResult comparisonResult : comparisonResults.getEndpointResults()) {
            String key = comparisonResult.getMethod() + " " + comparisonResult.getPath();
            EndpointTestResult baselineResult = baselineMap.get(key);
            
            if (baselineResult != null) {
                double throughputDiffPercent = calculatePercentDifference(
                        comparisonResult.getRequestsPerSecond(), 
                        baselineResult.getRequestsPerSecond());
                
                double responseTimeDiffPercent = calculatePercentDifference(
                        comparisonResult.getAvgResponseTimeMs(), 
                        baselineResult.getAvgResponseTimeMs());
                
                EndpointComparisonResult comparison = EndpointComparisonResult.builder()
                        .method(comparisonResult.getMethod())
                        .path(comparisonResult.getPath())
                        .description(comparisonResult.getDescription())
                        .baselineThroughput(baselineResult.getRequestsPerSecond())
                        .comparisonThroughput(comparisonResult.getRequestsPerSecond())
                        .throughputDiffPercent(throughputDiffPercent)
                        .baselineAvgResponseTimeMs(baselineResult.getAvgResponseTimeMs())
                        .comparisonAvgResponseTimeMs(comparisonResult.getAvgResponseTimeMs())
                        .responseTimeDiffPercent(responseTimeDiffPercent)
                        .baselineP95ResponseTimeMs(baselineResult.getP95ResponseTimeMs())
                        .comparisonP95ResponseTimeMs(comparisonResult.getP95ResponseTimeMs())
                        .baselineErrorRate(calculateErrorRate(baselineResult))
                        .comparisonErrorRate(calculateErrorRate(comparisonResult))
                        .build();
                
                endpointComparisons.add(comparison);
            }
        }
        
        ApiComparisonResult comparisonResult = ApiComparisonResult.builder()
                .testTime(LocalDateTime.now())
                .concurrentUsers(concurrentUsers)
                .durationSeconds(durationSeconds)
                .endpointComparisons(endpointComparisons)
                .build();
        
        log.info("API comparison completed: {}", comparisonResult);
        return comparisonResult;
    }
    
    /**
     * Generate a performance report from API test results.
     *
     * @param result The API test results
     * @param reportFile The file to write the report to
     * @throws IOException If an error occurs writing the report
     */
    public void generatePerformanceReport(ApiTestResult result, String reportFile) throws IOException {
        log.info("Generating performance report to file: {}", reportFile);
        
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(reportFile))) {
            writer.write("# API Performance Test Report\n\n");
            writer.write("Test Time: " + result.getTestTime().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME) + "\n");
            writer.write("Concurrent Users: " + result.getConcurrentUsers() + "\n");
            writer.write("Test Duration: " + result.getDurationSeconds() + " seconds\n\n");
            
            writer.write("## Endpoint Results\n\n");
            writer.write("| Method | Path | Requests/sec | Avg Response Time (ms) | P95 Response Time (ms) | Error Rate |\n");
            writer.write("|--------|------|-------------|------------------------|------------------------|------------|\n");
            
            for (EndpointTestResult endpoint : result.getEndpointResults()) {
                writer.write(String.format("| %s | %s | %.2f | %.2f | %d | %.2f%% |\n",
                        endpoint.getMethod(),
                        endpoint.getPath(),
                        endpoint.getRequestsPerSecond(),
                        endpoint.getAvgResponseTimeMs(),
                        endpoint.getP95ResponseTimeMs(),
                        calculateErrorRate(endpoint)));
            }
            
            writer.write("\n## Detailed Results\n\n");
            
            for (EndpointTestResult endpoint : result.getEndpointResults()) {
                writer.write("### " + endpoint.getMethod() + " " + endpoint.getPath() + "\n\n");
                writer.write("Description: " + endpoint.getDescription() + "\n\n");
                writer.write("- Total Requests: " + endpoint.getTotalRequests() + "\n");
                writer.write("- Successful Requests: " + endpoint.getSuccessCount() + "\n");
                writer.write("- Failed Requests: " + endpoint.getErrorCount() + "\n");
                writer.write("- Requests per Second: " + String.format("%.2f", endpoint.getRequestsPerSecond()) + "\n");
                writer.write("- Min Response Time: " + endpoint.getMinResponseTimeMs() + " ms\n");
                writer.write("- Max Response Time: " + endpoint.getMaxResponseTimeMs() + " ms\n");
                writer.write("- Avg Response Time: " + String.format("%.2f", endpoint.getAvgResponseTimeMs()) + " ms\n");
                writer.write("- 50th Percentile: " + endpoint.getP50ResponseTimeMs() + " ms\n");
                writer.write("- 90th Percentile: " + endpoint.getP90ResponseTimeMs() + " ms\n");
                writer.write("- 95th Percentile: " + endpoint.getP95ResponseTimeMs() + " ms\n");
                writer.write("- 99th Percentile: " + endpoint.getP99ResponseTimeMs() + " ms\n\n");
            }
        }
        
        log.info("Performance report generated successfully");
    }
    
    /**
     * Calculate the error rate for an endpoint test result.
     *
     * @param result The endpoint test result
     * @return The error rate as a percentage
     */
    private double calculateErrorRate(EndpointTestResult result) {
        if (result.getTotalRequests() == 0) {
            return 0.0;
        }
        return (double) result.getErrorCount() / result.getTotalRequests() * 100;
    }
    
    /**
     * Calculate the percent difference between two values.
     *
     * @param current The current value
     * @param baseline The baseline value
     * @return The percent difference
     */
    private double calculatePercentDifference(double current, double baseline) {
        if (baseline == 0) {
            return current == 0 ? 0 : 100;
        }
        return ((current - baseline) / baseline) * 100;
    }
    
    /**
     * Data class for API endpoint.
     */
    @Data
    @Builder
    public static class ApiEndpoint {
        private String method;
        private String path;
        private String description;
        private Supplier<Object> operation;
    }
    
    /**
     * Data class for API test results.
     */
    @Data
    @Builder
    public static class ApiTestResult {
        private LocalDateTime testTime;
        private int concurrentUsers;
        private int durationSeconds;
        private List<EndpointTestResult> endpointResults;
    }
    
    /**
     * Data class for endpoint test results.
     */
    @Data
    @Builder
    public static class EndpointTestResult {
        private String method;
        private String path;
        private String description;
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
     * Data class for API comparison results.
     */
    @Data
    @Builder
    public static class ApiComparisonResult {
        private LocalDateTime testTime;
        private int concurrentUsers;
        private int durationSeconds;
        private List<EndpointComparisonResult> endpointComparisons;
    }
    
    /**
     * Data class for endpoint comparison results.
     */
    @Data
    @Builder
    public static class EndpointComparisonResult {
        private String method;
        private String path;
        private String description;
        private double baselineThroughput;
        private double comparisonThroughput;
        private double throughputDiffPercent;
        private double baselineAvgResponseTimeMs;
        private double comparisonAvgResponseTimeMs;
        private double responseTimeDiffPercent;
        private long baselineP95ResponseTimeMs;
        private long comparisonP95ResponseTimeMs;
        private double baselineErrorRate;
        private double comparisonErrorRate;
    }
}
