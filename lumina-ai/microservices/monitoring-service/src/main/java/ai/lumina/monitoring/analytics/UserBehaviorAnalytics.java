package ai.lumina.monitoring.analytics;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import ai.lumina.monitoring.model.AnalyticsEvent;
import ai.lumina.monitoring.repository.AnalyticsEventRepository;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for user behavior analytics.
 * This class provides methods to analyze user interactions and behavior patterns.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class UserBehaviorAnalytics {

    private final AnalyticsEventRepository analyticsEventRepository;

    /**
     * Analyze user engagement over a time period.
     *
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @return The user engagement metrics
     */
    public UserEngagementMetrics analyzeUserEngagement(Instant startTime, Instant endTime) {
        log.info("Analyzing user engagement from {} to {}", startTime, endTime);
        
        List<AnalyticsEvent> events = analyticsEventRepository.findByTimestampBetween(startTime, endTime);
        
        // Count unique users
        Set<String> uniqueUsers = events.stream()
                .map(AnalyticsEvent::getUserId)
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());
        
        // Count sessions (group events by user and time proximity)
        Map<String, List<AnalyticsEvent>> eventsByUser = events.stream()
                .filter(e -> e.getUserId() != null)
                .collect(Collectors.groupingBy(AnalyticsEvent::getUserId));
        
        int sessionCount = 0;
        Map<String, Integer> sessionsPerUser = new HashMap<>();
        
        for (Map.Entry<String, List<AnalyticsEvent>> entry : eventsByUser.entrySet()) {
            String userId = entry.getKey();
            List<AnalyticsEvent> userEvents = entry.getValue().stream()
                    .sorted(Comparator.comparing(AnalyticsEvent::getTimestamp))
                    .collect(Collectors.toList());
            
            int userSessions = countSessions(userEvents, 30); // 30 minutes session timeout
            sessionsPerUser.put(userId, userSessions);
            sessionCount += userSessions;
        }
        
        // Calculate average session duration
        double avgSessionDuration = calculateAverageSessionDuration(eventsByUser, 30);
        
        // Count events by type
        Map<String, Long> eventCounts = events.stream()
                .collect(Collectors.groupingBy(AnalyticsEvent::getEventType, Collectors.counting()));
        
        // Calculate events per user
        double eventsPerUser = uniqueUsers.isEmpty() ? 0 : (double) events.size() / uniqueUsers.size();
        
        // Calculate daily active users
        Map<String, Integer> dailyActiveUsers = calculateDailyActiveUsers(events, startTime, endTime);
        
        // Calculate retention (users who returned on subsequent days)
        double retentionRate = calculateRetentionRate(events, startTime, endTime);
        
        UserEngagementMetrics metrics = UserEngagementMetrics.builder()
                .startTime(startTime)
                .endTime(endTime)
                .uniqueUserCount(uniqueUsers.size())
                .totalEventCount(events.size())
                .sessionCount(sessionCount)
                .averageSessionDurationMinutes(avgSessionDuration)
                .eventsPerUser(eventsPerUser)
                .eventTypeDistribution(eventCounts)
                .dailyActiveUsers(dailyActiveUsers)
                .retentionRate(retentionRate)
                .build();
        
        log.info("User engagement analysis completed: {}", metrics);
        return metrics;
    }
    
    /**
     * Identify user behavior patterns.
     *
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @param minSupport The minimum support threshold for pattern identification
     * @return The identified behavior patterns
     */
    public List<BehaviorPattern> identifyBehaviorPatterns(Instant startTime, Instant endTime, double minSupport) {
        log.info("Identifying behavior patterns from {} to {} with minimum support {}", 
                startTime, endTime, minSupport);
        
        List<AnalyticsEvent> events = analyticsEventRepository.findByTimestampBetween(startTime, endTime);
        
        // Group events by user
        Map<String, List<AnalyticsEvent>> eventsByUser = events.stream()
                .filter(e -> e.getUserId() != null)
                .collect(Collectors.groupingBy(AnalyticsEvent::getUserId));
        
        // Extract event sequences for each user
        Map<String, List<String>> eventSequences = new HashMap<>();
        for (Map.Entry<String, List<AnalyticsEvent>> entry : eventsByUser.entrySet()) {
            List<String> sequence = entry.getValue().stream()
                    .sorted(Comparator.comparing(AnalyticsEvent::getTimestamp))
                    .map(AnalyticsEvent::getEventType)
                    .collect(Collectors.toList());
            
            eventSequences.put(entry.getKey(), sequence);
        }
        
        // Find frequent patterns (simplified implementation)
        Map<List<String>, Integer> patternCounts = new HashMap<>();
        int totalUsers = eventSequences.size();
        
        // Look for patterns of length 2-3
        for (List<String> sequence : eventSequences.values()) {
            // Find patterns of length 2
            for (int i = 0; i < sequence.size() - 1; i++) {
                List<String> pattern2 = Arrays.asList(sequence.get(i), sequence.get(i + 1));
                patternCounts.put(pattern2, patternCounts.getOrDefault(pattern2, 0) + 1);
            }
            
            // Find patterns of length 3
            for (int i = 0; i < sequence.size() - 2; i++) {
                List<String> pattern3 = Arrays.asList(sequence.get(i), sequence.get(i + 1), sequence.get(i + 2));
                patternCounts.put(pattern3, patternCounts.getOrDefault(pattern3, 0) + 1);
            }
        }
        
        // Filter patterns by minimum support
        List<BehaviorPattern> patterns = new ArrayList<>();
        for (Map.Entry<List<String>, Integer> entry : patternCounts.entrySet()) {
            double support = (double) entry.getValue() / totalUsers;
            if (support >= minSupport) {
                BehaviorPattern pattern = BehaviorPattern.builder()
                        .eventSequence(entry.getKey())
                        .occurrences(entry.getValue())
                        .support(support)
                        .build();
                
                patterns.add(pattern);
            }
        }
        
        // Sort patterns by support (descending)
        patterns.sort(Comparator.comparing(BehaviorPattern::getSupport).reversed());
        
        log.info("Identified {} behavior patterns", patterns.size());
        return patterns;
    }
    
    /**
     * Analyze user conversion funnel.
     *
     * @param funnelSteps The event types representing funnel steps
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @return The funnel analysis results
     */
    public FunnelAnalysisResult analyzeFunnel(List<String> funnelSteps, Instant startTime, Instant endTime) {
        log.info("Analyzing funnel with steps {} from {} to {}", funnelSteps, startTime, endTime);
        
        List<AnalyticsEvent> events = analyticsEventRepository.findByTimestampBetween(startTime, endTime);
        
        // Group events by user
        Map<String, List<AnalyticsEvent>> eventsByUser = events.stream()
                .filter(e -> e.getUserId() != null)
                .collect(Collectors.groupingBy(AnalyticsEvent::getUserId));
        
        // Count users at each step
        List<Integer> usersPerStep = new ArrayList<>();
        List<Double> conversionRates = new ArrayList<>();
        
        // Count users who completed the first step
        int usersInPreviousStep = 0;
        
        for (int i = 0; i < funnelSteps.size(); i++) {
            String step = funnelSteps.get(i);
            int usersInStep = 0;
            
            for (Map.Entry<String, List<AnalyticsEvent>> entry : eventsByUser.entrySet()) {
                List<AnalyticsEvent> userEvents = entry.getValue();
                
                // Check if user has completed all previous steps
                boolean completedPreviousSteps = true;
                if (i > 0) {
                    for (int j = 0; j < i; j++) {
                        final String previousStep = funnelSteps.get(j);
                        boolean completedStep = userEvents.stream()
                                .anyMatch(e -> e.getEventType().equals(previousStep));
                        
                        if (!completedStep) {
                            completedPreviousSteps = false;
                            break;
                        }
                    }
                }
                
                if (completedPreviousSteps) {
                    boolean completedCurrentStep = userEvents.stream()
                            .anyMatch(e -> e.getEventType().equals(step));
                    
                    if (completedCurrentStep) {
                        usersInStep++;
                    }
                }
            }
            
            usersPerStep.add(usersInStep);
            
            // Calculate conversion rate
            double conversionRate = 0.0;
            if (i == 0) {
                // First step conversion is based on total users
                conversionRate = eventsByUser.isEmpty() ? 0 : (double) usersInStep / eventsByUser.size();
            } else if (usersInPreviousStep > 0) {
                // Subsequent steps are based on previous step
                conversionRate = (double) usersInStep / usersInPreviousStep;
            }
            
            conversionRates.add(conversionRate);
            usersInPreviousStep = usersInStep;
        }
        
        // Calculate overall conversion rate
        double overallConversionRate = 0.0;
        if (!eventsByUser.isEmpty() && !usersPerStep.isEmpty()) {
            overallConversionRate = (double) usersPerStep.get(usersPerStep.size() - 1) / eventsByUser.size();
        }
        
        FunnelAnalysisResult result = FunnelAnalysisResult.builder()
                .funnelSteps(funnelSteps)
                .startTime(startTime)
                .endTime(endTime)
                .totalUsers(eventsByUser.size())
                .usersPerStep(usersPerStep)
                .conversionRates(conversionRates)
                .overallConversionRate(overallConversionRate)
                .build();
        
        log.info("Funnel analysis completed: {}", result);
        return result;
    }
    
    /**
     * Count sessions from a list of user events.
     *
     * @param events The user events
     * @param sessionTimeoutMinutes The session timeout in minutes
     * @return The number of sessions
     */
    private int countSessions(List<AnalyticsEvent> events, int sessionTimeoutMinutes) {
        if (events.isEmpty()) {
            return 0;
        }
        
        int sessionCount = 1;
        Instant lastEventTime = events.get(0).getTimestamp();
        
        for (int i = 1; i < events.size(); i++) {
            Instant currentEventTime = events.get(i).getTimestamp();
            long minutesBetween = ChronoUnit.MINUTES.between(lastEventTime, currentEventTime);
            
            if (minutesBetween > sessionTimeoutMinutes) {
                sessionCount++;
            }
            
            lastEventTime = currentEventTime;
        }
        
        return sessionCount;
    }
    
    /**
     * Calculate the average session duration.
     *
     * @param eventsByUser The events grouped by user
     * @param sessionTimeoutMinutes The session timeout in minutes
     * @return The average session duration in minutes
     */
    private double calculateAverageSessionDuration(Map<String, List<AnalyticsEvent>> eventsByUser, int sessionTimeoutMinutes) {
        List<Double> sessionDurations = new ArrayList<>();
        
        for (List<AnalyticsEvent> userEvents : eventsByUser.values()) {
            if (userEvents.isEmpty()) {
                continue;
            }
            
            userEvents.sort(Comparator.comparing(AnalyticsEvent::getTimestamp));
            
            Instant sessionStart = userEvents.get(0).getTimestamp();
            Instant lastEventTime = sessionStart;
            
            for (int i = 1; i < userEvents.size(); i++) {
                Instant currentEventTime = userEvents.get(i).getTimestamp();
                long minutesBetween = ChronoUnit.MINUTES.between(lastEventTime, currentEventTime);
                
                if (minutesBetween > sessionTimeoutMinutes) {
                    // End of session, calculate duration
                    double sessionDuration = ChronoUnit.MINUTES.between(sessionStart, lastEventTime);
                    sessionDurations.add(sessionDuration);
                    
                    // Start new session
                    sessionStart = currentEventTime;
                }
                
                lastEventTime = currentEventTime;
            }
            
            // Add the last session
            double lastSessionDuration = ChronoUnit.MINUTES.between(sessionStart, lastEventTime);
            sessionDurations.add(lastSessionDuration);
        }
        
        return sessionDurations.stream().mapToDouble(Double::doubleValue).average().orElse(0);
    }
    
    /**
     * Calculate daily active users.
     *
     * @param events The analytics events
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @return Map of date to active user count
     */
    private Map<String, Integer> calculateDailyActiveUsers(List<AnalyticsEvent> events, Instant startTime, Instant endTime) {
        Map<String, Set<String>> usersByDay = new HashMap<>();
        
        for (AnalyticsEvent event : events) {
            if (event.getUserId() != null) {
                String day = event.getTimestamp().truncatedTo(ChronoUnit.DAYS).toString().substring(0, 10);
                usersByDay.computeIfAbsent(day, k -> new HashSet<>()).add(event.getUserId());
            }
        }
        
        Map<String, Integer> dailyActiveUsers = new HashMap<>();
        for (Map.Entry<String, Set<String>> entry : usersByDay.entrySet()) {
            dailyActiveUsers.put(entry.getKey(), entry.getValue().size());
        }
        
        return dailyActiveUsers;
    }
    
    /**
     * Calculate user retention rate.
     *
     * @param events The analytics events
     * @param startTime The start of the time period
     * @param endTime The end of the time period
     * @return The retention rate
     */
    private double calculateRetentionRate(List<AnalyticsEvent> events, Instant startTime, Instant endTime) {
        Map<String, Set<String>> usersByDay = new HashMap<>();
        
        for (AnalyticsEvent event : events) {
            if (event.getUserId() != null) {
                String day = event.getTimestamp().truncatedTo(ChronoUnit.DAYS).toString().substring(0, 10);
                usersByDay.computeIfAbsent(day, k -> new HashSet<>()).add(event.getUserId());
            }
        }
        
        if (usersByDay.size() <= 1) {
            return 0.0;
        }
        
        List<String> days = new ArrayList<>(usersByDay.keySet());
        Collections.sort(days);
        
        int totalReturnedUsers = 0;
        int totalFirstDayUsers = 0;
        
        for (int i = 0; i < days.size() - 1; i++) {
            Set<String> firstDayUsers = usersByDay.get(days.get(i));
            Set<String> nextDayUsers = usersByDay.get(days.get(i + 1));
            
            // Count users who returned the next day
            int returnedUsers = 0;
            for (String userId : firstDayUsers) {
                if (nextDayUsers.contains(userId)) {
                    returnedUsers++;
                }
            }
            
            totalReturnedUsers += returnedUsers;
            totalFirstDayUsers += firstDayUsers.size();
        }
        
        return totalFirstDayUsers > 0 ? (double) totalReturnedUsers / totalFirstDayUsers : 0;
    }
    
    /**
     * Data class for user engagement metrics.
     */
    @lombok.Data
    @lombok.Builder
    public static class UserEngagementMetrics {
        private Instant startTime;
        private Instant endTime;
        private int uniqueUserCount;
        private int totalEventCount;
        private int sessionCount;
        private double averageSessionDurationMinutes;
        private double eventsPerUser;
        private Map<String, Long> eventTypeDistribution;
        private Map<String, Integer> dailyActiveUsers;
        private double retentionRate;
    }
    
    /**
     * Data class for behavior pattern.
     */
    @lombok.Data
    @lombok.Builder
    public static class BehaviorPattern {
        private List<String> eventSequence;
        private int occurrences;
        private double support;
    }
    
    /**
     * Data class for funnel analysis result.
     */
    @lombok.Data
    @lombok.Builder
    public static class FunnelAnalysisResult {
        private List<String> funnelSteps;
        private Instant startTime;
        private Instant endTime;
        private int totalUsers;
        private List<Integer> usersPerStep;
        private List<Double> conversionRates;
        private double overallConversionRate;
    }
}
