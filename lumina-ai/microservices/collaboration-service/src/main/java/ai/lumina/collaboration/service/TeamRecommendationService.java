package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.*;
import ai.lumina.collaboration.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

/**
 * Enhanced service for team recommendations and analysis.
 */
@Service
public class TeamRecommendationService {

    private static final Logger logger = LoggerFactory.getLogger(TeamRecommendationService.class);

    @Autowired
    private AgentRepository agentRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private AdvancedTeamFormationService teamFormationService;

    @Value("${collaboration.team.dynamic-formation.capability-match-threshold:0.75}")
    private double capabilityMatchThreshold;

    /**
     * Generate multiple team recommendations for a task using different strategies.
     *
     * @param taskId The ID of the task for which to generate recommendations
     * @param count The number of recommendations to generate
     * @return A list of recommended teams
     */
    @Transactional
    public List<Team> getTeamRecommendations(Long taskId, int count) {
        logger.info("Generating {} team recommendations for task ID: {}", count, taskId);
        
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new NoSuchElementException("Task not found with ID: " + taskId));
        
        List<Team> recommendations = new ArrayList<>();
        
        // Generate recommendations using different strategies
        recommendations.add(generateCapabilityBasedTeam(task));
        
        if (count > 1) {
            recommendations.add(generatePerformanceBasedTeam(task));
        }
        
        if (count > 2) {
            recommendations.add(generateCostOptimizedTeam(task));
        }
        
        if (count > 3) {
            recommendations.add(generateSpecializationBasedTeam(task));
        }
        
        if (count > 4) {
            recommendations.add(generateBalancedTeam(task));
        }
        
        // Sort recommendations by a composite score
        recommendations.sort(Comparator.comparingDouble(this::calculateTeamCompositeScore).reversed());
        
        // Limit to requested count
        if (recommendations.size() > count) {
            recommendations = recommendations.subList(0, count);
        }
        
        return recommendations;
    }
    
    /**
     * Generate a team optimized for capability matching.
     *
     * @param task The task for which to form a team
     * @return The formed team
     */
    private Team generateCapabilityBasedTeam(Task task) {
        Team team = createBaseTeam(task, "Capability-Optimized");
        
        // Get all available agents
        List<Agent> availableAgents = agentRepository.findByAvailableTrue();
        
        // For each required role, find the agent with the best capability match
        for (Role role : task.getRequiredRoles()) {
            Agent bestAgent = findBestAgentByCapability(role, task.getRequiredCapabilities(), availableAgents, team);
            
            if (bestAgent != null) {
                team.getAgents().add(bestAgent);
                availableAgents.remove(bestAgent);
                logger.debug("Added agent {} to capability-based team for role {}", bestAgent.getName(), role.getName());
            }
        }
        
        finalizeTeam(team);
        return team;
    }
    
    /**
     * Generate a team optimized for performance.
     *
     * @param task The task for which to form a team
     * @return The formed team
     */
    private Team generatePerformanceBasedTeam(Task task) {
        Team team = createBaseTeam(task, "Performance-Optimized");
        
        // Get all available agents
        List<Agent> availableAgents = agentRepository.findByAvailableTrue();
        
        // For each required role, find the agent with the best performance
        for (Role role : task.getRequiredRoles()) {
            Agent bestAgent = findBestAgentByPerformance(role, task.getRequiredCapabilities(), availableAgents, team);
            
            if (bestAgent != null) {
                team.getAgents().add(bestAgent);
                availableAgents.remove(bestAgent);
                logger.debug("Added agent {} to performance-based team for role {}", bestAgent.getName(), role.getName());
            }
        }
        
        finalizeTeam(team);
        return team;
    }
    
    /**
     * Generate a team optimized for cost efficiency.
     *
     * @param task The task for which to form a team
     * @return The formed team
     */
    private Team generateCostOptimizedTeam(Task task) {
        Team team = createBaseTeam(task, "Cost-Optimized");
        
        // Get all available agents
        List<Agent> availableAgents = agentRepository.findByAvailableTrue();
        
        // For each required role, find the agent with the best cost efficiency
        for (Role role : task.getRequiredRoles()) {
            Agent bestAgent = findBestAgentByCost(role, task.getRequiredCapabilities(), availableAgents, team);
            
            if (bestAgent != null) {
                team.getAgents().add(bestAgent);
                availableAgents.remove(bestAgent);
                logger.debug("Added agent {} to cost-optimized team for role {}", bestAgent.getName(), role.getName());
            }
        }
        
        finalizeTeam(team);
        return team;
    }
    
    /**
     * Generate a team optimized for specialization.
     *
     * @param task The task for which to form a team
     * @return The formed team
     */
    private Team generateSpecializationBasedTeam(Task task) {
        Team team = createBaseTeam(task, "Specialization-Optimized");
        
        // Get all available agents
        List<Agent> availableAgents = agentRepository.findByAvailableTrue();
        
        // For each required role, find the agent with the best specialization match
        for (Role role : task.getRequiredRoles()) {
            Agent bestAgent = findBestAgentBySpecialization(role, task.getRequiredCapabilities(), availableAgents, team);
            
            if (bestAgent != null) {
                team.getAgents().add(bestAgent);
                availableAgents.remove(bestAgent);
                logger.debug("Added agent {} to specialization-based team for role {}", bestAgent.getName(), role.getName());
            }
        }
        
        finalizeTeam(team);
        return team;
    }
    
    /**
     * Generate a team with a balanced approach.
     *
     * @param task The task for which to form a team
     * @return The formed team
     */
    private Team generateBalancedTeam(Task task) {
        Team team = createBaseTeam(task, "Balanced");
        
        // Get all available agents
        List<Agent> availableAgents = agentRepository.findByAvailableTrue();
        
        // For each required role, find the agent with the best balanced score
        for (Role role : task.getRequiredRoles()) {
            Agent bestAgent = findBestAgentBalanced(role, task.getRequiredCapabilities(), availableAgents, team);
            
            if (bestAgent != null) {
                team.getAgents().add(bestAgent);
                availableAgents.remove(bestAgent);
                logger.debug("Added agent {} to balanced team for role {}", bestAgent.getName(), role.getName());
            }
        }
        
        finalizeTeam(team);
        return team;
    }
    
    /**
     * Create a base team object.
     *
     * @param task The task for which to create a team
     * @param strategyName The name of the strategy used
     * @return A new team object
     */
    private Team createBaseTeam(Task task, String strategyName) {
        Team team = new Team();
        team.setName(strategyName + " Team for " + task.getName());
        team.setCreatedAt(LocalDateTime.now());
        team.setTask(task);
        team.setAgents(new HashSet<>());
        team.setFormationStrategy(strategyName);
        return team;
    }
    
    /**
     * Finalize a team by setting its status and metrics.
     *
     * @param team The team to finalize
     */
    private void finalizeTeam(Team team) {
        // Set team status based on completeness
        if (team.getAgents().size() >= team.getTask().getRequiredRoles().size()) {
            team.setStatus("COMPLETE");
        } else {
            team.setStatus("PARTIAL");
        }
        
        // Calculate and set performance metrics
        Map<String, Double> metrics = new HashMap<>();
        metrics.put("capabilityCoverage", calculateCapabilityCoverage(team));
        metrics.put("performanceRating", calculateTeamPerformance(team));
        metrics.put("costEfficiency", calculateCostEfficiency(team));
        metrics.put("specialization", calculateSpecializationScore(team));
        metrics.put("compositeScore", calculateTeamCompositeScore(team));
        
        team.setPerformanceMetrics(metrics);
    }
    
    /**
     * Find the best agent for a role based on capability matching.
     *
     * @param role The role to fill
     * @param requiredCapabilities The capabilities required for the task
     * @param availableAgents The available agents
     * @param currentTeam The current team being formed
     * @return The best agent for the role, or null if no suitable agent is found
     */
    private Agent findBestAgentByCapability(Role role, Set<Capability> requiredCapabilities, 
                                          List<Agent> availableAgents, Team currentTeam) {
        Agent bestAgent = null;
        double bestScore = 0.0;
        
        for (Agent agent : availableAgents) {
            if (currentTeam.getAgents().contains(agent)) {
                continue;
            }
            
            // Calculate capability match score
            double capabilityScore = calculateCapabilityMatchScore(agent, requiredCapabilities);
            
            // Skip agents that don't meet the minimum capability threshold
            if (capabilityScore < capabilityMatchThreshold) {
                continue;
            }
            
            if (capabilityScore > bestScore) {
                bestScore = capabilityScore;
                bestAgent = agent;
            }
        }
        
        return bestAgent;
    }
    
    /**
     * Find the best agent for a role based on performance.
     *
     * @param role The role to fill
     * @param requiredCapabilities The capabilities required for the task
     * @param availableAgents The available agents
     * @param currentTeam The current team being formed
     * @return The best agent for the role, or null if no suitable agent is found
     */
    private Agent findBestAgentByPerformance(Role role, Set<Capability> requiredCapabilities, 
                                           List<Agent> availableAgents, Team currentTeam) {
        Agent bestAgent = null;
        double bestScore = 0.0;
        
        for (Agent agent : availableAgents) {
            if (currentTeam.getAgents().contains(agent)) {
                continue;
            }
            
            // Calculate capability match score
            double capabilityScore = calculateCapabilityMatchScore(agent, requiredCapabilities);
            
            // Skip agents that don't meet the minimum capability threshold
            if (capabilityScore < capabilityMatchThreshold) {
                continue;
            }
            
            // Calculate performance score
            double performanceScore = agent.getPerformanceRating() / 10.0; // Normalize to 0-1
            
            // Combined score with heavy weight on performance
            double combinedScore = capabilityScore * 0.3 + performanceScore * 0.7;
            
            if (combinedScore > bestScore) {
                bestScore = combinedScore;
                bestAgent = agent;
            }
        }
        
        return bestAgent;
    }
    
    /**
     * Find the best agent for a role based on cost efficiency.
     *
     * @param role The role to fill
     * @param requiredCapabilities The capabilities required for the task
     * @param availableAgents The available agents
     * @param currentTeam The current team being formed
     * @return The best agent for the role, or null if no suitable agent is found
     */
    private Agent findBestAgentByCost(Role role, Set<Capability> requiredCapabilities, 
                                    List<Agent> availableAgents, Team currentTeam) {
        Agent bestAgent = null;
        double bestScore = 0.0;
        
        for (Agent agent : availableAgents) {
            if (currentTeam.getAgents().contains(agent)) {
                continue;
            }
            
            // Calculate capability match score
            double capabilityScore = calculateCapabilityMatchScore(agent, requiredCapabilities);
            
            // Skip agents that don't meet the minimum capability threshold
            if (capabilityScore < capabilityMatchThreshold) {
                continue;
            }
            
            // Calculate cost efficiency (higher is better)
            double costEfficiency = 1.0 - Math.min(1.0, agent.getCostPerToken() / 0.01); // Normalize to 0-1
            
            // Combined score with heavy weight on cost efficiency
            double combinedScore = capabilityScore * 0.3 + costEfficiency * 0.7;
            
            if (combinedScore > bestScore) {
                bestScore = combinedScore;
                bestAgent = agent;
            }
        }
        
        return bestAgent;
    }
    
    /**
     * Find the best agent for a role based on specialization.
     *
     * @param role The role to fill
     * @param requiredCapabilities The capabilities required for the task
     * @param availableAgents The available agents
     * @param currentTeam The current team being formed
     * @return The best agent for the role, or null if no suitable agent is found
     */
    private Agent findBestAgentBySpecialization(Role role, Set<Capability> requiredCapabilities, 
                                              List<Agent> availableAgents, Team currentTeam) {
        Agent bestAgent = null;
        double bestScore = 0.0;
        
        for (Agent agent : availableAgents) {
            if (currentTeam.getAgents().contains(agent)) {
                continue;
            }
            
            // Calculate capability match score
            double capabilityScore = calculateCapabilityMatchScore(agent, requiredCapabilities);
            
            // Skip agents that don't meet the minimum capability threshold
            if (capabilityScore < capabilityMatchThreshold) {
                continue;
            }
            
            // Calculate specialization score
            double specializationScore = calculateSpecializationMatchScore(agent, role);
            
            // Combined score with heavy weight on specialization
            double combinedScore = capabilityScore * 0.3 + specializationScore * 0.7;
            
            if (combinedScore > bestScore) {
                bestScore = combinedScore;
                bestAgent = agent;
            }
        }
        
        return bestAgent;
    }
    
    /**
     * Find the best agent for a role using a balanced approach.
     *
     * @param role The role to fill
     * @param requiredCapabilities The capabilities required for the task
     * @param availableAgents The available agents
     * @param currentTeam The current team being formed
     * @return The best agent for the role, or null if no suitable agent is found
     */
    private Agent findBestAgentBalanced(Role role, Set<Capability> requiredCapabilities, 
                                      List<Agent> availableAgents, Team currentTeam) {
        Agent bestAgent = null;
        double bestScore = 0.0;
        
        for (Agent agent : availableAgents) {
            if (currentTeam.getAgents().contains(agent)) {
                continue;
            }
            
            // Calculate capability match score
            double capabilityScore = calculateCapabilityMatchScore(agent, requiredCapabilities);
            
            // Skip agents that don't meet the minimum capability threshold
            if (capabilityScore < capabilityMatchThreshold) {
                continue;
            }
            
            // Calculate performance score
            double performanceScore = agent.getPerformanceRating() / 10.0; // Normalize to 0-1
            
            // Calculate specialization score
            double specializationScore = calculateSpecializationMatchScore(agent, role);
            
            // Calculate cost efficiency
            double costEfficiency = 1.0 - Math.min(1.0, agent.getCostPerToken() / 0.01); // Normalize to 0-1
            
            // Combined score with balanced weights
            double combinedScore = capabilityScore * 0.4 + 
                                  performanceScore * 0.25 + 
                                  specializationScore * 0.25 + 
                                  costEfficiency * 0.1;
            
            if (combinedScore > bestScore) {
                bestScore = combinedScore;
                bestAgent = agent;
            }
        }
        
        return bestAgent;
    }
    
    /**
     * Calculate how well an agent's capabilities match the required capabilities.
     *
     * @param agent The agent to evaluate
     * @param requiredCapabilities The capabilities required for the task
     * @return A score between 0 and 1 representing the capability match
     */
    private double calculateCapabilityMatchScore(Agent agent, Set<Capability> requiredCapabilities) {
        if (requiredCapabilities.isEmpty()) {
            return 1.0;
        }
        
        Set<String> agentCapabilityIds = agent.getCapabilities().stream()
                .map(Capability::getId)
                .collect(Collectors.toSet());
                
        Set<String> requiredCapabilityIds = requiredCapabilities.stream()
                .map(Capability::getId)
                .collect(Collectors.toSet());
        
        // Count how many required capabilities the agent has
        long matchCount = requiredCapabilityIds.stream()
                .filter(agentCapabilityIds::contains)
                .count();
        
        return (double) matchCount / requiredCapabilityIds.size();
    }
    
    /**
     * Calculate how well an agent's specialization matches a role.
     *
     * @param agent The agent to evaluate
     * @param role The role to match against
     * @return A score between 0 and 1 representing the specialization match
     */
    private double calculateSpecializationMatchScore(Agent agent, Role role) {
        if (agent.getSpecialization().equals(role.getName())) {
            return 1.0;
        }
        
        // Check for partial matches in specialization
        if (agent.getSpecialization().contains(role.getName()) || 
            role.getName().contains(agent.getSpecialization())) {
            return 0.7;
        }
        
        // Check for related specializations based on role categories
        Set<String> roleCategories = role.getCategories();
        if (roleCategories.contains(agent.getSpecialization())) {
            return 0.5;
        }
        
        return 0.1;
    }
    
    /**
     * Calculate how well a team covers the required capabilities for a task.
     *
     * @param team The team to evaluate
     * @return A score between 0 and 1 representing the capability coverage
     */
    private double calculateCapabilityCoverage(Team team) {
        Task task = team.getTask();
        if (task == null || task.getRequiredCapabilities().isEmpty()) {
            return 1.0;
        }
        
        // Collect all capabilities from team members
        Set<String> teamCapabilityIds = new HashSet<>();
        for (Agent agent : team.getAgents()) {
            teamCapabilityIds.addAll(agent.getCapabilities().stream()
                    .map(Capability::getId)
                    .collect(Collectors.toSet()));
        }
        
        // Calculate coverage
        Set<String> requiredCapabilityIds = task.getRequiredCapabilities().stream()
                .map(Capability::getId)
                .collect(Collectors.toSet());
        
        long coveredCount = requiredCapabilityIds.stream()
                .filter(teamCapabilityIds::contains)
                .count();
        
        return (double) coveredCount / requiredCapabilityIds.size();
    }
    
    /**
     * Calculate the overall performance rating of a team.
     *
     * @param team The team to evaluate
     * @return A score representing the team's performance
     */
    private double calculateTeamPerformance(Team team) {
        if (team.getAgents().isEmpty()) {
            return 0.0;
        }
        
        // Average of all agent performance ratings
        return team.getAgents().stream()
                .mapToDouble(Agent::getPerformanceRating)
                .average()
                .orElse(0.0) / 10.0; // Normalize to 0-1
    }
    
    /**
     * Calculate the cost efficiency of a team.
     *
     * @param team The team to evaluate
     * @return A score representing the team's cost efficiency (higher is better)
     */
    private double calculateCostEfficiency(Team team) {
        if (team.getAgents().isEmpty()) {
            return 0.0;
        }
        
        // Average cost per token (lower is better)
        double avgCost = team.getAgents().stream()
                .mapToDouble(Agent::getCostPerToken)
                .average()
                .orElse(0.0);
        
        // Normalize to 0-1 (higher is better)
        return 1.0 - Math.min(1.0, avgCost / 0.01);
    }
    
    /**
     * Calculate the specialization score of a team.
     *
     * @param team The team to evaluate
     * @return A score representing how well the team's agents match their roles
     */
    private double calculateSpecializationScore(Team team) {
        Task task = team.getTask();
        if (task == null || task.getRequiredRoles().isEmpty() || team.getAgents().isEmpty()) {
            return 0.0;
        }
        
        double totalScore = 0.0;
        int matchCount = 0;
        
        // For each role, find the best matching agent
        for (Role role : task.getRequiredRoles()) {
            double bestMatch = 0.0;
            
            for (Agent agent : team.getAgents()) {
                double match = calculateSpecializationMatchScore(agent, role);
                bestMatch = Math.max(bestMatch, match);
            }
            
            if (bestMatch > 0.0) {
                totalScore += bestMatch;
                matchCount++;
            }
        }
        
        return matchCount > 0 ? totalScore / matchCount : 0.0;
    }
    
    /**
     * Calculate a composite score for a team.
     *
     * @param team The team to evaluate
     * @return A composite score representing the team's overall quality
     */
    private double calculateTeamCompositeScore(Team team) {
        double capabilityCoverage = calculateCapabilityCoverage(team);
        double performanceRating = calculateTeamPerformance(team);
        double costEfficiency = calculateCostEfficiency(team);
        double specialization = calculateSpecializationScore(team);
        
        // Weighted composite score
        return capabilityCoverage * 0.4 + 
               performanceRating * 0.3 + 
               specialization * 0.2 + 
               costEfficiency * 0.1;
    }
    
    /**
     * Analyze team formation history to extract insights and patterns.
     *
     * @return A map of analysis results
     */
    public Map<String, Object> analyzeTeamFormationHistory() {
        List<Team> teamHistory = teamRepository.findAll();
        
        Map<String, Object> analysis = new HashMap<>();
        
        // Basic statistics
        analysis.put("totalTeamsFormed", teamHistory.size());
        analysis.put("completeTeams", teamHistory.stream()
                .filter(t -> "COMPLETE".equals(t.getStatus()))
                .count());
        analysis.put("partialTeams", teamHistory.stream()
                .filter(t -> "PARTIAL".equals(t.getStatus()))
                .count());
        
        // Performance metrics
        if (!teamHistory.isEmpty()) {
            OptionalDouble avgPerformance = teamHistory.stream()
                    .filter(t -> t.getPerformanceMetrics() != null && t.getPerformanceMetrics().containsKey("performanceRating"))
                    .mapToDouble(t -> t.getPerformanceMetrics().get("performanceRating"))
                    .average();
            
            analysis.put("avgTeamPerformance", avgPerformance.orElse(0.0));
            
            OptionalDouble avgCapabilityCoverage = teamHistory.stream()
                    .filter(t -> t.getPerformanceMetrics() != null && t.getPerformanceMetrics().containsKey("capabilityCoverage"))
                    .mapToDouble(t -> t.getPerformanceMetrics().get("capabilityCoverage"))
                    .average();
            
            analysis.put("avgCapabilityCoverage", avgCapabilityCoverage.orElse(0.0));
        }
        
        // Agent utilization
        Map<String, Long> agentUtilization = teamHistory.stream()
                .flatMap(t -> t.getAgents().stream())
                .collect(Collectors.groupingBy(Agent::getId, Collectors.counting()));
        
        analysis.put("agentUtilization", agentUtilization);
        
        // Most utilized agents
        if (!agentUtilization.isEmpty()) {
            List<Map.Entry<String, Long>> mostUtilizedAgents = agentUtilization.entrySet().stream()
                    .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                    .limit(5)
                    .collect(Collectors.toList());
            
            analysis.put("mostUtilizedAgents", mostUtilizedAgents);
        }
        
        // Strategy effectiveness
        Map<String, Double> strategyPerformance = new HashMap<>();
        
        for (Team team : teamHistory) {
            String strategy = team.getFormationStrategy();
            if (strategy != null && team.getPerformanceMetrics() != null && 
                team.getPerformanceMetrics().containsKey("compositeScore")) {
                
                double score = team.getPerformanceMetrics().get("compositeScore");
                strategyPerformance.put(strategy, 
                        strategyPerformance.getOrDefault(strategy, 0.0) + score);
            }
        }
        
        analysis.put("strategyPerformance", strategyPerformance);
        
        return analysis;
    }
    
    /**
     * Update agent collaboration scores based on team performance.
     *
     * @param teamId The ID of the team
     * @param successRating A rating of how successful the team was (0.0 to 1.0)
     */
    @Transactional
    public void updateAgentCollaborationScores(Long teamId, double successRating) {
        Team team = teamRepository.findById(teamId)
                .orElseThrow(() -> new NoSuchElementException("Team not found with ID: " + teamId));
        
        // Validate success rating
        if (successRating < 0.0 || successRating > 1.0) {
            throw new IllegalArgumentException("Success rating must be between 0.0 and 1.0");
        }
        
        // Update collaboration scores for all agents in the team
        for (Agent agent : team.getAgents()) {
            // Update collaboration score with exponential moving average
            double alpha = 0.3;  // Weight for new observation
            double oldScore = agent.getCollaborationScore();
            double newScore = alpha * successRating + (1 - alpha) * oldScore;
            
            agent.setCollaborationScore(newScore);
            agentRepository.save(agent);
            
            logger.info("Updated collaboration score for agent {}: {:.2f} -> {:.2f}", 
                       agent.getName(), oldScore, newScore);
        }
    }
}
