package ai.lumina.monitoring.analytics;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import ai.lumina.monitoring.model.AnalyticsEvent;
import ai.lumina.monitoring.model.Metric;
import ai.lumina.monitoring.repository.AnalyticsEventRepository;
import ai.lumina.monitoring.repository.MetricRepository;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for business impact analytics.
 * This class provides methods to analyze the business impact of system performance and user behavior.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class BusinessImpactAnalytics {

    private final AnalyticsEventRepository analyticsEventRepository;
    private final MetricRepository metricRepository;

    /**
     * Analyze the correlation between system performance and business metrics.
     *
     * @param performanceMetricName The name of the performance metric
     * @param businessMetricName The name of the business metric
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @param intervalMinutes The interval for aggregation in minutes
     * @return The correlation analysis results
     */
    public CorrelationAnalysisResult analyzePerformanceBusinessCorrelation(
            String performanceMetricName,
            String businessMetricName,
            Instant startTime,
            Instant endTime,
            int intervalMinutes) {
        
        log.info("Analyzing correlation between performance metric {} and business metric {} from {} to {}",
                performanceMetricName, businessMetricName, startTime, endTime);
        
        List<Metric> performanceMetrics = metricRepository.findByNameAndTimestampBetween(
                performanceMetricName, startTime, endTime);
        
        List<Metric> businessMetrics = metricRepository.findByNameAndTimestampBetween(
                businessMetricName, startTime, endTime);
        
        // Group metrics by interval
        Map<Instant, List<Metric>> performanceByInterval = groupMetricsByInterval(performanceMetrics, intervalMinutes);
        Map<Instant, List<Metric>> businessByInterval = groupMetricsByInterval(businessMetrics, intervalMinutes);
        
        // Calculate average for each interval
        List<CorrelationDataPoint> correlationData = new ArrayList<>();
        
        // Find common intervals
        Set<Instant> commonIntervals = new HashSet<>(performanceByInterval.keySet());
        commonIntervals.retainAll(businessByInterval.keySet());
        
        for (Instant interval : commonIntervals) {
            List<Metric> performanceIntervalMetrics = performanceByInterval.get(interval);
            List<Metric> businessIntervalMetrics = businessByInterval.get(interval);
            
            double performanceAvg = performanceIntervalMetrics.stream()
                    .mapToDouble(Metric::getValue)
                    .average()
                    .orElse(0);
            
            double businessAvg = businessIntervalMetrics.stream()
                    .mapToDouble(Metric::getValue)
                    .average()
                    .orElse(0);
            
            CorrelationDataPoint dataPoint = CorrelationDataPoint.builder()
                    .timestamp(interval)
                    .performanceValue(performanceAvg)
                    .businessValue(businessAvg)
                    .build();
            
            correlationData.add(dataPoint);
        }
        
        // Sort data points by timestamp
        correlationData.sort(Comparator.comparing(CorrelationDataPoint::getTimestamp));
        
        // Calculate correlation coefficient
        double correlationCoefficient = calculateCorrelationCoefficient(
                correlationData.stream().map(CorrelationDataPoint::getPerformanceValue).collect(Collectors.toList()),
                correlationData.stream().map(CorrelationDataPoint::getBusinessValue).collect(Collectors.toList()));
        
        // Determine correlation strength and direction
        String correlationStrength;
        if (Math.abs(correlationCoefficient) < 0.3) {
            correlationStrength = "WEAK";
        } else if (Math.abs(correlationCoefficient) < 0.7) {
            correlationStrength = "MODERATE";
        } else {
            correlationStrength = "STRONG";
        }
        
        String correlationDirection = correlationCoefficient >= 0 ? "POSITIVE" : "NEGATIVE";
        
        // Calculate impact estimate (simple linear model)
        double impactEstimate = 0;
        if (correlationData.size() >= 2) {
            // Simple linear regression
            double[] coefficients = calculateLinearRegressionCoefficients(correlationData);
            double slope = coefficients[0];
            
            // Estimate impact: how much business metric changes for 1 unit change in performance
            impactEstimate = slope;
        }
        
        CorrelationAnalysisResult result = CorrelationAnalysisResult.builder()
                .performanceMetricName(performanceMetricName)
                .businessMetricName(businessMetricName)
                .startTime(startTime)
                .endTime(endTime)
                .intervalMinutes(intervalMinutes)
                .dataPoints(correlationData)
                .correlationCoefficient(correlationCoefficient)
                .correlationStrength(correlationStrength)
                .correlationDirection(correlationDirection)
                .impactEstimate(impactEstimate)
                .build();
        
        log.info("Correlation analysis completed: {}", result);
        return result;
    }
    
    /**
     * Analyze the business impact of system incidents.
     *
     * @param incidentEventType The event type for incidents
     * @param businessMetricName The name of the business metric
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @param impactWindowHours The number of hours to consider for impact after an incident
     * @return The incident impact analysis results
     */
    public IncidentImpactAnalysisResult analyzeIncidentBusinessImpact(
            String incidentEventType,
            String businessMetricName,
            Instant startTime,
            Instant endTime,
            int impactWindowHours) {
        
        log.info("Analyzing business impact of incidents from {} to {} with impact window of {} hours",
                startTime, endTime, impactWindowHours);
        
        // Find incident events
        List<AnalyticsEvent> incidentEvents = analyticsEventRepository.findByEventTypeAndTimestampBetween(
                incidentEventType, startTime, endTime);
        
        // Find business metrics
        List<Metric> businessMetrics = metricRepository.findByNameAndTimestampBetween(
                businessMetricName, startTime, endTime);
        
        List<IncidentImpactInfo> incidentImpacts = new ArrayList<>();
        
        for (AnalyticsEvent incident : incidentEvents) {
            Instant incidentTime = incident.getTimestamp();
            Instant impactEndTime = incidentTime.plus(impactWindowHours, ChronoUnit.HOURS);
            
            // Get business metrics before incident (baseline)
            Instant baselineStartTime = incidentTime.minus(impactWindowHours, ChronoUnit.HOURS);
            List<Metric> baselineMetrics = businessMetrics.stream()
                    .filter(m -> m.getTimestamp().isAfter(baselineStartTime) && m.getTimestamp().isBefore(incidentTime))
                    .collect(Collectors.toList());
            
            // Get business metrics after incident (impact period)
            List<Metric> impactMetrics = businessMetrics.stream()
                    .filter(m -> m.getTimestamp().isAfter(incidentTime) && m.getTimestamp().isBefore(impactEndTime))
                    .collect(Collectors.toList());
            
            // Calculate average values
            double baselineAvg = baselineMetrics.stream()
                    .mapToDouble(Metric::getValue)
                    .average()
                    .orElse(0);
            
            double impactAvg = impactMetrics.stream()
                    .mapToDouble(Metric::getValue)
                    .average()
                    .orElse(0);
            
            // Calculate percent change
            double percentChange = baselineAvg == 0 ? 0 : ((impactAvg - baselineAvg) / baselineAvg) * 100;
            
            // Determine impact severity
            String impactSeverity;
            if (Math.abs(percentChange) < 5) {
                impactSeverity = "MINIMAL";
            } else if (Math.abs(percentChange) < 15) {
                impactSeverity = "MODERATE";
            } else {
                impactSeverity = "SEVERE";
            }
            
            IncidentImpactInfo impactInfo = IncidentImpactInfo.builder()
                    .incidentId(incident.getId())
                    .incidentTime(incidentTime)
                    .incidentProperties(incident.getProperties())
                    .baselineStartTime(baselineStartTime)
                    .impactEndTime(impactEndTime)
                    .baselineAvg(baselineAvg)
                    .impactAvg(impactAvg)
                    .percentChange(percentChange)
                    .impactSeverity(impactSeverity)
                    .build();
            
            incidentImpacts.add(impactInfo);
        }
        
        // Calculate total business impact
        double totalImpact = incidentImpacts.stream()
                .mapToDouble(impact -> impact.getPercentChange())
                .sum();
        
        // Calculate average impact per incident
        double avgImpactPerIncident = incidentImpacts.isEmpty() ? 0 :
                totalImpact / incidentImpacts.size();
        
        IncidentImpactAnalysisResult result = IncidentImpactAnalysisResult.builder()
                .incidentEventType(incidentEventType)
                .businessMetricName(businessMetricName)
                .startTime(startTime)
                .endTime(endTime)
                .impactWindowHours(impactWindowHours)
                .incidentCount(incidentEvents.size())
                .incidentImpacts(incidentImpacts)
                .totalImpact(totalImpact)
                .avgImpactPerIncident(avgImpactPerIncident)
                .build();
        
        log.info("Incident impact analysis completed: {}", result);
        return result;
    }
    
    /**
     * Analyze the ROI of performance improvements.
     *
     * @param performanceMetricName The name of the performance metric
     * @param businessMetricName The name of the business metric
     * @param improvementStartTime The time when the improvement was implemented
     * @param beforePeriodHours The number of hours to consider before the improvement
     * @param afterPeriodHours The number of hours to consider after the improvement
     * @param implementationCost The cost of implementing the improvement
     * @param businessMetricValue The monetary value of one unit of the business metric
     * @return The ROI analysis results
     */
    public RoiAnalysisResult analyzePerformanceImprovementRoi(
            String performanceMetricName,
            String businessMetricName,
            Instant improvementStartTime,
            int beforePeriodHours,
            int afterPeriodHours,
            double implementationCost,
            double businessMetricValue) {
        
        log.info("Analyzing ROI of performance improvement at {} for metric {}", 
                improvementStartTime, performanceMetricName);
        
        // Define time periods
        Instant beforeStartTime = improvementStartTime.minus(beforePeriodHours, ChronoUnit.HOURS);
        Instant afterEndTime = improvementStartTime.plus(afterPeriodHours, ChronoUnit.HOURS);
        
        // Get performance metrics before and after
        List<Metric> beforePerformanceMetrics = metricRepository.findByNameAndTimestampBetween(
                performanceMetricName, beforeStartTime, improvementStartTime);
        
        List<Metric> afterPerformanceMetrics = metricRepository.findByNameAndTimestampBetween(
                performanceMetricName, improvementStartTime, afterEndTime);
        
        // Get business metrics before and after
        List<Metric> beforeBusinessMetrics = metricRepository.findByNameAndTimestampBetween(
                businessMetricName, beforeStartTime, improvementStartTime);
        
        List<Metric> afterBusinessMetrics = metricRepository.findByNameAndTimestampBetween(
                businessMetricName, improvementStartTime, afterEndTime);
        
        // Calculate average values
        double beforePerformanceAvg = beforePerformanceMetrics.stream()
                .mapToDouble(Metric::getValue)
                .average()
                .orElse(0);
        
        double afterPerformanceAvg = afterPerformanceMetrics.stream()
                .mapToDouble(Metric::getValue)
                .average()
                .orElse(0);
        
        double beforeBusinessAvg = beforeBusinessMetrics.stream()
                .mapToDouble(Metric::getValue)
                .average()
                .orElse(0);
        
        double afterBusinessAvg = afterBusinessMetrics.stream()
                .mapToDouble(Metric::getValue)
                .average()
                .orElse(0);
        
        // Calculate percent changes
        double performanceImprovement = beforePerformanceAvg == 0 ? 0 :
                ((afterPerformanceAvg - beforePerformanceAvg) / beforePerformanceAvg) * 100;
        
        double businessImprovement = beforeBusinessAvg == 0 ? 0 :
                ((afterBusinessAvg - beforeBusinessAvg) / beforeBusinessAvg) * 100;
        
        // Calculate business value
        double businessValueBefore = beforeBusinessAvg * businessMetricValue * beforePeriodHours;
        double businessValueAfter = afterBusinessAvg * businessMetricValue * afterPeriodHours;
        
        // Normalize to same time period if before and after periods differ
        if (beforePeriodHours != afterPeriodHours) {
            double hourRatio = (double) beforePeriodHours / afterPeriodHours;
            businessValueAfter = businessValueAfter * hourRatio;
        }
        
        double businessValueDifference = businessValueAfter - businessValueBefore;
        
        // Calculate ROI
        double roi = implementationCost == 0 ? 0 :
                (businessValueDifference - implementationCost) / implementationCost * 100;
        
        // Calculate payback period (in hours)
        double hourlyValueIncrease = businessValueDifference / beforePeriodHours;
        double paybackPeriodHours = hourlyValueIncrease <= 0 ? Double.POSITIVE_INFINITY :
                implementationCost / hourlyValueIncrease;
        
        RoiAnalysisResult result = RoiAnalysisResult.builder()
                .performanceMetricName(performanceMetricName)
                .businessMetricName(businessMetricName)
                .improvementStartTime(improvementStartTime)
                .beforePeriodHours(beforePeriodHours)
                .afterPeriodHours(afterPeriodHours)
                .beforePerformanceAvg(beforePerformanceAvg)
                .afterPerformanceAvg(afterPerformanceAvg)
                .performanceImprovement(performanceImprovement)
                .beforeBusinessAvg(beforeBusinessAvg)
                .afterBusinessAvg(afterBusinessAvg)
                .businessImprovement(businessImprovement)
                .implementationCost(implementationCost)
                .businessMetricValue(businessMetricValue)
                .businessValueDifference(businessValueDifference)
                .roi(roi)
                .paybackPeriodHours(paybackPeriodHours)
                .build();
        
        log.info("ROI analysis completed: {}", result);
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
     * Calculate correlation coefficient between two lists of values.
     *
     * @param x The first list of values
     * @param y The second list of values
     * @return The correlation coefficient
     */
    private double calculateCorrelationCoefficient(List<Double> x, List<Double> y) {
        if (x.size() != y.size() || x.isEmpty()) {
            return 0;
        }
        
        int n = x.size();
        
        double sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;
        
        for (int i = 0; i < n; i++) {
            sumX += x.get(i);
            sumY += y.get(i);
            sumXY += x.get(i) * y.get(i);
            sumX2 += x.get(i) * x.get(i);
            sumY2 += y.get(i) * y.get(i);
        }
        
        double numerator = n * sumXY - sumX * sumY;
        double denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
        
        return denominator == 0 ? 0 : numerator / denominator;
    }
    
    /**
     * Calculate linear regression coefficients.
     *
     * @param correlationData The correlation data points
     * @return Array with [slope, intercept]
     */
    private double[] calculateLinearRegressionCoefficients(List<CorrelationDataPoint> correlationData) {
        double[] x = new double[correlationData.size()];
        double[] y = new double[correlationData.size()];
        
        for (int i = 0; i < correlationData.size(); i++) {
            CorrelationDataPoint point = correlationData.get(i);
            x[i] = point.getPerformanceValue();
            y[i] = point.getBusinessValue();
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
     * Data class for correlation data point.
     */
    @lombok.Data
    @lombok.Builder
    public static class CorrelationDataPoint {
        private Instant timestamp;
        private double performanceValue;
        private double businessValue;
    }
    
    /**
     * Data class for correlation analysis result.
     */
    @lombok.Data
    @lombok.Builder
    public static class CorrelationAnalysisResult {
        private String performanceMetricName;
        private String businessMetricName;
        private Instant startTime;
        private Instant endTime;
        private int intervalMinutes;
        private List<CorrelationDataPoint> dataPoints;
        private double correlationCoefficient;
        private String correlationStrength;
        private String correlationDirection;
        private double impactEstimate;
    }
    
    /**
     * Data class for incident impact information.
     */
    @lombok.Data
    @lombok.Builder
    public static class IncidentImpactInfo {
        private String incidentId;
        private Instant incidentTime;
        private Map<String, String> incidentProperties;
        private Instant baselineStartTime;
        private Instant impactEndTime;
        private double baselineAvg;
        private double impactAvg;
        private double percentChange;
        private String impactSeverity;
    }
    
    /**
     * Data class for incident impact analysis result.
     */
    @lombok.Data
    @lombok.Builder
    public static class IncidentImpactAnalysisResult {
        private String incidentEventType;
        private String businessMetricName;
        private Instant startTime;
        private Instant endTime;
        private int impactWindowHours;
        private int incidentCount;
        private List<IncidentImpactInfo> incidentImpacts;
        private double totalImpact;
        private double avgImpactPerIncident;
    }
    
    /**
     * Data class for ROI analysis result.
     */
    @lombok.Data
    @lombok.Builder
    public static class RoiAnalysisResult {
        private String performanceMetricName;
        private String businessMetricName;
        private Instant improvementStartTime;
        private int beforePeriodHours;
        private int afterPeriodHours;
        private double beforePerformanceAvg;
        private double afterPerformanceAvg;
        private double performanceImprovement;
        private double beforeBusinessAvg;
        private double afterBusinessAvg;
        private double businessImprovement;
        private double implementationCost;
        private double businessMetricValue;
        private double businessValueDifference;
        private double roi;
        private double paybackPeriodHours;
    }
}
