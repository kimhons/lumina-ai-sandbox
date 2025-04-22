package ai.lumina.monitoring.performance;

import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Utility for database performance testing and optimization.
 * This class provides methods to analyze and optimize database queries.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DatabasePerformanceTester {

    private final DataSource dataSource;
    private final JdbcTemplate jdbcTemplate;

    /**
     * Analyze a SQL query and provide performance metrics.
     *
     * @param query The SQL query to analyze
     * @param params The query parameters
     * @return The query analysis result
     */
    public QueryAnalysisResult analyzeQuery(String query, Object... params) {
        log.info("Analyzing query: {}", query);
        
        // Execute EXPLAIN ANALYZE
        String explainQuery = "EXPLAIN ANALYZE " + query;
        List<String> explainResults = new ArrayList<>();
        
        try {
            jdbcTemplate.query(explainQuery, rs -> {
                while (rs.next()) {
                    explainResults.add(rs.getString(1));
                }
            }, params);
        } catch (Exception e) {
            log.error("Error executing EXPLAIN ANALYZE: {}", e.getMessage());
        }
        
        // Execute the query and measure performance
        Instant start = Instant.now();
        long rowCount = 0;
        
        try {
            rowCount = jdbcTemplate.query(query, rs -> {
                long count = 0;
                while (rs.next()) {
                    count++;
                }
                return count;
            }, params);
        } catch (Exception e) {
            log.error("Error executing query: {}", e.getMessage());
        }
        
        long executionTimeMs = Duration.between(start, Instant.now()).toMillis();
        
        // Check for potential issues
        List<String> optimizationSuggestions = analyzeExplainResults(explainResults);
        
        QueryAnalysisResult result = QueryAnalysisResult.builder()
                .query(query)
                .executionTimeMs(executionTimeMs)
                .rowCount(rowCount)
                .explainResults(explainResults)
                .optimizationSuggestions(optimizationSuggestions)
                .build();
        
        log.info("Query analysis completed: {}", result);
        return result;
    }
    
    /**
     * Benchmark multiple query variations to find the most efficient one.
     *
     * @param queryVariations Map of query variations with their names
     * @param iterations Number of iterations for each query
     * @param params Query parameters
     * @return The benchmark results
     */
    public QueryBenchmarkResult benchmarkQueries(Map<String, String> queryVariations, int iterations, Object... params) {
        log.info("Benchmarking {} query variations with {} iterations each", queryVariations.size(), iterations);
        
        List<QueryVariationResult> results = new ArrayList<>();
        
        for (Map.Entry<String, String> entry : queryVariations.entrySet()) {
            String variationName = entry.getKey();
            String query = entry.getValue();
            
            log.info("Benchmarking query variation: {}", variationName);
            
            List<Long> executionTimes = new ArrayList<>();
            long totalRows = 0;
            
            for (int i = 0; i < iterations; i++) {
                Instant start = Instant.now();
                long rowCount = 0;
                
                try {
                    rowCount = jdbcTemplate.query(query, rs -> {
                        long count = 0;
                        while (rs.next()) {
                            count++;
                        }
                        return count;
                    }, params);
                    
                    totalRows += rowCount;
                } catch (Exception e) {
                    log.error("Error executing query variation {}: {}", variationName, e.getMessage());
                }
                
                long executionTimeMs = Duration.between(start, Instant.now()).toMillis();
                executionTimes.add(executionTimeMs);
            }
            
            // Calculate statistics
            long[] sortedTimes = executionTimes.stream().mapToLong(Long::longValue).sorted().toArray();
            long minTime = sortedTimes.length > 0 ? sortedTimes[0] : 0;
            long maxTime = sortedTimes.length > 0 ? sortedTimes[sortedTimes.length - 1] : 0;
            double avgTime = executionTimes.stream().mapToLong(Long::longValue).average().orElse(0);
            
            QueryVariationResult result = QueryVariationResult.builder()
                    .variationName(variationName)
                    .query(query)
                    .iterations(iterations)
                    .minExecutionTimeMs(minTime)
                    .maxExecutionTimeMs(maxTime)
                    .avgExecutionTimeMs(avgTime)
                    .avgRowCount(totalRows / iterations)
                    .build();
            
            results.add(result);
            log.info("Benchmark for query variation {} completed: {}", variationName, result);
        }
        
        // Find the best variation
        QueryVariationResult bestVariation = results.stream()
                .min((r1, r2) -> Double.compare(r1.getAvgExecutionTimeMs(), r2.getAvgExecutionTimeMs()))
                .orElse(null);
        
        QueryBenchmarkResult benchmarkResult = QueryBenchmarkResult.builder()
                .iterations(iterations)
                .variationResults(results)
                .bestVariation(bestVariation != null ? bestVariation.getVariationName() : null)
                .build();
        
        log.info("Query benchmark completed: {}", benchmarkResult);
        return benchmarkResult;
    }
    
    /**
     * Identify slow queries in the database.
     *
     * @param thresholdMs The threshold in milliseconds to consider a query slow
     * @param limit The maximum number of slow queries to return
     * @return The list of slow queries
     */
    public List<SlowQueryInfo> identifySlowQueries(long thresholdMs, int limit) {
        log.info("Identifying slow queries with threshold {}ms, limit {}", thresholdMs, limit);
        
        List<SlowQueryInfo> slowQueries = new ArrayList<>();
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                     "SELECT query, calls, total_time, mean_time, rows " +
                     "FROM pg_stat_statements " +
                     "WHERE mean_time > ? " +
                     "ORDER BY mean_time DESC " +
                     "LIMIT ?")) {
            
            stmt.setDouble(1, thresholdMs);
            stmt.setInt(2, limit);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    SlowQueryInfo info = SlowQueryInfo.builder()
                            .query(rs.getString("query"))
                            .calls(rs.getLong("calls"))
                            .totalTimeMs(rs.getDouble("total_time"))
                            .meanTimeMs(rs.getDouble("mean_time"))
                            .rows(rs.getLong("rows"))
                            .build();
                    
                    slowQueries.add(info);
                }
            }
        } catch (SQLException e) {
            log.error("Error identifying slow queries: {}", e.getMessage());
        }
        
        log.info("Identified {} slow queries", slowQueries.size());
        return slowQueries;
    }
    
    /**
     * Analyze EXPLAIN results and provide optimization suggestions.
     *
     * @param explainResults The EXPLAIN ANALYZE results
     * @return List of optimization suggestions
     */
    private List<String> analyzeExplainResults(List<String> explainResults) {
        List<String> suggestions = new ArrayList<>();
        
        for (String line : explainResults) {
            if (line.contains("Seq Scan") && !line.contains("ON")) {
                suggestions.add("Consider adding an index to avoid sequential scan: " + line);
            }
            
            if (line.contains("Hash Join") && line.contains("cost=")) {
                suggestions.add("Large hash join detected, consider optimizing join conditions: " + line);
            }
            
            if (line.contains("Sort") && line.contains("using disk")) {
                suggestions.add("Sort operation using disk, consider increasing work_mem: " + line);
            }
            
            if (line.contains("Nested Loop") && line.contains("rows=") && extractRowCount(line) > 1000) {
                suggestions.add("Large nested loop join, consider using a different join type: " + line);
            }
        }
        
        return suggestions;
    }
    
    /**
     * Extract row count from EXPLAIN ANALYZE result line.
     *
     * @param line The EXPLAIN ANALYZE result line
     * @return The extracted row count
     */
    private long extractRowCount(String line) {
        try {
            int rowsIndex = line.indexOf("rows=");
            if (rowsIndex >= 0) {
                int endIndex = line.indexOf(' ', rowsIndex + 5);
                if (endIndex < 0) {
                    endIndex = line.length();
                }
                String rowsStr = line.substring(rowsIndex + 5, endIndex);
                return Long.parseLong(rowsStr);
            }
        } catch (Exception e) {
            log.warn("Error extracting row count from line: {}", line);
        }
        return 0;
    }
    
    /**
     * Data class for query analysis results.
     */
    @Data
    @Builder
    public static class QueryAnalysisResult {
        private String query;
        private long executionTimeMs;
        private long rowCount;
        private List<String> explainResults;
        private List<String> optimizationSuggestions;
    }
    
    /**
     * Data class for query benchmark results.
     */
    @Data
    @Builder
    public static class QueryBenchmarkResult {
        private int iterations;
        private List<QueryVariationResult> variationResults;
        private String bestVariation;
    }
    
    /**
     * Data class for query variation results in a benchmark.
     */
    @Data
    @Builder
    public static class QueryVariationResult {
        private String variationName;
        private String query;
        private int iterations;
        private long minExecutionTimeMs;
        private long maxExecutionTimeMs;
        private double avgExecutionTimeMs;
        private long avgRowCount;
    }
    
    /**
     * Data class for slow query information.
     */
    @Data
    @Builder
    public static class SlowQueryInfo {
        private String query;
        private long calls;
        private double totalTimeMs;
        private double meanTimeMs;
        private long rows;
    }
}
