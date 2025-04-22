package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.*;
import ai.lumina.collaboration.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Enhanced service for negotiation protocol operations.
 */
@Service
public class ConflictResolutionService {

    private static final Logger logger = LoggerFactory.getLogger(ConflictResolutionService.class);

    @Autowired
    private NegotiationRepository negotiationRepository;

    @Autowired
    private AgentRepository agentRepository;

    @Value("${collaboration.negotiation.default-strategy:COMPROMISE}")
    private String defaultStrategy;

    // Cache for utility functions
    private final Map<String, Map<String, Double>> utilityCache = new ConcurrentHashMap<>();

    /**
     * Resolve a negotiation using the specified conflict resolution strategy.
     *
     * @param negotiation The negotiation to resolve
     * @param strategy The conflict resolution strategy to use
     * @return The resolved negotiation
     */
    @Transactional
    public Negotiation resolveNegotiation(Negotiation negotiation, String strategy) {
        logger.info("Resolving negotiation {} using strategy: {}", negotiation.getId(), strategy);

        if (negotiation.getStatus().equals("SUCCESSFUL") || 
            negotiation.getStatus().equals("FAILED") || 
            negotiation.getStatus().equals("TIMEOUT")) {
            throw new IllegalStateException("Cannot resolve a negotiation that is already completed");
        }

        // Set negotiation to conflict resolution status
        negotiation.setStatus("CONFLICT_RESOLUTION");
        
        // Determine which strategy to use
        String resolutionStrategy = strategy != null ? strategy : 
                                   negotiation.getConflictResolutionStrategy() != null ? 
                                   negotiation.getConflictResolutionStrategy() : 
                                   defaultStrategy;
        
        // Resolve using the appropriate strategy
        Map<String, Object> resolvedProposal = null;
        
        switch (resolutionStrategy) {
            case "PRIORITY_BASED":
                resolvedProposal = resolvePriorityBased(negotiation);
                break;
            case "COMPROMISE":
                resolvedProposal = resolveCompromise(negotiation);
                break;
            case "VOTING":
                resolvedProposal = resolveVoting(negotiation);
                break;
            case "OPTIMIZATION":
                resolvedProposal = resolveOptimization(negotiation);
                break;
            case "FAIR_DIVISION":
                resolvedProposal = resolveFairDivision(negotiation);
                break;
            case "PARETO_OPTIMAL":
                resolvedProposal = resolveParetoOptimal(negotiation);
                break;
            case "NASH_BARGAINING":
                resolvedProposal = resolveNashBargaining(negotiation);
                break;
            default:
                // Default to compromise
                resolvedProposal = resolveCompromise(negotiation);
                break;
        }
        
        if (resolvedProposal != null) {
            // Update negotiation with resolved proposal
            negotiation.setFinalAgreement(resolvedProposal);
            negotiation.setStatus("SUCCESSFUL");
            negotiation.setEndTime(LocalDateTime.now());
            
            // Add resolution message
            NegotiationMessage resolutionMessage = new NegotiationMessage();
            resolutionMessage.setNegotiation(negotiation);
            resolutionMessage.setSenderId("SYSTEM");
            resolutionMessage.setMessageType("RESOLUTION");
            resolutionMessage.setContent(resolvedProposal);
            resolutionMessage.setTimestamp(LocalDateTime.now());
            
            negotiation.getMessages().add(resolutionMessage);
        } else {
            // If resolution failed
            negotiation.setStatus("FAILED");
            negotiation.setEndTime(LocalDateTime.now());
        }
        
        return negotiationRepository.save(negotiation);
    }

    /**
     * Resolve a negotiation using priority-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolvePriorityBased(Negotiation negotiation) {
        // Get participant priorities
        Map<String, Integer> participantPriorities = new HashMap<>();
        
        // Add participants
        for (String participantId : negotiation.getParticipantIds()) {
            Agent agent = agentRepository.findById(participantId)
                    .orElse(null);
            
            if (agent != null) {
                participantPriorities.put(participantId, agent.getPriority());
            }
        }
        
        // Add initiator
        Agent initiator = agentRepository.findById(negotiation.getInitiatorId())
                .orElse(null);
        
        if (initiator != null) {
            participantPriorities.put(negotiation.getInitiatorId(), initiator.getPriority());
        }
        
        if (participantPriorities.isEmpty()) {
            return negotiation.getCurrentProposal();
        }
        
        // Find the participant with highest priority
        String highestPriorityId = Collections.max(
                participantPriorities.entrySet(),
                Map.Entry.comparingByValue()
        ).getKey();
        
        // Use the proposal from the highest priority participant
        return negotiation.getProposals().getOrDefault(highestPriorityId, negotiation.getCurrentProposal());
    }

    /**
     * Resolve a negotiation using compromise-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveCompromise(Negotiation negotiation) {
        // Create a new proposal that combines elements from all proposals
        Map<String, Object> compromiseProposal = new HashMap<>();
        
        // Get all resource keys from all proposals
        Set<String> allKeys = new HashSet<>();
        for (Map<String, Object> proposal : negotiation.getProposals().values()) {
            allKeys.addAll(proposal.keySet());
        }
        
        // For each resource, find a compromise value
        for (String key : allKeys) {
            List<Object> values = new ArrayList<>();
            for (Map<String, Object> proposal : negotiation.getProposals().values()) {
                if (proposal.containsKey(key)) {
                    values.add(proposal.get(key));
                }
            }
            
            if (values.isEmpty()) {
                continue;
            }
            
            // Determine compromise value based on type
            Object firstValue = values.get(0);
            if (firstValue instanceof Number) {
                // For numbers, use average
                double sum = 0;
                for (Object value : values) {
                    sum += ((Number) value).doubleValue();
                }
                compromiseProposal.put(key, sum / values.size());
            } else if (firstValue instanceof Boolean) {
                // For booleans, use majority vote
                int trueCount = 0;
                for (Object value : values) {
                    if ((Boolean) value) {
                        trueCount++;
                    }
                }
                compromiseProposal.put(key, trueCount > values.size() / 2);
            } else {
                // For strings or other objects, use most frequent value
                Map<Object, Integer> valueCounts = new HashMap<>();
                for (Object value : values) {
                    valueCounts.put(value, valueCounts.getOrDefault(value, 0) + 1);
                }
                
                Object mostFrequent = Collections.max(
                        valueCounts.entrySet(),
                        Map.Entry.comparingByValue()
                ).getKey();
                
                compromiseProposal.put(key, mostFrequent);
            }
        }
        
        return compromiseProposal;
    }

    /**
     * Resolve a negotiation using voting-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveVoting(Negotiation negotiation) {
        // Count votes for each proposal
        Map<String, Integer> proposalVotes = new HashMap<>();
        
        for (Map.Entry<String, Map<String, Object>> entry : negotiation.getProposals().entrySet()) {
            // Convert proposal to string representation for comparison
            String proposalKey = entry.getValue().toString();
            proposalVotes.put(proposalKey, proposalVotes.getOrDefault(proposalKey, 0) + 1);
        }
        
        if (proposalVotes.isEmpty()) {
            return negotiation.getCurrentProposal();
        }
        
        // Find proposal with most votes
        String winningProposalKey = Collections.max(
                proposalVotes.entrySet(),
                Map.Entry.comparingByValue()
        ).getKey();
        
        // Find the original proposal that matches this key
        for (Map<String, Object> proposal : negotiation.getProposals().values()) {
            if (proposal.toString().equals(winningProposalKey)) {
                return proposal;
            }
        }
        
        // Fallback to current proposal if no match found
        return negotiation.getCurrentProposal();
    }

    /**
     * Resolve a negotiation using optimization-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveOptimization(Negotiation negotiation) {
        // This would implement a more sophisticated optimization algorithm
        // For now, we'll use a simplified approach that maximizes overall utility
        
        Map<String, Object> optimizedProposal = new HashMap<>();
        Set<String> allKeys = new HashSet<>();
        
        // Collect all keys from all proposals
        for (Map<String, Object> proposal : negotiation.getProposals().values()) {
            allKeys.addAll(proposal.keySet());
        }
        
        // For each key, choose the value that maximizes overall utility
        for (String key : allKeys) {
            Object bestValue = null;
            double bestUtility = Double.NEGATIVE_INFINITY;
            
            // Collect all proposed values for this key
            Set<Object> values = new HashSet<>();
            for (Map<String, Object> proposal : negotiation.getProposals().values()) {
                if (proposal.containsKey(key)) {
                    values.add(proposal.get(key));
                }
            }
            
            // For each possible value, calculate total utility across all participants
            for (Object value : values) {
                double totalUtility = 0;
                
                // Create a test proposal with just this key-value pair
                Map<String, Object> testProposal = new HashMap<>();
                testProposal.put(key, value);
                
                // Calculate utility for all participants
                for (String participantId : negotiation.getParticipantIds()) {
                    Agent agent = agentRepository.findById(participantId).orElse(null);
                    if (agent != null) {
                        // For simplicity, we'll just check if this matches their preference
                        Map<String, Double> preferences = getAgentPreferences(agent);
                        if (preferences.containsKey(key)) {
                            Object preferredValue = preferences.get(key);
                            if (value.equals(preferredValue)) {
                                totalUtility += 1;
                            }
                        }
                    }
                }
                
                // Also check initiator
                Agent initiator = agentRepository.findById(negotiation.getInitiatorId()).orElse(null);
                if (initiator != null) {
                    Map<String, Double> preferences = getAgentPreferences(initiator);
                    if (preferences.containsKey(key)) {
                        Object preferredValue = preferences.get(key);
                        if (value.equals(preferredValue)) {
                            totalUtility += 1;
                        }
                    }
                }
                
                if (totalUtility > bestUtility) {
                    bestUtility = totalUtility;
                    bestValue = value;
                }
            }
            
            if (bestValue != null) {
                optimizedProposal.put(key, bestValue);
            }
        }
        
        return optimizedProposal;
    }

    /**
     * Resolve a negotiation using fair division algorithms.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveFairDivision(Negotiation negotiation) {
        // Simplified implementation of fair division
        // In a real implementation, this would use more sophisticated algorithms
        
        Map<String, Object> fairProposal = new HashMap<>();
        Set<String> allKeys = new HashSet<>();
        
        // Collect all keys from all proposals
        for (Map<String, Object> proposal : negotiation.getProposals().values()) {
            allKeys.addAll(proposal.keySet());
        }
        
        // For each key, allocate based on participant preferences
        for (String key : allKeys) {
            // Collect preferences for this key
            Map<String, Double> preferences = new HashMap<>();
            for (String participantId : negotiation.getParticipantIds()) {
                Agent agent = agentRepository.findById(participantId).orElse(null);
                if (agent != null) {
                    Map<String, Double> agentPreferences = getAgentPreferences(agent);
                    if (agentPreferences.containsKey(key)) {
                        preferences.put(participantId, agentPreferences.get(key));
                    }
                }
            }
            
            // Also check initiator
            Agent initiator = agentRepository.findById(negotiation.getInitiatorId()).orElse(null);
            if (initiator != null) {
                Map<String, Double> initiatorPreferences = getAgentPreferences(initiator);
                if (initiatorPreferences.containsKey(key)) {
                    preferences.put(negotiation.getInitiatorId(), initiatorPreferences.get(key));
                }
            }
            
            if (preferences.isEmpty()) {
                // If no preferences, use compromise
                List<Object> values = new ArrayList<>();
                for (Map<String, Object> proposal : negotiation.getProposals().values()) {
                    if (proposal.containsKey(key)) {
                        values.add(proposal.get(key));
                    }
                }
                
                if (!values.isEmpty()) {
                    if (values.get(0) instanceof Number) {
                        double sum = 0;
                        for (Object value : values) {
                            sum += ((Number) value).doubleValue();
                        }
                        fairProposal.put(key, sum / values.size());
                    } else {
                        fairProposal.put(key, values.get(0));
                    }
                }
            } else {
                // Allocate based on strongest preference
                String strongestPreferenceId = Collections.max(
                        preferences.entrySet(),
                        Map.Entry.comparingByValue()
                ).getKey();
                
                // Use the proposal from the agent with strongest preference
                Map<String, Object> agentProposal = negotiation.getProposals().get(strongestPreferenceId);
                if (agentProposal != null && agentProposal.containsKey(key)) {
                    fairProposal.put(key, agentProposal.get(key));
                }
            }
        }
        
        return fairProposal;
    }

    /**
     * Resolve a negotiation by finding a Pareto optimal solution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveParetoOptimal(Negotiation negotiation) {
        // A Pareto optimal solution is one where no participant can be made better off
        // without making at least one participant worse off
        
        // Start with all proposals
        List<Map<String, Object>> candidateProposals = new ArrayList<>(negotiation.getProposals().values());
        if (candidateProposals.isEmpty()) {
            return negotiation.getCurrentProposal();
        }
        
        // Calculate utilities for all participants for all proposals
        List<Map.Entry<Map<String, Object>, Map<String, Double>>> proposalUtilities = new ArrayList<>();
        
        for (Map<String, Object> proposal : candidateProposals) {
            Map<String, Double> utilities = new HashMap<>();
            
            // Calculate utility for each participant
            for (String participantId : negotiation.getParticipantIds()) {
                Agent agent = agentRepository.findById(participantId).orElse(null);
                if (agent != null) {
                    utilities.put(participantId, calculateUtility(agent, proposal));
                }
            }
            
            // Include initiator
            Agent initiator = agentRepository.findById(negotiation.getInitiatorId()).orElse(null);
            if (initiator != null) {
                utilities.put(negotiation.getInitiatorId(), calculateUtility(initiator, proposal));
            }
            
            proposalUtilities.add(Map.entry(proposal, utilities));
        }
        
        // Find Pareto optimal proposals
        List<Map<String, Object>> paretoOptimal = new ArrayList<>();
        
        for (int i = 0; i < proposalUtilities.size(); i++) {
            Map.Entry<Map<String, Object>, Map<String, Double>> entry1 = proposalUtilities.get(i);
            Map<String, Object> proposal1 = entry1.getKey();
            Map<String, Double> utilities1 = entry1.getValue();
            
            boolean isDominated = false;
            
            for (int j = 0; j < proposalUtilities.size(); j++) {
                if (i == j) continue;
                
                Map.Entry<Map<String, Object>, Map<String, Double>> entry2 = proposalUtilities.get(j);
                Map<String, Double> utilities2 = entry2.getValue();
                
                // Check if proposal2 dominates proposal1
                boolean dominates = true;
                for (Map.Entry<String, Double> utilityEntry : utilities1.entrySet()) {
                    String agentId = utilityEntry.getKey();
                    double utility1 = utilityEntry.getValue();
                    double utility2 = utilities2.getOrDefault(agentId, 0.0);
                    
                    if (utility2 < utility1) {
                        dominates = false;
                        break;
                    }
                }
                
                // If at least one utility is strictly better in proposal2
                boolean strictlyBetter = false;
                for (Map.Entry<String, Double> utilityEntry : utilities2.entrySet()) {
                    String agentId = utilityEntry.getKey();
                    double utility2 = utilityEntry.getValue();
                    double utility1 = utilities1.getOrDefault(agentId, 0.0);
                    
                    if (utility2 > utility1) {
                        strictlyBetter = true;
                        break;
                    }
                }
                
                if (dominates && strictlyBetter) {
                    isDominated = true;
                    break;
                }
            }
            
            if (!isDominated) {
                paretoOptimal.add(proposal1);
            }
        }
        
        if (paretoOptimal.isEmpty()) {
            // If no Pareto optimal solutions found, use compromise
            return resolveCompromise(negotiation);
        }
        
        // Choose the Pareto optimal proposal with highest average utility
        Map<String, Object> bestProposal = null;
        double bestAvgUtility = Double.NEGATIVE_INFINITY;
        
        for (Map<String, Object> proposal : paretoOptimal) {
            double totalUtility = 0;
            int count = 0;
            
            // Calculate utility for each participant
            for (String participantId : negotiation.getParticipantIds()) {
                Agent agent = agentRepository.findById(participantId).orElse(null);
                if (agent != null) {
                    totalUtility += calculateUtility(agent, proposal);
                    count++;
                }
            }
            
            // Include initiator
            Agent initiator = agentRepository.findById(negotiation.getInitiatorId()).orElse(null);
            if (initiator != null) {
                totalUtility += calculateUtility(initiator, proposal);
                count++;
            }
            
            double avgUtility = count > 0 ? totalUtility / count : 0;
            
            if (avgUtility > bestAvgUtility) {
                bestAvgUtility = avgUtility;
                bestProposal = proposal;
            }
        }
        
        return bestProposal != null ? bestProposal : paretoOptimal.get(0);
    }

    /**
     * Resolve a negotiation using the Nash bargaining solution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveNashBargaining(Negotiation negotiation) {
        // The Nash bargaining solution maximizes the product of utility gains
        
        // Include all proposals and the compromise proposal
        List<Map<String, Object>> candidateProposals = new ArrayList<>(negotiation.getProposals().values());
        Map<String, Object> compromiseProposal = resolveCompromise(negotiation);
        candidateProposals.add(compromiseProposal);
        
        if (candidateProposals.isEmpty()) {
            return negotiation.getCurrentProposal();
        }
        
        // Calculate disagreement point (utilities if negotiation fails)
        Map<String, Double> disagreementUtilities = new HashMap<>();
        for (String participantId : negotiation.getParticipantIds()) {
            disagreementUtilities.put(participantId, 0.0);  // Assume zero utility if negotiation fails
        }
        disagreementUtilities.put(negotiation.getInitiatorId(), 0.0);
        
        // Calculate Nash product for each proposal
        Map<String, Object> bestProposal = null;
        double bestNashProduct = Double.NEGATIVE_INFINITY;
        
        for (Map<String, Object> proposal : candidateProposals) {
            double nashProduct = 1.0;
            
            // Calculate utility for each participant
            for (String participantId : negotiation.getParticipantIds()) {
                Agent agent = agentRepository.findById(participantId).orElse(null);
                if (agent != null) {
                    double utility = calculateUtility(agent, proposal);
                    double utilityGain = Math.max(0, utility - disagreementUtilities.getOrDefault(participantId, 0.0));
                    nashProduct *= utilityGain;
                }
            }
            
            // Include initiator
            Agent initiator = agentRepository.findById(negotiation.getInitiatorId()).orElse(null);
            if (initiator != null) {
                double utility = calculateUtility(initiator, proposal);
                double utilityGain = Math.max(0, utility - disagreementUtilities.getOrDefault(negotiation.getInitiatorId(), 0.0));
                nashProduct *= utilityGain;
            }
            
            if (nashProduct > bestNashProduct) {
                bestNashProduct = nashProduct;
                bestProposal = proposal;
            }
        }
        
        return bestProposal != null ? bestProposal : compromiseProposal;
    }

    /**
     * Calculate the utility of a proposal for an agent.
     *
     * @param agent The agent
     * @param proposal The proposal
     * @return The utility value
     */
    private double calculateUtility(Agent agent, Map<String, Object> proposal) {
        Map<String, Double> preferences = getAgentPreferences(agent);
        
        if (preferences.isEmpty()) {
            return 0.0;
        }
        
        double utility = 0.0;
        for (Map.Entry<String, Object> entry : proposal.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();
            
            if (preferences.containsKey(key)) {
                double preference = preferences.get(key);
                
                // Handle different types of values
                if (value instanceof Number && preference != 0) {
                    // For numeric values, utility is higher when closer to preference
                    double numValue = ((Number) value).doubleValue();
                    utility += 1.0 - Math.min(1.0, Math.abs(numValue - preference) / Math.max(1.0, Math.abs(preference)));
                } else if (value.toString().equals(String.valueOf(preference))) {
                    // For exact matches
                    utility += 1.0;
                }
            }
        }
        
        // Normalize by number of preferences
        return utility / Math.max(1, preferences.size());
    }

    /**
     * Get an agent's preferences.
     *
     * @param agent The agent
     * @return A map of preferences
     */
    private Map<String, Double> getAgentPreferences(Agent agent) {
        // Check cache first
        if (utilityCache.containsKey(agent.getId())) {
            return utilityCache.get(agent.getId());
        }
        
        // In a real implementation, this would retrieve preferences from the agent
        // For now, we'll use a simplified approach
        Map<String, Double> preferences = new HashMap<>();
        
        // Example: extract preferences from agent capabilities
        for (Capability capability : agent.getCapabilities()) {
            if (capability.getName().startsWith("PREF_")) {
                String key = capability.getName().substring(5);
                try {
                    double value = Double.parseDouble(capability.getDescription());
                    preferences.put(key, value);
                } catch (NumberFormatException e) {
                    preferences.put(key, 1.0);  // Default value
                }
            }
        }
        
        // Cache the result
        utilityCache.put(agent.getId(), preferences);
        
        return preferences;
    }

    /**
     * Calculate the fairness of a negotiation outcome.
     *
     * @param negotiation The negotiation
     * @return A fairness score between 0 and 1
     */
    public double calculateFairness(Negotiation negotiation) {
        if (!negotiation.getStatus().equals("SUCCESSFUL")) {
            return 0.0;
        }
        
        Map<String, Object> finalAgreement = negotiation.getFinalAgreement();
        Map<String, Double> utilities = new HashMap<>();
        
        // Calculate utilities for all participants
        for (String participantId : negotiation.getParticipantIds()) {
            Agent agent = agentRepository.findById(participantId).orElse(null);
            if (agent != null) {
                utilities.put(participantId, calculateUtility(agent, finalAgreement));
            }
        }
        
        // Include initiator
        Agent initiator = agentRepository.findById(negotiation.getInitiatorId()).orElse(null);
        if (initiator != null) {
            utilities.put(negotiation.getInitiatorId(), calculateUtility(initiator, finalAgreement));
        }
        
        if (utilities.isEmpty()) {
            return 0.0;
        }
        
        // Calculate fairness metrics
        double minUtility = Collections.min(utilities.values());
        double maxUtility = Collections.max(utilities.values());
        
        // Jain's fairness index
        double sumUtilities = utilities.values().stream().mapToDouble(Double::doubleValue).sum();
        double sumSquaredUtilities = utilities.values().stream().mapToDouble(u -> u * u).sum();
        double jainsIndex = (sumUtilities * sumUtilities) / (utilities.size() * sumSquaredUtilities);
        
        // Combine metrics (equal weight)
        double fairness = (minUtility / Math.max(0.001, maxUtility) + jainsIndex) / 2;
        
        return fairness;
    }
}
