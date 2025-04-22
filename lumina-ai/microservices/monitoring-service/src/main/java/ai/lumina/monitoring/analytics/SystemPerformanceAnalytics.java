package ai.lumina.monitoring.analytics;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import ai.lumina.monitoring.model.Metric;
import ai.lumina.monitoring.repository.MetricRepository;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for system performance analytics.
 * This class provides methods to analyze system performance metrics and identify trends.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class SystemPerformanceAnalytics {

    private final MetricRepository metricRepository;

    /**
     * Analyze system performance over a time period.
     *
     * @param metricName The name of the metric to analyze
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @param interval The interval for aggregation in minutes
     * @return The performance analysis results
     */
    public PerformanceAnalysisResult analyzePerformance(String metricName, Instant startTime, Instant endTime, int interval) {
        log.info("Analyzing performance for metric {} from {} to {} with interval {} minutes", 
                metricName, startTime, endTime, interval);
        
        List<Metric> metrics = metricRepository.findByNameAndTimestampBetween(metricName, startTime, endTime);
        
        // Group metrics by interval
        Map<Instant, List<Metric>> metricsByInterval = groupMetricsByInterval(metrics, interval);
        
        // Calculate statistics for each interval
        List<IntervalStats> intervalStats = new ArrayList<>();
        
        for (Map.Entry<Instant, List<Metric>> entry : metricsByInterval.entrySet()) {
            Instant intervalStart = entry.getKey();
            List<Metric> intervalMetrics = entry.getValue();
            
            double min = intervalMetrics.stream().mapToDouble(Metric::getValue).min().orElse(0);
            double max = intervalMetrics.stream().mapToDouble(Metric::getValue).max().orElse(0);
            double avg = intervalMetrics.stream().mapToDouble(Metric::getValue).average().orElse(0);
            double median = calculateMedian(intervalMetrics);
            double p95 = calculatePercentile(intervalMetrics, 95);
            
            IntervalStats stats = IntervalStats.builder()
                    .intervalStart(intervalStart)
                    .count(intervalMetrics.size())
                    .min(min)
                    .max(max)
                    .avg(avg)
                    .median(median)
                    .p95(p95)
                    .build();
            
            intervalStats.add(stats);
        }
        
        // Sort intervals by time
        intervalStats.sort(Comparator.comparing(IntervalStats::getIntervalStart));
        
        // Calculate overall statistics
        double overallMin = metrics.stream().mapToDouble(Metric::getValue).min().orElse(0);
        double overallMax = metrics.stream().mapToDouble(Metric::getValue).max().orElse(0);
        double overallAvg = metrics.stream().mapToDouble(Metric::getValue).average().orElse(0);
        double overallMedian = calculateMedian(metrics);
        double overallP95 = calculatePercentile(metrics, 95);
        
        // Detect anomalies
        List<AnomalyInfo> anomalies = detectAnomalies(metrics, overallAvg, overallP95);
        
        // Identify trends
        TrendInfo trend = identifyTrend(intervalStats);
        
        PerformanceAnalysisResult result = PerformanceAnalysisResult.builder()
                .metricName(metricName)
                .startTime(startTime)
                .endTime(endTime)
                .intervalMinutes(interval)
                .totalDataPoints(metrics.size())
                .overallMin(overallMin)
                .overallMax(overallMax)
                .overallAvg(overallAvg)
                .overallMedian(overallMedian)
                .overallP95(overallP95)
                .intervalStats(intervalStats)
                .anomalies(anomalies)
                .trend(trend)
                .build();
        
        log.info("Performance analysis completed: {}", result);
        return result;
    }
    
    /**
     * Compare performance between two time periods.
     *
     * @param metricName The name of the metric to compare
     * @param baselineStartTime The start of the baseline period
     * @param baselineEndTime The end of the baseline period
     * @param comparisonStartTime The start of the comparison period
     * @param comparisonEndTime The end of the comparison period
     * @return The performance comparison results
     */
    public PerformanceComparisonResult comparePerformance(
            String metricName,
            Instant baselineStartTime,
            Instant baselineEndTime,
            Instant comparisonStartTime,
            Instant comparisonEndTime) {
        
        log.info("Comparing performance for metric {} between baseline period ({} to {}) and comparison period ({} to {})",
                metricName, baselineStartTime, baselineEndTime, comparisonStartTime, comparisonEndTime);
        
        List<Metric> baselineMetrics = metricRepository.findByNameAndTimestampBetween(
                metricName, baselineStartTime, baselineEndTime);
        
        List<Metric> comparisonMetrics = metricRepository.findByNameAndTimestampBetween(
                metricName, comparisonStartTime, comparisonEndTime);
        
        // Calculate statistics for baseline period
        double baselineMin = baselineMetrics.stream().mapToDouble(Metric::getValue).min().orElse(0);
        double baselineMax = baselineMetrics.stream().mapToDouble(Metric::getValue).max().orElse(0);
        double baselineAvg = baselineMetrics.stream().mapToDouble(Metric::getValue).average().orElse(0);
        double baselineMedian = calculateMedian(baselineMetrics);
        double baselineP95 = calculatePercentile(baselineMetrics, 95);
        
        // Calculate statistics for comparison period
        double comparisonMin = comparisonMetrics.stream().mapToDouble(Metric::getValue).min().orElse(0);
        double comparisonMax = comparisonMetrics.stream().mapToDouble(Metric::getValue).max().orElse(0);
        double comparisonAvg = comparisonMetrics.stream().mapToDouble(Metric::getValue).average().orElse(0);
        double comparisonMedian = calculateMedian(comparisonMetrics);
        double comparisonP95 = calculatePercentile(comparisonMetrics, 95);
        
        // Calculate percent changes
        double avgPercentChange = calculatePercentChange(baselineAvg, comparisonAvg);
        double medianPercentChange = calculatePercentChange(baselineMedian, comparisonMedian);
        double p95PercentChange = calculatePercentChange(baselineP95, comparisonP95);
        
        // Determine if changes are significant
        boolean isSignificantChange = Math.abs(avgPercentChange) > 10 || Math.abs(p95PercentChange) > 15;
        
        PerformanceComparisonResult result = PerformanceComparisonResult.builder()
                .metricName(metricName)
                .baselineStartTime(baselineStartTime)
                .baselineEndTime(baselineEndTime)
                .comparisonStartTime(comparisonStartTime)
                .comparisonEndTime(comparisonEndTime)
                .baselineDataPoints(baselineMetrics.size())
                .comparisonDataPoints(comparisonMetrics.size())
                .baselineMin(baselineMin)
                .baselineMax(baselineMax)
                .baselineAvg(baselineAvg)
                .baselineMedian(baselineMedian)
                .baselineP95(baselineP95)
                .comparisonMin(comparisonMin)
                .comparisonMax(comparisonMax)
                .comparisonAvg(comparisonAvg)
                .comparisonMedian(comparisonMedian)
                .comparisonP95(comparisonP95)
                .avgPercentChange(avgPercentChange)
                .medianPercentChange(medianPercentChange)
                .p95PercentChange(p95PercentChange)
                .isSignificantChange(isSignificantChange)
                .build();
        
        log.info("Performance comparison completed: {}", result);
        return result;
    }
    
    /**
     * Forecast future performance based on historical data.
     *
     * @param metricName The name of the metric to forecast
     * @param startTime The start of the historical period
     * @param endTime The end of the historical period
     * @param forecastHours The number of hours to forecast
     * @param intervalMinutes The interval for aggregation in minutes
     * @return The performance forecast results
     */
    public PerformanceForecastResult forecastPerformance(
            String metricName,
            Instant startTime,
            Instant endTime,
            int forecastHours,
            int intervalMinutes) {
        
        log.info("Forecasting performance for metric {} based on data from {} to {}, forecasting {} hours ahead",
                metricName, startTime, endTime, forecastHours);
        
        List<Metric> metrics = metricRepository.findByNameAndTimestampBetween(metricName, startTime, endTime);
        
        // Group metrics by interval
        Map<Instant, List<Metric>> metricsByInterval = groupMetricsByInterval(metrics, intervalMinutes);
        
        // Calculate average for each interval
        List<TimeSeriesPoint> timeSeriesData = new ArrayList<>();
        
        for (Map.Entry<Instant, List<Metric>> entry : metricsByInterval.entrySet()) {
            Instant intervalStart = entry.getKey();
            List<Metric> intervalMetrics = entry.getValue();
            
            double avg = intervalMetrics.stream().mapToDouble(Metric::getValue).average().orElse(0);
            
            TimeSeriesPoint point = TimeSeriesPoint.builder()
                    .timestamp(intervalStart)
                    .value(avg)
                    .build();
            
            timeSeriesData.add(point);
        }
        
        // Sort time series data by timestamp
        timeSeriesData.sort(Comparator.comparing(TimeSeriesPoint::getTimestamp));
        
        // Simple linear regression for forecasting
        List<TimeSeriesPoint> forecastData = new ArrayList<>();
        
        if (!timeSeriesData.isEmpty()) {
            // Calculate linear regression coefficients
            double[] coefficients = calculateLinearRegressionCoefficients(timeSeriesData);
            double slope = coefficients[0];
            double intercept = coefficients[1];
            
            // Generate forecast points
            Instant lastDataPoint = timeSeriesData.get(timeSeriesData.size() - 1).getTimestamp();
            
            for (int i = 1; i <= forecastHours * (60 / intervalMinutes); i++) {
                Instant forecastTimestamp = lastDataPoint.plus(i * intervalMinutes, ChronoUnit.MINUTES);
                
                // x is the number of intervals from the start
                double x = ChronoUnit.MINUTES.between(timeSeriesData.get(0).getTimestamp(), forecastTimestamp) / intervalMinutes;
                double forecastValue = slope * x + intercept;
                
                TimeSeriesPoint forecastPoint = TimeSeriesPoint.builder()
                        .timestamp(forecastTimestamp)
                        .value(forecastValue)
                        .build();
                
                forecastData.add(forecastPoint);
            }
        }
        
        PerformanceForecastResult result = PerformanceForecastResult.builder()
                .metricName(metricName)
                .startTime(startTime)
                .endTime(endTime)
                .forecastHours(forecastHours)
                .intervalMinutes(intervalMinutes)
                .historicalData(timeSeriesData)
                .forecastData(forecastData)
                .build();
        
        log.info("Performance forecast completed: {}", result);
        return result;
    }
    
    /**
     * Group metrics by time interval.
     *
     * @param metrics The metrics to group
     * @param intervalMinutes The interval in minutes
     * @return Map of interval start time to metrics in that interval
     */
    private Map<Instant, List<Metric>> groupMetricsByInterval(List<Metric> metrics, int intervalMinutes) {
        Map<Instant, List<Metric>> metricsByInterval = new HashMap<>();
        
        for (Metric metric : metrics) {
            Instant intervalStart = metric.getTimestamp().truncatedTo(ChronoUnit.MINUTES)
                    .minus(metric.getTimestamp().toEpochMilli() % (intervalMinutes * 60 * 1000), ChronoUnit.MILLIS);
            
            metricsByInterval.computeIfAbsent(intervalStart, k -> new ArrayList<>()).add(metric);
        }
        
        return metricsByInterval;
    }
    
    /**
     * Calculate the median value from a list of metrics.
     *
     * @param metrics The metrics
     * @return The median value
     */
    private double calculateMedian(List<Metric> metrics) {
        if (metrics.isEmpty()) {
            return 0;
        }
        
        List<Double> values = metrics.stream()
                .map(Metric::getValue)
                .sorted()
                .collect(Collectors.toList());
        
        int middle = values.size() / 2;
        if (values.size() % 2 == 1) {
            return values.get(middle);
        } else {
            return (values.get(middle - 1) + values.get(middle)) / 2.0;
        }
    }
    
    /**
     * Calculate a percentile value from a list of metrics.
     *
     * @param metrics The metrics
     * @param percentile The percentile (0-100)
     * @return The percentile value
     */
    private double calculatePercentile(List<Metric> metrics, int percentile) {
        if (metrics.isEmpty()) {
            return 0;
        }
        
        List<Double> values = metrics.stream()
                .map(Metric::getValue)
                .sorted()
                .collect(Collectors.toList());
        
        int index = (int) Math.ceil(percentile / 100.0 * values.size()) - 1;
        index = Math.max(0, Math.min(values.size() - 1, index));
        
        return values.get(index);
    }
    
    /**
     * Detect anomalies in metrics.
     *
     * @param metrics The metrics
     * @param avg The average value
     * @param p95 The 95th percentile value
     * @return List of anomalies
     */
    private List<AnomalyInfo> detectAnomalies(List<Metric> metrics, double avg, double p95) {
        List<AnomalyInfo> anomalies = new ArrayList<>();
        
        // Define anomaly threshold as 2x the average or above p95
        double threshold = Math.max(2 * avg, p95);
        
        for (Metric metric : metrics) {
            if (metric.getValue() > threshold) {
                AnomalyInfo anomaly = AnomalyInfo.builder()
                        .timestamp(metric.getTimestamp())
                        .value(metric.getValue())
                        .threshold(threshold)
                        .percentAboveThreshold((metric.getValue() - threshold) / threshold * 100)
                        .build();
                
                anomalies.add(anomaly);
            }
        }
        
        return anomalies;
    }
    
    /**
     * Identify trend in interval statistics.
     *
     * @param intervalStats The interval statistics
     * @return The trend information
     */
    private TrendInfo identifyTrend(List<IntervalStats> intervalStats) {
        if (intervalStats.size() < 2) {
            return TrendInfo.builder()
                    .direction("STABLE")
                    .slope(0)
                    .confidence(0)
                    .build();
        }
        
        // Extract x (interval index) and y (average value) for regression
        double[] x = new double[intervalStats.size()];
        double[] y = new double[intervalStats.size()];
        
        for (int i = 0; i < intervalStats.size(); i++) {
            x[i] = i;
            y[i] = intervalStats.get(i).getAvg();
        }
        
        // Calculate linear regression
        double sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        for (int i = 0; i < x.length; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumX2 += x[i] * x[i];
        }
        
        double n = x.length;
        double slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        
        // Calculate correlation coefficient for confidence
        double sumY2 = 0;
        for (int i = 0; i < y.length; i++) {
            sumY2 += y[i] * y[i];
        }
        
        double r = (n * sumXY - sumX * sumY) / 
                Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
        double confidence = Math.abs(r);
        
        // Determine trend direction
        String direction;
        if (Math.abs(slope) < 0.01) {
            direction = "STABLE";
        } else if (slope > 0) {
            direction = "INCREASING";
        } else {
            direction = "DECREASING";
        }
        
        return TrendInfo.builder()
                .direction(direction)
                .slope(slope)
                .confidence(confidence)
                .build();
    }
    
    /**
     * Calculate linear regression coefficients.
     *
     * @param timeSeriesData The time series data
     * @return Array with [slope, intercept]
     */
    private double[] calculateLinearRegressionCoefficients(List<TimeSeriesPoint> timeSeriesData) {
        double[] x = new double[timeSeriesData.size()];
        double[] y = new double[timeSeriesData.size()];
        
        Instant firstTimestamp = timeSeriesData.get(0).getTimestamp();
        
        for (int i = 0; i < timeSeriesData.size(); i++) {
            TimeSeriesPoint point = timeSeriesData.get(i);
            // x is the number of minutes from the first timestamp
            x[i] = ChronoUnit.MINUTES.between(firstTimestamp, point.getTimestamp());
            y[i] = point.getValue();
        }
        
        // Calculate linear regression coefficients
        double sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        for (int i = 0; i < x.length; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumX2 += x[i] * x[i];
        }
        
        double n = x.length;
        double slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        double intercept = (sumY - slope * sumX) / n;
        
        return new double[] { slope, intercept };
    }
    
    /**
     * Calculate percent change between two values.
     *
     * @param baseline The baseline value
     * @param comparison The comparison value
     * @return The percent change
     */
    private double calculatePercentChange(double baseline, double comparison) {
        if (baseline == 0) {
            return comparison == 0 ? 0 : 100;
        }
        return ((comparison - baseline) / baseline) * 100;
    }
    
    /**
     * Data class for interval statistics.
     */
    @lombok.Data
    @lombok.Builder
    public static class IntervalStats {
        private Instant intervalStart;
        private int count;
        private double min;
        private double max;
        private double avg;
        private double median;
        private double p95;
    }
    
    /**
     * Data class for anomaly information.
     */
    @lombok.Data
    @lombok.Builder
    public static class AnomalyInfo {
        private Instant timestamp;
        private double value;
        private double threshold;
        private double percentAboveThreshold;
    }
    
    /**
     * Data class for trend information.
     */
    @lombok.Data
    @lombok.Builder
    public static class TrendInfo {
        private String direction;
        private double slope;
        private double confidence;
    }
    
    /**
     * Data class for time series point.
     */
    @lombok.Data
    @lombok.Builder
    public static class TimeSeriesPoint {
        private Instant timestamp;
        private double value;
    }
    
    /**
     * Data class for performance analysis result.
     */
    @lombok.Data
    @lombok.Builder
    public static class PerformanceAnalysisResult {
        private String metricName;
        private Instant startTime;
        private Instant endTime;
        private int intervalMinutes;
        private int totalDataPoints;
        private double overallMin;
        private double overallMax;
        private double overallAvg;
        private double overallMedian;
        private double overallP95;
        private List<IntervalStats> intervalStats;
        private List<AnomalyInfo> anomalies;
        private TrendInfo trend;
    }
    
    /**
     * Data class for performance comparison result.
     */
    @lombok.Data
    @lombok.Builder
    public static class PerformanceComparisonResult {
        private String metricName;
        private Instant baselineStartTime;
        private Instant baselineEndTime;
        private Instant comparisonStartTime;
        private Instant comparisonEndTime;
        private int baselineDataPoints;
        private int comparisonDataPoints;
        private double baselineMin;
        private double baselineMax;
        private double baselineAvg;
        private double baselineMedian;
        private double baselineP95;
        private double comparisonMin;
        private double comparisonMax;
        private double comparisonAvg;
        private double comparisonMedian;
        private double comparisonP95;
        private double avgPercentChange;
        private double medianPercentChange;
        private double p95PercentChange;
        private boolean isSignificantChange;
    }
    
    /**
     * Data class for performance forecast result.
     */
    @lombok.Data
    @lombok.Builder
    public static class PerformanceForecastResult {
        private String metricName;
        private Instant startTime;
        private Instant endTime;
        private int forecastHours;
        private int intervalMinutes;
        private List<TimeSeriesPoint> historicalData;
        private List<TimeSeriesPoint> forecastData;
    }
}
