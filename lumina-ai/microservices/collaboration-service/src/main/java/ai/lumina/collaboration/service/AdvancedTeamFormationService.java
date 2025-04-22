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
 * Advanced implementation of team formation service that provides dynamic team assembly
 * based on task requirements, agent capabilities, and performance metrics.
 */
@Service
public class AdvancedTeamFormationService {

    private static final Logger logger = LoggerFactory.getLogger(AdvancedTeamFormationService.class);

    @Autowired
    private AgentRepository agentRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private CapabilityRepository capabilityRepository;

    @Autowired
    private TaskRepository taskRepository;

    @Value("${collaboration.team.dynamic-formation.capability-match-threshold:0.75}")
    private double capabilityMatchThreshold;

    @Value("${collaboration.team.dynamic-formation.performance-weight:0.6}")
    private double performanceWeight;

    @Value("${collaboration.team.dynamic-formation.specialization-weight:0.4}")
    private double specializationWeight;

    /**
     * Dynamically forms a team based on task requirements, optimizing for capability match,
     * performance history, and specialization.
     *
     * @param task The task for which to form a team
     * @return The formed team
     */
    @Transactional
    public Team formTeamForTask(Task task) {
        logger.info("Forming team for task: {}", task.getName());
        
        // Extract required capabilities from task
        Set<Capability> requiredCapabilities = task.getRequiredCapabilities();
        if (requiredCapabilities.isEmpty()) {
            throw new IllegalArgumentException("Task must have at least one required capability");
        }
        
        // Create a new team
        Team team = new Team();
        team.setName("Team for " + task.getName());
        team.setCreatedAt(LocalDateTime.now());
        team.setTask(task);
        team = teamRepository.save(team);
        
        // Find suitable agents for each required role
        for (Role role : task.getRequiredRoles()) {
            Agent bestAgent = findBestAgentForRole(role, requiredCapabilities, team);
            if (bestAgent != null) {
                team.getAgents().add(bestAgent);
                logger.info("Added agent {} to team for role {}", bestAgent.getName(), role.getName());
            } else {
                logger.warn("Could not find suitable agent for role: {}", role.getName());
            }
        }
        
        // Update team status based on agent assignment
        if (team.getAgents().size() >= task.getRequiredRoles().size()) {
            team.setStatus("COMPLETE");
        } else {
            team.setStatus("PARTIAL");
        }
        
        return teamRepository.save(team);
    }
    
    /**
     * Asynchronously forms a team based on task requirements.
     *
     * @param taskId The ID of the task for which to form a team
     * @return A CompletableFuture containing the formed team
     */
    @Async("collaborationTaskExecutor")
    public CompletableFuture<Team> formTeamForTaskAsync(Long taskId) {
        Task task = taskRepository.findById(taskId)
                .orElseThrow(() -> new NoSuchElementException("Task not found with ID: " + taskId));
        return CompletableFuture.completedFuture(formTeamForTask(task));
    }
    
    /**
     * Finds the best agent for a specific role based on capability matching, performance history,
     * and specialization.
     *
     * @param role The role to fill
     * @param requiredCapabilities The capabilities required for the task
     * @param currentTeam The current team being formed
     * @return The best agent for the role, or null if no suitable agent is found
     */
    @Cacheable(value = "agentRoleMatches", key = "#role.id")
    private Agent findBestAgentForRole(Role role, Set<Capability> requiredCapabilities, Team currentTeam) {
        // Get all available agents
        List<Agent> availableAgents = agentRepository.findByAvailableTrue();
        
        // Filter out agents already in the team
        availableAgents = availableAgents.stream()
                .filter(agent -> !currentTeam.getAgents().contains(agent))
                .collect(Collectors.toList());
        
        // Calculate scores for each agent
        Map<Agent, Double> agentScores = new HashMap<>();
        
        for (Agent agent : availableAgents) {
            // Calculate capability match score
            double capabilityMatchScore = calculateCapabilityMatchScore(agent, requiredCapabilities);
            
            // Skip agents that don't meet the minimum capability threshold
            if (capabilityMatchScore < capabilityMatchThreshold) {
                continue;
            }
            
            // Calculate role match score
            double roleMatchScore = calculateRoleMatchScore(agent, role);
            
            // Calculate performance score
            double performanceScore = agent.getPerformanceRating() / 10.0; // Normalize to 0-1
            
            // Calculate specialization score
            double specializationScore = calculateSpecializationScore(agent, role);
            
            // Calculate final score with weights
            double finalScore = (capabilityMatchScore * 0.4) + 
                               (roleMatchScore * 0.2) +
                               (performanceScore * performanceWeight) + 
                               (specializationScore * specializationWeight);
            
            agentScores.put(agent, finalScore);
        }
        
        // Find agent with highest score
        return agentScores.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);
    }
    
    /**
     * Calculates how well an agent's capabilities match the required capabilities.
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
     * Calculates how well an agent matches a specific role.
     *
     * @param agent The agent to evaluate
     * @param role The role to match against
     * @return A score between 0 and 1 representing the role match
     */
    private double calculateRoleMatchScore(Agent agent, Role role) {
        // Check if agent has the required role capability
        boolean hasRoleCapability = agent.getCapabilities().stream()
                .anyMatch(c -> c.getName().equals(role.getName()) || 
                          c.getDescription().contains(role.getDescription()));
        
        // Base score on whether agent has the role capability
        double baseScore = hasRoleCapability ? 0.8 : 0.2;
        
        // Adjust score based on agent's specialization
        if (agent.getSpecialization().equals(role.getName())) {
            baseScore += 0.2;
        }
        
        return Math.min(baseScore, 1.0);
    }
    
    /**
     * Calculates a specialization score based on how well an agent's specialization
     * matches the required role.
     *
     * @param agent The agent to evaluate
     * @param role The role to match against
     * @return A score between 0 and 1 representing the specialization match
     */
    private double calculateSpecializationScore(Agent agent, Role role) {
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
     * Optimizes an existing team by suggesting agent replacements that could improve
     * overall team performance.
     *
     * @param teamId The ID of the team to optimize
     * @return The optimized team
     */
    @Transactional
    public Team optimizeTeam(Long teamId) {
        Team team = teamRepository.findById(teamId)
                .orElseThrow(() -> new NoSuchElementException("Team not found with ID: " + teamId));
        
        Task task = team.getTask();
        if (task == null) {
            throw new IllegalStateException("Team must have an associated task for optimization");
        }
        
        // Get all available agents not currently in the team
        List<Agent> availableAgents = agentRepository.findByAvailableTrue().stream()
                .filter(agent -> !team.getAgents().contains(agent))
                .collect(Collectors.toList());
        
        // For each agent in the team, check if there's a better replacement
        boolean teamImproved = false;
        Set<Agent> currentAgents = new HashSet<>(team.getAgents());
        
        for (Agent currentAgent : currentAgents) {
            // Find the role this agent is fulfilling
            Role agentRole = findAgentRole(currentAgent, task);
            if (agentRole == null) continue;
            
            // Calculate current agent's score
            double currentScore = calculateAgentRoleScore(currentAgent, agentRole, task.getRequiredCapabilities());
            
            // Find potential replacement with better score
            Agent bestReplacement = null;
            double bestReplacementScore = currentScore;
            
            for (Agent candidate : availableAgents) {
                double candidateScore = calculateAgentRoleScore(candidate, agentRole, task.getRequiredCapabilities());
                if (candidateScore > bestReplacementScore) {
                    bestReplacement = candidate;
                    bestReplacementScore = candidateScore;
                }
            }
            
            // Replace agent if better candidate found
            if (bestReplacement != null) {
                team.getAgents().remove(currentAgent);
                team.getAgents().add(bestReplacement);
                availableAgents.remove(bestReplacement);
                availableAgents.add(currentAgent);
                teamImproved = true;
                
                logger.info("Optimized team by replacing agent {} with {} for role {}", 
                           currentAgent.getName(), bestReplacement.getName(), agentRole.getName());
            }
        }
        
        if (teamImproved) {
            team.setLastOptimizedAt(LocalDateTime.now());
            return teamRepository.save(team);
        }
        
        return team;
    }
    
    /**
     * Finds the role that an agent is fulfilling in a task.
     *
     * @param agent The agent
     * @param task The task
     * @return The role the agent is fulfilling, or null if not found
     */
    private Role findAgentRole(Agent agent, Task task) {
        for (Role role : task.getRequiredRoles()) {
            if (calculateRoleMatchScore(agent, role) > 0.5) {
                return role;
            }
        }
        return null;
    }
    
    /**
     * Calculates a comprehensive score for an agent's suitability for a role.
     *
     * @param agent The agent to evaluate
     * @param role The role to match against
     * @param requiredCapabilities The capabilities required for the task
     * @return A score representing the agent's suitability
     */
    private double calculateAgentRoleScore(Agent agent, Role role, Set<Capability> requiredCapabilities) {
        double capabilityMatchScore = calculateCapabilityMatchScore(agent, requiredCapabilities);
        double roleMatchScore = calculateRoleMatchScore(agent, role);
        double performanceScore = agent.getPerformanceRating() / 10.0;
        double specializationScore = calculateSpecializationScore(agent, role);
        
        return (capabilityMatchScore * 0.4) + 
               (roleMatchScore * 0.2) +
               (performanceScore * performanceWeight) + 
               (specializationScore * specializationWeight);
    }
}
