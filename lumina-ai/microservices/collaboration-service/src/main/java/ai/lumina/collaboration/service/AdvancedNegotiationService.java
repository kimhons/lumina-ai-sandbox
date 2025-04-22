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
 * Advanced implementation of negotiation service that provides sophisticated negotiation
 * capabilities for efficient task allocation and resource management between agents.
 */
@Service
public class AdvancedNegotiationService {

    private static final Logger logger = LoggerFactory.getLogger(AdvancedNegotiationService.class);

    @Autowired
    private NegotiationRepository negotiationRepository;

    @Autowired
    private AgentRepository agentRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Autowired
    private TaskRepository taskRepository;

    @Value("${collaboration.negotiation.max-rounds:10}")
    private int maxRounds;

    @Value("${collaboration.negotiation.timeout-ms:15000}")
    private long timeoutMs;

    @Value("${collaboration.negotiation.conflict-resolution.strategy:PRIORITY_BASED}")
    private String conflictResolutionStrategy;

    @Value("${collaboration.negotiation.conflict-resolution.fallback-strategy:COMPROMISE}")
    private String fallbackStrategy;

    @Value("${collaboration.negotiation.resource-allocation.optimization-enabled:true}")
    private boolean resourceOptimizationEnabled;

    /**
     * Initiates a negotiation process between agents for task allocation or resource management.
     *
     * @param initiatorId The ID of the agent initiating the negotiation
     * @param participantIds The IDs of the participating agents
     * @param subject The subject of the negotiation
     * @param resources The resources being negotiated
     * @param initialProposal The initial proposal
     * @return The created negotiation
     */
    @Transactional
    public Negotiation initiateNegotiation(String initiatorId, List<String> participantIds, 
                                          String subject, Map<String, Object> resources,
                                          Map<String, Object> initialProposal) {
        logger.info("Initiating negotiation by agent {} with {} participants on subject: {}", 
                   initiatorId, participantIds.size(), subject);
        
        // Validate participants
        Agent initiator = agentRepository.findById(initiatorId)
                .orElseThrow(() -> new NoSuchElementException("Initiator agent not found with ID: " + initiatorId));
        
        List<Agent> participants = new ArrayList<>();
        for (String participantId : participantIds) {
            Agent participant = agentRepository.findById(participantId)
                    .orElseThrow(() -> new NoSuchElementException("Participant agent not found with ID: " + participantId));
            participants.add(participant);
        }
        
        // Create negotiation
        Negotiation negotiation = new Negotiation();
        negotiation.setInitiatorId(initiatorId);
        negotiation.setParticipantIds(new HashSet<>(participantIds));
        negotiation.setSubject(subject);
        negotiation.setResources(resources);
        negotiation.setStatus("INITIATED");
        negotiation.setStartTime(LocalDateTime.now());
        negotiation.setCurrentRound(1);
        negotiation.setMaxRounds(maxRounds);
        negotiation.setTimeoutMs(timeoutMs);
        
        // Initialize messages with initial proposal
        List<Map<String, Object>> messages = new ArrayList<>();
        Map<String, Object> initialMessage = new HashMap<>();
        initialMessage.put("sender", initiatorId);
        initialMessage.put("type", "PROPOSAL");
        initialMessage.put("content", initialProposal);
        initialMessage.put("timestamp", LocalDateTime.now());
        messages.add(initialMessage);
        negotiation.setMessages(messages);
        
        // Initialize proposals state
        Map<String, Object> proposals = new HashMap<>();
        proposals.put(initiatorId, initialProposal);
        negotiation.setProposals(proposals);
        
        // Initialize state
        negotiation.setState(new HashMap<>());
        negotiation.getState().put("currentProposal", initialProposal);
        
        return negotiationRepository.save(negotiation);
    }
    
    /**
     * Submits a response to an ongoing negotiation.
     *
     * @param negotiationId The ID of the negotiation
     * @param agentId The ID of the agent submitting the response
     * @param responseType The type of response (COUNTER_PROPOSAL, ACCEPT, REJECT, etc.)
     * @param content The content of the response
     * @return The updated negotiation
     */
    @Transactional
    public Negotiation submitNegotiationResponse(String negotiationId, String agentId, 
                                               String responseType, Map<String, Object> content) {
        Negotiation negotiation = negotiationRepository.findById(negotiationId)
                .orElseThrow(() -> new NoSuchElementException("Negotiation not found with ID: " + negotiationId));
        
        // Validate agent is a participant
        if (!negotiation.getParticipantIds().contains(agentId) && !negotiation.getInitiatorId().equals(agentId)) {
            throw new IllegalArgumentException("Agent is not a participant in this negotiation");
        }
        
        // Validate negotiation is still active
        if (!"INITIATED".equals(negotiation.getStatus()) && !"IN_PROGRESS".equals(negotiation.getStatus())) {
            throw new IllegalStateException("Negotiation is no longer active");
        }
        
        // Update negotiation status if it was just initiated
        if ("INITIATED".equals(negotiation.getStatus())) {
            negotiation.setStatus("IN_PROGRESS");
        }
        
        // Add message
        Map<String, Object> message = new HashMap<>();
        message.put("sender", agentId);
        message.put("type", responseType);
        message.put("content", content);
        message.put("timestamp", LocalDateTime.now());
        negotiation.getMessages().add(message);
        
        // Update proposals if it's a counter-proposal
        if ("COUNTER_PROPOSAL".equals(responseType)) {
            negotiation.getProposals().put(agentId, content);
            negotiation.getState().put("currentProposal", content);
            
            // Increment round if all participants have responded
            if (haveAllParticipantsResponded(negotiation)) {
                negotiation.setCurrentRound(negotiation.getCurrentRound() + 1);
                
                // Check if max rounds reached
                if (negotiation.getCurrentRound() > negotiation.getMaxRounds()) {
                    resolveNegotiationWithConflictResolution(negotiation);
                }
            }
        } else if ("ACCEPT".equals(responseType)) {
            // Mark this agent as accepting the current proposal
            Map<String, Boolean> acceptances = (Map<String, Boolean>) negotiation.getState()
                    .getOrDefault("acceptances", new HashMap<String, Boolean>());
            acceptances.put(agentId, true);
            negotiation.getState().put("acceptances", acceptances);
            
            // Check if all participants have accepted
            if (haveAllParticipantsAccepted(negotiation)) {
                negotiation.setStatus("SUCCESSFUL");
                negotiation.setEndTime(LocalDateTime.now());
                negotiation.getState().put("finalAgreement", negotiation.getState().get("currentProposal"));
            }
        } else if ("REJECT".equals(responseType)) {
            // If any participant rejects and no further negotiation is possible, fail the negotiation
            if (negotiation.getCurrentRound() >= negotiation.getMaxRounds()) {
                negotiation.setStatus("FAILED");
                negotiation.setEndTime(LocalDateTime.now());
            }
        }
        
        // Check for timeout
        if (isNegotiationTimedOut(negotiation)) {
            negotiation.setStatus("TIMEOUT");
            negotiation.setEndTime(LocalDateTime.now());
            
            // Apply conflict resolution if timeout occurs
            resolveNegotiationWithConflictResolution(negotiation);
        }
        
        return negotiationRepository.save(negotiation);
    }
    
    /**
     * Checks if all participants have responded in the current round.
     *
     * @param negotiation The negotiation to check
     * @return True if all participants have responded, false otherwise
     */
    private boolean haveAllParticipantsResponded(Negotiation negotiation) {
        Set<String> allParticipants = new HashSet<>(negotiation.getParticipantIds());
        allParticipants.add(negotiation.getInitiatorId());
        
        // Get all agents who have submitted proposals
        Set<String> respondedAgents = negotiation.getProposals().keySet();
        
        return respondedAgents.containsAll(allParticipants);
    }
    
    /**
     * Checks if all participants have accepted the current proposal.
     *
     * @param negotiation The negotiation to check
     * @return True if all participants have accepted, false otherwise
     */
    private boolean haveAllParticipantsAccepted(Negotiation negotiation) {
        Map<String, Boolean> acceptances = (Map<String, Boolean>) negotiation.getState()
                .getOrDefault("acceptances", new HashMap<String, Boolean>());
        
        Set<String> allParticipants = new HashSet<>(negotiation.getParticipantIds());
        allParticipants.add(negotiation.getInitiatorId());
        
        // Check if all participants have accepted
        for (String participantId : allParticipants) {
            if (!Boolean.TRUE.equals(acceptances.get(participantId))) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Checks if a negotiation has timed out.
     *
     * @param negotiation The negotiation to check
     * @return True if the negotiation has timed out, false otherwise
     */
    private boolean isNegotiationTimedOut(Negotiation negotiation) {
        LocalDateTime startTime = negotiation.getStartTime();
        long elapsedMs = java.time.Duration.between(startTime, LocalDateTime.now()).toMillis();
        return elapsedMs > negotiation.getTimeoutMs();
    }
    
    /**
     * Resolves a negotiation using the configured conflict resolution strategy.
     *
     * @param negotiation The negotiation to resolve
     */
    private void resolveNegotiationWithConflictResolution(Negotiation negotiation) {
        logger.info("Resolving negotiation {} using strategy: {}", 
                   negotiation.getId(), conflictResolutionStrategy);
        
        Map<String, Object> resolvedProposal;
        
        switch (conflictResolutionStrategy) {
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
            default:
                // Fallback strategy
                resolvedProposal = resolveCompromise(negotiation);
        }
        
        // Update negotiation with resolved proposal
        negotiation.getState().put("finalAgreement", resolvedProposal);
        negotiation.setStatus("SUCCESSFUL");
        negotiation.setEndTime(LocalDateTime.now());
        
        // Add resolution message
        Map<String, Object> resolutionMessage = new HashMap<>();
        resolutionMessage.put("sender", "SYSTEM");
        resolutionMessage.put("type", "RESOLUTION");
        resolutionMessage.put("content", resolvedProposal);
        resolutionMessage.put("timestamp", LocalDateTime.now());
        negotiation.getMessages().add(resolutionMessage);
    }
    
    /**
     * Resolves a negotiation using priority-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolvePriorityBased(Negotiation negotiation) {
        // Get agent priorities (could be based on role, performance, etc.)
        Map<String, Integer> agentPriorities = getAgentPriorities(negotiation);
        
        // Find the agent with highest priority
        String highestPriorityAgent = agentPriorities.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(negotiation.getInitiatorId()); // Default to initiator
        
        // Use the proposal from the highest priority agent
        return (Map<String, Object>) negotiation.getProposals().getOrDefault(
                highestPriorityAgent, negotiation.getState().get("currentProposal"));
    }
    
    /**
     * Resolves a negotiation using compromise-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveCompromise(Negotiation negotiation) {
        // Create a new proposal that combines elements from all proposals
        Map<String, Object> compromiseProposal = new HashMap<>();
        
        // Get all resource keys from all proposals
        Set<String> allResourceKeys = new HashSet<>();
        for (Object proposalObj : negotiation.getProposals().values()) {
            Map<String, Object> proposal = (Map<String, Object>) proposalObj;
            allResourceKeys.addAll(proposal.keySet());
        }
        
        // For each resource, find a compromise value
        for (String key : allResourceKeys) {
            List<Object> allValues = new ArrayList<>();
            for (Object proposalObj : negotiation.getProposals().values()) {
                Map<String, Object> proposal = (Map<String, Object>) proposalObj;
                if (proposal.containsKey(key)) {
                    allValues.add(proposal.get(key));
                }
            }
            
            // Determine compromise value based on type
            if (!allValues.isEmpty()) {
                Object firstValue = allValues.get(0);
                if (firstValue instanceof Number) {
                    // For numbers, use average
                    double sum = 0;
                    for (Object value : allValues) {
                        sum += ((Number) value).doubleValue();
                    }
                    compromiseProposal.put(key, sum / allValues.size());
                } else if (firstValue instanceof Boolean) {
                    // For booleans, use majority vote
                    int trueCount = 0;
                    for (Object value : allValues) {
                        if ((Boolean) value) {
                            trueCount++;
                        }
                    }
                    compromiseProposal.put(key, trueCount > allValues.size() / 2);
                } else {
                    // For strings or other objects, use most frequent value
                    Map<Object, Integer> valueCounts = new HashMap<>();
                    for (Object value : allValues) {
                        valueCounts.put(value, valueCounts.getOrDefault(value, 0) + 1);
                    }
                    Object mostFrequentValue = valueCounts.entrySet().stream()
                            .max(Map.Entry.comparingByValue())
                            .map(Map.Entry::getKey)
                            .orElse(firstValue);
                    compromiseProposal.put(key, mostFrequentValue);
                }
            }
        }
        
        return compromiseProposal;
    }
    
    /**
     * Resolves a negotiation using voting-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveVoting(Negotiation negotiation) {
        // Count votes for each proposal
        Map<Object, Integer> proposalVotes = new HashMap<>();
        
        for (Object proposalObj : negotiation.getProposals().values()) {
            proposalVotes.put(proposalObj, proposalVotes.getOrDefault(proposalObj, 0) + 1);
        }
        
        // Find proposal with most votes
        Map.Entry<Object, Integer> winningProposal = proposalVotes.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .orElse(null);
        
        if (winningProposal != null) {
            return (Map<String, Object>) winningProposal.getKey();
        } else {
            // Fallback to current proposal
            return (Map<String, Object>) negotiation.getState().get("currentProposal");
        }
    }
    
    /**
     * Resolves a negotiation using optimization-based conflict resolution.
     *
     * @param negotiation The negotiation to resolve
     * @return The resolved proposal
     */
    private Map<String, Object> resolveOptimization(Negotiation negotiation) {
        if (!resourceOptimizationEnabled) {
            return resolveCompromise(negotiation);
        }
        
        // This would implement a more sophisticated optimization algorithm
        // For now, we'll use a simplified approach that maximizes overall utility
        
        Map<String, Object> optimizedProposal = new HashMap<>();
        Map<String, Double> resourceUtilities = calculateResourceUtilities(negotiation);
        
        // For each resource, choose the allocation that maximizes utility
        for (String resource : resourceUtilities.keySet()) {
            double bestUtility = Double.NEGATIVE_INFINITY;
            Object bestValue = null;
            
            for (Object proposalObj : negotiation.getProposals().values()) {
                Map<String, Object> proposal = (Map<String, Object>) proposalObj;
                if (proposal.containsKey(resource)) {
                    Object value = proposal.get(resource);
                    double utility = calculateUtilityForResourceValue(resource, value, negotiation);
                    
                    if (utility > bestUtility) {
                        bestUtility = utility;
                        bestValue = value;
                    }
                }
            }
            
            if (bestValue != null) {
                optimizedProposal.put(resource, bestValue);
            }
        }
        
        return optimizedProposal;
    }
    
    /**
     * Calculates the utility of different resources in a negotiation.
     *
     * @param negotiation The negotiation
     * @return A map of resource names to utility values
     */
    private Map<String, Double> calculateResourceUtilities(Negotiation negotiation) {
        Map<String, Double> utilities = new HashMap<>();
        
        // Extract all resource keys from all proposals
        Set<String> allResourceKeys = new HashSet<>();
        for (Object proposalObj : negotiation.getProposals().values()) {
            Map<String, Object> proposal = (Map<String, Object>) proposalObj;
            allResourceKeys.addAll(proposal.keySet());
        }
        
        // Assign utility based on frequency of appearance and priority
        for (String key : allResourceKeys) {
            int frequency = 0;
            for (Object proposalObj : negotiation.getProposals().values()) {
                Map<String, Object> proposal = (Map<String, Object>) proposalObj;
                if (proposal.containsKey(key)) {
                    frequency++;
                }
            }
            
            // Calculate utility based on frequency and resource priority
            double priority = getResourcePriority(key, negotiation);
            utilities.put(key, frequency * priority);
        }
        
        return utilities;
    }
    
    /**
     * Calculates the utility of a specific resource value in a negotiation.
     *
     * @param resource The resource name
     * @param value The resource value
     * @param negotiation The negotiation
     * @return The utility value
     */
    private double calculateUtilityForResourceValue(String resource, Object value, Negotiation negotiation) {
        // This would implement a more sophisticated utility calculation
        // For now, we'll use a simplified approach
        
        double baseUtility = 1.0;
        
        // Count how many agents proposed this value
        int supportCount = 0;
        for (Object proposalObj : negotiation.getProposals().values()) {
            Map<String, Object> proposal = (Map<String, Object>) proposalObj;
            if (proposal.containsKey(resource) && proposal.get(resource).equals(value)) {
                supportCount++;
            }
        }
        
        // Adjust utility based on support
        baseUtility *= (1.0 + supportCount / (double) negotiation.getProposals().size());
        
        return baseUtility;
    }
    
    /**
     * Gets the priority of a resource in a negotiation.
     *
     * @param resource The resource name
     * @param negotiation The negotiation
     * @return The priority value
     */
    private double getResourcePriority(String resource, Negotiation negotiation) {
        // This would be based on the negotiation subject and context
        // For now, return a default priority
        return 1.0;
    }
    
    /**
     * Gets the priorities of agents in a negotiation.
     *
     * @param negotiation The negotiation
     * @return A map of agent IDs to priority values
     */
    private Map<String, Integer> getAgentPriorities(Negotiation negotiation) {
        Map<String, Integer> priorities = new HashMap<>();
        
        // Get all participant IDs including initiator
        Set<String> allParticipants = new HashSet<>(negotiation.getParticipantIds());
        allParticipants.add(negotiation.getInitiatorId());
        
        // Assign priorities based on agent roles and performance
        for (String agentId : allParticipants) {
            Agent agent = agentRepository.findById(agentId).orElse(null);
            if (agent != null) {
                // Initiator gets a slight priority boost
                int priority = (int) (agent.getPerformanceRating() * 10);
                if (agentId.equals(negotiation.getInitiatorId())) {
                    priority += 5;
                }
                priorities.put(agentId, priority);
            } else {
                priorities.put(agentId, 0);
            }
        }
        
        return priorities;
    }
    
    /**
     * Analyzes a completed negotiation to extract insights and patterns.
     *
     * @param negotiationId The ID of the negotiation to analyze
     * @return A map of analysis results
     */
    public Map<String, Object> analyzeNegotiation(String negotiationId) {
        Negotiation negotiation = negotiationRepository.findById(negotiationId)
                .orElseThrow(() -> new NoSuchElementException("Negotiation not found with ID: " + negotiationId));
        
        // Ensure negotiation is completed
        if ("IN_PROGRESS".equals(negotiation.getStatus()) || "INITIATED".equals(negotiation.getStatus())) {
            throw new IllegalStateException("Cannot analyze an ongoing negotiation");
        }
        
        Map<String, Object> analysis = new HashMap<>();
        
        // Basic statistics
        analysis.put("status", negotiation.getStatus());
        analysis.put("duration", java.time.Duration.between(
                negotiation.getStartTime(), 
                negotiation.getEndTime() != null ? negotiation.getEndTime() : LocalDateTime.now()).toMillis());
        analysis.put("rounds", negotiation.getCurrentRound());
        analysis.put("participantCount", negotiation.getParticipantIds().size() + 1); // +1 for initiator
        
        // Message analysis
        List<Map<String, Object>> messages = negotiation.getMessages();
        Map<String, Integer> messageTypeCount = new HashMap<>();
        Map<String, Integer> agentMessageCount = new HashMap<>();
        
        for (Map<String, Object> message : messages) {
            String type = (String) message.get("type");
            String sender = (String) message.get("sender");
            
            messageTypeCount.put(type, messageTypeCount.getOrDefault(type, 0) + 1);
            agentMessageCount.put(sender, agentMessageCount.getOrDefault(sender, 0) + 1);
        }
        
        analysis.put("messageTypeCount", messageTypeCount);
        analysis.put("agentMessageCount", agentMessageCount);
        
        // Proposal evolution analysis
        if ("SUCCESSFUL".equals(negotiation.getStatus())) {
            Map<String, Object> initialProposal = (Map<String, Object>) negotiation.getMessages().get(0).get("content");
            Map<String, Object> finalAgreement = (Map<String, Object>) negotiation.getState().get("finalAgreement");
            
            Map<String, Object> proposalEvolution = new HashMap<>();
            proposalEvolution.put("initialProposal", initialProposal);
            proposalEvolution.put("finalAgreement", finalAgreement);
            proposalEvolution.put("changedKeys", getChangedKeys(initialProposal, finalAgreement));
            
            analysis.put("proposalEvolution", proposalEvolution);
        }
        
        return analysis;
    }
    
    /**
     * Gets the keys that changed between two proposals.
     *
     * @param initialProposal The initial proposal
     * @param finalAgreement The final agreement
     * @return A set of keys that changed
     */
    private Set<String> getChangedKeys(Map<String, Object> initialProposal, Map<String, Object> finalAgreement) {
        Set<String> changedKeys = new HashSet<>();
        
        // Find keys in both proposals with different values
        for (String key : initialProposal.keySet()) {
            if (finalAgreement.containsKey(key)) {
                if (!Objects.equals(initialProposal.get(key), finalAgreement.get(key))) {
                    changedKeys.add(key);
                }
            } else {
                changedKeys.add(key);
            }
        }
        
        // Find keys in final agreement that weren't in initial proposal
        for (String key : finalAgreement.keySet()) {
            if (!initialProposal.containsKey(key)) {
                changedKeys.add(key);
            }
        }
        
        return changedKeys;
    }
}
