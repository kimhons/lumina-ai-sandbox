package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.*;
import ai.lumina.collaboration.repository.AgentRepository;
import ai.lumina.collaboration.repository.CapabilityRepository;
import ai.lumina.collaboration.repository.RoleRepository;
import ai.lumina.collaboration.repository.TeamRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for dynamic team formation capabilities.
 */
@Service
public class TeamFormationService {

    private static final Logger logger = LoggerFactory.getLogger(TeamFormationService.class);

    private final AgentRepository agentRepository;
    private final TeamRepository teamRepository;
    private final RoleRepository roleRepository;
    private final CapabilityRepository capabilityRepository;

    @Autowired
    public TeamFormationService(
            AgentRepository agentRepository,
            TeamRepository teamRepository,
            RoleRepository roleRepository,
            CapabilityRepository capabilityRepository) {
        this.agentRepository = agentRepository;
        this.teamRepository = teamRepository;
        this.roleRepository = roleRepository;
        this.capabilityRepository = capabilityRepository;
    }

    /**
     * Form a team based on task requirements using the specified strategy.
     *
     * @param task The task requiring a team
     * @param strategy The team formation strategy to use
     * @return The formed team
     */
    @Transactional
    public Team formTeam(Task task, String strategy) {
        logger.info("Forming team for task {} using strategy {}", task.getId(), strategy);
        
        // Get available agents
        List<Agent> availableAgents = agentRepository.findByAvailable(true);
        
        if (availableAgents.isEmpty()) {
            logger.warn("No available agents found for team formation");
            throw new IllegalStateException("No available agents available for team formation");
        }
        
        // Create a new team
        Team team = new Team();
        team.setName("Team for " + task.getName());
        team.setDescription("Team formed to handle task: " + task.getName());
        team.setStatus("FORMING");
        team.setCreatedAt(LocalDateTime.now());
        team.setUpdatedAt(LocalDateTime.now());
        
        // Use the appropriate strategy to form the team
        if ("diversity".equalsIgnoreCase(strategy)) {
            formDiverseTeam(team, task, availableAgents);
        } else {
            // Default to capability-based strategy
            formCapabilityBasedTeam(team, task, availableAgents);
        }
        
        // Save the team
        team = teamRepository.save(team);
        
        // Update task with the assigned team
        task.setAssignedTeam(team);
        
        // Set team status based on completeness
        if (isTeamComplete(team)) {
            team.setStatus("ACTIVE");
            teamRepository.save(team);
        }
        
        logger.info("Team formation completed: {}", team.getId());
        return team;
    }

    /**
     * Form a team based on required capabilities.
     *
     * @param team The team to populate
     * @param task The task with requirements
     * @param availableAgents List of available agents
     */
    private void formCapabilityBasedTeam(Team team, Task task, List<Agent> availableAgents) {
        // Define roles based on required capabilities
        List<Role> roles = defineRoles(task.getRequiredCapabilities());
        
        // Save roles and associate with team
        for (Role role : roles) {
            role.setTeam(team);
            roleRepository.save(role);
        }
        
        // Find the best agents for each role
        assignAgentsToRoles(roles, availableAgents, team);
    }

    /**
     * Form a diverse team that covers all required capabilities while maximizing diversity.
     *
     * @param team The team to populate
     * @param task The task with requirements
     * @param availableAgents List of available agents
     */
    private void formDiverseTeam(Team team, Task task, List<Agent> availableAgents) {
        // Define diverse roles
        List<Role> roles = defineDiverseRoles(task.getRequiredCapabilities());
        
        // Save roles and associate with team
        for (Role role : roles) {
            role.setTeam(team);
            roleRepository.save(role);
        }
        
        // Select a minimal set of agents that cover all required capabilities
        Set<String> requiredCapabilities = task.getRequiredCapabilities();
        List<Agent> selectedAgents = selectMinimalAgentSet(availableAgents, requiredCapabilities);
        
        // Add these agents to the team
        for (Agent agent : selectedAgents) {
            addAgentToTeam(agent, team);
        }
        
        // Assign agents to specific roles
        assignDiverseAgentsToRoles(roles, selectedAgents, availableAgents, team);
    }

    /**
     * Define roles based on required capabilities.
     *
     * @param requiredCapabilities The set of required capabilities
     * @return List of defined roles
     */
    private List<Role> defineRoles(Set<String> requiredCapabilities) {
        List<Role> roles = new ArrayList<>();
        
        // Group related capabilities into roles
        Map<String, Set<String>> capabilityGroups = groupCapabilities(requiredCapabilities);
        
        int roleIndex = 0;
        for (Map.Entry<String, Set<String>> entry : capabilityGroups.entrySet()) {
            String roleName = entry.getKey();
            Set<String> capabilities = entry.getValue();
            
            Role role = new Role();
            role.setName(roleName);
            role.setDescription("Role requiring capabilities: " + String.join(", ", capabilities));
            role.setRequiredCapabilities(capabilities);
            role.setPriority(capabilities.size());  // Priority based on number of capabilities
            role.setFilled(false);
            role.setCreatedAt(LocalDateTime.now());
            role.setUpdatedAt(LocalDateTime.now());
            
            roles.add(role);
            roleIndex++;
        }
        
        return roles;
    }

    /**
     * Define diverse roles covering different aspects of the required capabilities.
     *
     * @param requiredCapabilities The set of required capabilities
     * @return List of defined diverse roles
     */
    private List<Role> defineDiverseRoles(Set<String> requiredCapabilities) {
        List<Role> roles = new ArrayList<>();
        
        // Create a coordinator role
        Role coordinatorRole = new Role();
        coordinatorRole.setName("Team Coordinator");
        coordinatorRole.setDescription("Coordinates team activities and ensures task completion");
        Set<String> coordinationCapabilities = new HashSet<>(Arrays.asList("coordination", "planning", "communication"));
        coordinatorRole.setRequiredCapabilities(coordinationCapabilities);
        coordinatorRole.setPriority(3);
        coordinatorRole.setFilled(false);
        coordinatorRole.setCreatedAt(LocalDateTime.now());
        coordinatorRole.setUpdatedAt(LocalDateTime.now());
        roles.add(coordinatorRole);
        
        // Create specialist roles for different capability domains
        Map<String, Set<String>> domains = identifyCapabilityDomains(requiredCapabilities);
        
        int roleIndex = 0;
        for (Map.Entry<String, Set<String>> entry : domains.entrySet()) {
            String domainName = entry.getKey();
            Set<String> domainCapabilities = entry.getValue();
            
            Role role = new Role();
            role.setName(domainName + " Specialist");
            role.setDescription("Specialist in " + domainName + " capabilities");
            role.setRequiredCapabilities(domainCapabilities);
            role.setPriority(2);
            role.setFilled(false);
            role.setCreatedAt(LocalDateTime.now());
            role.setUpdatedAt(LocalDateTime.now());
            
            roles.add(role);
            roleIndex++;
        }
        
        // Create a generalist role to cover any remaining capabilities
        Set<String> coveredCapabilities = new HashSet<>();
        for (Role role : roles) {
            coveredCapabilities.addAll(role.getRequiredCapabilities());
        }
        
        Set<String> remainingCapabilities = new HashSet<>(requiredCapabilities);
        remainingCapabilities.removeAll(coveredCapabilities);
        
        if (!remainingCapabilities.isEmpty()) {
            Role generalistRole = new Role();
            generalistRole.setName("Generalist");
            generalistRole.setDescription("Covers various general capabilities");
            generalistRole.setRequiredCapabilities(remainingCapabilities);
            generalistRole.setPriority(1);
            generalistRole.setFilled(false);
            generalistRole.setCreatedAt(LocalDateTime.now());
            generalistRole.setUpdatedAt(LocalDateTime.now());
            
            roles.add(generalistRole);
        }
        
        return roles;
    }

    /**
     * Group related capabilities together for role definition.
     *
     * @param capabilities The set of capabilities to group
     * @return Map of role names to sets of capabilities
     */
    private Map<String, Set<String>> groupCapabilities(Set<String> capabilities) {
        Map<String, Set<String>> groups = new HashMap<>();
        
        // This is a simplified implementation
        // In a real system, this would use semantic analysis or predefined groupings
        
        Set<String> reasoningCapabilities = new HashSet<>();
        Set<String> memoryCapabilities = new HashSet<>();
        Set<String> specializedCapabilities = new HashSet<>();
        
        for (String capability : capabilities) {
            String capabilityLower = capability.toLowerCase();
            if (capabilityLower.contains("reasoning") || capabilityLower.contains("logic")) {
                reasoningCapabilities.add(capability);
            } else if (capabilityLower.contains("memory") || capabilityLower.contains("recall")) {
                memoryCapabilities.add(capability);
            } else {
                specializedCapabilities.add(capability);
            }
        }
        
        if (!reasoningCapabilities.isEmpty()) {
            groups.put("Reasoning Specialist", reasoningCapabilities);
        }
        
        if (!memoryCapabilities.isEmpty()) {
            groups.put("Memory Specialist", memoryCapabilities);
        }
        
        if (!specializedCapabilities.isEmpty()) {
            groups.put("Domain Specialist", specializedCapabilities);
        }
        
        // If no grouping was possible, create a single "General" role
        if (groups.isEmpty()) {
            groups.put("General", new HashSet<>(capabilities));
        }
        
        return groups;
    }

    /**
     * Identify different domains within the capabilities.
     *
     * @param capabilities The set of capabilities to categorize
     * @return Map of domain names to sets of capabilities
     */
    private Map<String, Set<String>> identifyCapabilityDomains(Set<String> capabilities) {
        Map<String, Set<String>> domains = new HashMap<>();
        domains.put("Reasoning", new HashSet<>());
        domains.put("Memory", new HashSet<>());
        domains.put("Perception", new HashSet<>());
        domains.put("Communication", new HashSet<>());
        domains.put("Domain Knowledge", new HashSet<>());
        
        for (String capability : capabilities) {
            String capabilityLower = capability.toLowerCase();
            if (containsAny(capabilityLower, Arrays.asList("reason", "logic", "inference", "deduction"))) {
                domains.get("Reasoning").add(capability);
            } else if (containsAny(capabilityLower, Arrays.asList("memory", "recall", "storage"))) {
                domains.get("Memory").add(capability);
            } else if (containsAny(capabilityLower, Arrays.asList("perceive", "detect", "sense", "observe"))) {
                domains.get("Perception").add(capability);
            } else if (containsAny(capabilityLower, Arrays.asList("communicate", "language", "express"))) {
                domains.get("Communication").add(capability);
            } else {
                domains.get("Domain Knowledge").add(capability);
            }
        }
        
        // Remove empty domains
        return domains.entrySet().stream()
                .filter(entry -> !entry.getValue().isEmpty())
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    /**
     * Check if a string contains any of the specified substrings.
     *
     * @param str The string to check
     * @param substrings List of substrings to look for
     * @return True if the string contains any of the substrings
     */
    private boolean containsAny(String str, List<String> substrings) {
        return substrings.stream().anyMatch(str::contains);
    }

    /**
     * Assign the best available agents to each role in the team.
     *
     * @param roles List of roles to fill
     * @param availableAgents List of available agents
     * @param team The team being formed
     */
    private void assignAgentsToRoles(List<Role> roles, List<Agent> availableAgents, Team team) {
        // Sort roles by priority (highest first)
        roles.sort(Comparator.comparing(Role::getPriority).reversed());
        
        // Make a copy of available agents to track remaining agents
        List<Agent> remainingAgents = new ArrayList<>(availableAgents);
        
        for (Role role : roles) {
            // Find the best agent for this role
            Map.Entry<Agent, Double> bestMatch = findBestAgentForRole(role, remainingAgents);
            
            if (bestMatch != null && bestMatch.getValue() > 0.5) {  // Threshold for acceptable match
                Agent bestAgent = bestMatch.getKey();
                
                // Assign the agent to the role
                role.setAssignedAgent(bestAgent);
                role.setFilled(true);
                roleRepository.save(role);
                
                // Add the agent to the team if not already present
                addAgentToTeam(bestAgent, team);
                
                // If this is the first role and it has high priority, make this agent the leader
                if (team.getLeader() == null && role.getPriority() > 1) {
                    team.setLeader(bestAgent);
                    teamRepository.save(team);
                }
                
                // Remove the agent from the remaining available agents
                remainingAgents.remove(bestAgent);
            }
        }
    }

    /**
     * Assign agents to maximize diversity while covering all required capabilities.
     *
     * @param roles List of roles to fill
     * @param selectedAgents List of pre-selected agents
     * @param availableAgents List of all available agents
     * @param team The team being formed
     */
    private void assignDiverseAgentsToRoles(List<Role> roles, List<Agent> selectedAgents, 
                                          List<Agent> availableAgents, Team team) {
        // Sort roles by priority
        roles.sort(Comparator.comparing(Role::getPriority).reversed());
        
        // Make a copy of available agents
        List<Agent> remainingAgents = new ArrayList<>(availableAgents);
        remainingAgents.removeAll(selectedAgents);
        
        // Now assign agents to specific roles
        for (Role role : roles) {
            // Find agents that can fill this role
            List<Agent> capableAgents = selectedAgents.stream()
                    .filter(agent -> hasAllCapabilities(agent, role.getRequiredCapabilities()))
                    .collect(Collectors.toList());
            
            if (!capableAgents.isEmpty()) {
                // Choose the agent with the best match for this specific role
                Agent bestAgent = capableAgents.stream()
                        .max(Comparator.comparing(agent -> 
                            calculateCapabilityMatchScore(agent, role.getRequiredCapabilities())))
                        .orElse(null);
                
                if (bestAgent != null) {
                    role.setAssignedAgent(bestAgent);
                    role.setFilled(true);
                    roleRepository.save(role);
                }
            } else {
                // Look for agents from the remaining pool
                for (Agent agent : remainingAgents) {
                    if (hasAllCapabilities(agent, role.getRequiredCapabilities())) {
                        role.setAssignedAgent(agent);
                        role.setFilled(true);
                        roleRepository.save(role);
                        
                        addAgentToTeam(agent, team);
                        selectedAgents.add(agent);
                        remainingAgents.remove(agent);
                        break;
                    }
                }
            }
        }
        
        // If we still don't have a leader, select the agent with highest performance rating
        if (team.getLeader() == null && !selectedAgents.isEmpty()) {
            Agent leader = selectedAgents.stream()
                    .max(Comparator.comparing(Agent::getPerformanceRating))
                    .orElse(selectedAgents.get(0));
            
            team.setLeader(leader);
            teamRepository.save(team);
        }
    }

    /**
     * Find the best agent for a specific role based on capability match and performance.
     *
     * @param role The role to fill
     * @param availableAgents List of available agents
     * @return The best agent and their score, or null if no suitable agent found
     */
    private Map.Entry<Agent, Double> findBestAgentForRole(Role role, List<Agent> availableAgents) {
        Agent bestAgent = null;
        double bestScore = 0.0;
        
        for (Agent agent : availableAgents) {
            // Calculate capability match score
            double capabilityScore = calculateCapabilityMatchScore(agent, role.getRequiredCapabilities());
            
            // Consider performance rating (normalized to 0-1)
            double performanceScore = Math.min(1.0, agent.getPerformanceRating() / 10.0);
            
            // Combined score (weighted average)
            double combinedScore = (0.7 * capabilityScore) + (0.3 * performanceScore);
            
            if (combinedScore > bestScore) {
                bestScore = combinedScore;
                bestAgent = agent;
            }
        }
        
        if (bestAgent != null) {
            return Map.entry(bestAgent, bestScore);
        }
        
        return null;
    }

    /**
     * Calculate how well an agent's capabilities match the requirements.
     *
     * @param agent The agent to evaluate
     * @param requiredCapabilities The set of required capabilities
     * @return A score between 0 and 1 indicating the match quality
     */
    private double calculateCapabilityMatchScore(Agent agent, Set<String> requiredCapabilities) {
        if (requiredCapabilities.isEmpty()) {
            return 1.0;
        }
        
        int matches = 0;
        for (String capability : requiredCapabilities) {
            if (agent.getCapabilities().contains(capability)) {
                matches++;
            }
        }
        
        return (double) matches / requiredCapabilities.size();
    }

    /**
     * Check if an agent has all the specified capabilities.
     *
     * @param agent The agent to check
     * @param capabilities The set of capabilities to check for
     * @return True if the agent has all the specified capabilities
     */
    private boolean hasAllCapabilities(Agent agent, Set<String> capabilities) {
        return agent.getCapabilities().containsAll(capabilities);
    }

    /**
     * Select a minimal set of agents that collectively cover all required capabilities.
     * Uses a greedy algorithm for the set cover problem.
     *
     * @param agents List of available agents
     * @param requiredCapabilities Set of required capabilities
     * @return List of selected agents
     */
    private List<Agent> selectMinimalAgentSet(List<Agent> agents, Set<String> requiredCapabilities) {
        if (requiredCapabilities.isEmpty()) {
            return Collections.emptyList();
        }
        
        List<Agent> selectedAgents = new ArrayList<>();
        Set<String> remainingCapabilities = new HashSet<>(requiredCapabilities);
        List<Agent> remainingAgents = new ArrayList<>(agents);
        
        while (!remainingCapabilities.isEmpty() && !remainingAgents.isEmpty()) {
            // Find the agent that covers the most remaining capabilities
            Agent bestAgent = null;
            int bestCoverage = 0;
            
            for (Agent agent : remainingAgents) {
                Set<String> intersection = new HashSet<>(agent.getCapabilities());
                intersection.retainAll(remainingCapabilities);
                int coverage = intersection.size();
                
                if (coverage > bestCoverage) {
                    bestCoverage = coverage;
                    bestAgent = agent;
                }
            }
            
            if (bestAgent != null && bestCoverage > 0) {
                selectedAgents.add(bestAgent);
                remainingCapabilities.removeAll(bestAgent.getCapabilities());
                remainingAgents.remove(bestAgent);
            } else {
                // No agent can cover more capabilities, break to avoid infinite loop
                break;
            }
        }
        
        return selectedAgents;
    }

    /**
     * Add an agent to a team and update team capabilities.
     *
     * @param agent The agent to add
     * @param team The team to add the agent to
     */
    private void addAgentToTeam(Agent agent, Team team) {
        if (!team.getAgents().contains(agent)) {
            team.getAgents().add(agent);
            team.getCapabilities().addAll(agent.getCapabilities());
            updateTeamPerformanceRating(team);
            teamRepository.save(team);
        }
    }

    /**
     * Update the team's performance rating based on member agents.
     *
     * @param team The team to update
     */
    private void updateTeamPerformanceRating(Team team) {
        if (team.getAgents().isEmpty()) {
            team.setPerformanceRating(0.0);
            return;
        }
        
        // Calculate weighted average of agent performance ratings
        double totalRating = team.getAgents().stream()
                .mapToDouble(Agent::getPerformanceRating)
                .sum();
        
        team.setPerformanceRating(totalRating / team.getAgents().size());
    }

    /**
     * Check if all roles in a team are filled.
     *
     * @param team The team to check
     * @return True if all roles are filled
     */
    private boolean isTeamComplete(Team team) {
        List<Role> roles = roleRepository.findByTeamId(team.getId());
        return roles.stream().allMatch(Role::isFilled);
    }

    /**
     * Get all teams formed by this service.
     *
     * @return List of all teams
     */
    public List<Team> getAllTeams() {
        return teamRepository.findAll();
    }

    /**
     * Get a team by ID.
     *
     * @param teamId The team ID
     * @return The team, or null if not found
     */
    public Team getTeamById(String teamId) {
        return teamRepository.findById(teamId).orElse(null);
    }

    /**
     * Disband a team, making its agents available for other teams.
     *
     * @param teamId The ID of the team to disband
     * @return True if the team was disbanded successfully
     */
    @Transactional
    public boolean disbandTeam(String teamId) {
        Optional<Team> optionalTeam = teamRepository.findById(teamId);
        
        if (optionalTeam.isPresent()) {
            Team team = optionalTeam.get();
            team.setStatus("DISBANDED");
            teamRepository.save(team);
            return true;
        }
        
        return false;
    }

    /**
     * Find suitable teams for a task based on required capabilities.
     *
     * @param requiredCapabilities The set of required capabilities
     * @return List of suitable teams, sorted by performance rating
     */
    public List<Team> findSuitableTeamsForTask(Set<String> requiredCapabilities) {
        List<Team> activeTeams = teamRepository.findByStatus("ACTIVE");
        
        List<Team> suitableTeams = activeTeams.stream()
                .filter(team -> team.getCapabilities().containsAll(requiredCapabilities))
                .sorted(Comparator.comparing(Team::getPerformanceRating).reversed())
                .collect(Collectors.toList());
        
        return suitableTeams;
    }
}
