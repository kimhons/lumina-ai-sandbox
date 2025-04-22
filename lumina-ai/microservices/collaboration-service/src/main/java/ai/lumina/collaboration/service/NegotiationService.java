package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.*;
import ai.lumina.collaboration.repository.NegotiationRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for negotiation protocol capabilities.
 */
@Service
public class NegotiationService {

    private static final Logger logger = LoggerFactory.getLogger(NegotiationService.class);

    private final NegotiationRepository negotiationRepository;

    @Autowired
    public NegotiationService(NegotiationRepository negotiationRepository) {
        this.negotiationRepository = negotiationRepository;
    }

    /**
     * Create a new negotiation session.
     *
     * @param topic Topic of negotiation
     * @param initiatorId ID of the initiating participant
     * @param participants List of participants
     * @param resources List of resources to negotiate
     * @param constraints Optional constraints on the negotiation
     * @param preferences Optional global preferences
     * @param deadline Optional deadline for the negotiation
     * @return The created negotiation session
     */
    @Transactional
    public Negotiation createSession(String topic, String initiatorId, 
                                    List<Agent> participants, 
                                    List<Resource> resources,
                                    Map<String, Object> constraints,
                                    Map<String, Double> preferences,
                                    LocalDateTime deadline) {
        logger.info("Creating negotiation session on topic '{}' initiated by {}", topic, initiatorId);
        
        // Create negotiation session
        Negotiation negotiation = new Negotiation();
        negotiation.setTopic(topic);
        negotiation.setInitiatorId(initiatorId);
        negotiation.setParticipants(new HashSet<>(participants));
        negotiation.setResources(new HashSet<>(resources));
        negotiation.setConstraints(constraints);
        negotiation.setPreferences(preferences);
        negotiation.setDeadline(deadline);
        negotiation.setStatus(NegotiationStatus.INITIATED);
        negotiation.setStartTime(LocalDateTime.now());
        negotiation.setMessages(new ArrayList<>());
        
        // Save and return
        return negotiationRepository.save(negotiation);
    }

    /**
     * Send a message in a negotiation session.
     *
     * @param negotiationId ID of the negotiation session
     * @param message The message to send
     * @return True if the message was sent successfully
     */
    @Transactional
    public boolean sendMessage(String negotiationId, NegotiationMessage message) {
        logger.info("Sending message in negotiation {}: {}", negotiationId, message);
        
        Optional<Negotiation> optionalNegotiation = negotiationRepository.findById(negotiationId);
        if (optionalNegotiation.isEmpty()) {
            logger.error("Negotiation {} not found", negotiationId);
            return false;
        }
        
        Negotiation negotiation = optionalNegotiation.get();
        
        // Check if negotiation is still active
        if (!isActive(negotiation)) {
            logger.warn("Cannot send message to inactive negotiation {}", negotiationId);
            return false;
        }
        
        // Check if sender is a participant
        boolean senderIsParticipant = negotiation.getParticipants().stream()
                .anyMatch(p -> p.getId().equals(message.getSenderId()));
        if (!senderIsParticipant) {
            logger.error("Sender {} is not a participant in negotiation {}", 
                       message.getSenderId(), negotiationId);
            return false;
        }
        
        // Check if receiver is a participant
        boolean receiverIsParticipant = negotiation.getParticipants().stream()
                .anyMatch(p -> p.getId().equals(message.getReceiverId()));
        if (!receiverIsParticipant) {
            logger.error("Receiver {} is not a participant in negotiation {}", 
                       message.getReceiverId(), negotiationId);
            return false;
        }
        
        // Add message to negotiation
        message.setTimestamp(LocalDateTime.now());
        message.setNegotiation(negotiation);
        negotiation.getMessages().add(message);
        
        // Update negotiation status
        if (negotiation.getStatus() == NegotiationStatus.INITIATED) {
            negotiation.setStatus(NegotiationStatus.IN_PROGRESS);
        }
        
        // Check for completion
        checkNegotiationCompletion(negotiation);
        
        // Save and return
        negotiationRepository.save(negotiation);
        return true;
    }

    /**
     * Get a negotiation session by ID.
     *
     * @param negotiationId ID of the negotiation session
     * @return The negotiation session, or empty if not found
     */
    public Optional<Negotiation> getSession(String negotiationId) {
        return negotiationRepository.findById(negotiationId);
    }

    /**
     * Get all active negotiation sessions.
     *
     * @return List of active negotiation sessions
     */
    public List<Negotiation> getActiveSessions() {
        return negotiationRepository.findByStatusIn(
                Arrays.asList(NegotiationStatus.INITIATED, NegotiationStatus.IN_PROGRESS));
    }

    /**
     * End a negotiation session with the specified status and outcome.
     *
     * @param negotiationId ID of the negotiation session
     * @param status Final status of the negotiation
     * @param outcome Optional outcome of the negotiation
     * @return True if the session was ended successfully
     */
    @Transactional
    public boolean endSession(String negotiationId, NegotiationStatus status, 
                            Map<String, Object> outcome) {
        logger.info("Ending negotiation {} with status {}", negotiationId, status);
        
        Optional<Negotiation> optionalNegotiation = negotiationRepository.findById(negotiationId);
        if (optionalNegotiation.isEmpty()) {
            logger.error("Negotiation {} not found", negotiationId);
            return false;
        }
        
        Negotiation negotiation = optionalNegotiation.get();
        
        // Update negotiation
        negotiation.setStatus(status);
        negotiation.setEndTime(LocalDateTime.now());
        negotiation.setOutcome(outcome);
        
        // Save and return
        negotiationRepository.save(negotiation);
        return true;
    }

    /**
     * Generate a proposal using the specified strategy.
     *
     * @param negotiationId ID of the negotiation session
     * @param participantId ID of the participant generating the proposal
     * @param strategyName Name of the strategy to use
     * @return Generated proposal, or empty if generation failed
     */
    public Optional<Map<String, Object>> generateProposal(String negotiationId, 
                                                       String participantId, 
                                                       String strategyName) {
        logger.info("Generating proposal for participant {} in negotiation {} using {} strategy", 
                  participantId, negotiationId, strategyName);
        
        Optional<Negotiation> optionalNegotiation = negotiationRepository.findById(negotiationId);
        if (optionalNegotiation.isEmpty()) {
            logger.error("Negotiation {} not found", negotiationId);
            return Optional.empty();
        }
        
        Negotiation negotiation = optionalNegotiation.get();
        
        // Check if negotiation is active
        if (!isActive(negotiation)) {
            logger.warn("Cannot generate proposal for inactive negotiation {}", negotiationId);
            return Optional.empty();
        }
        
        // Check if participant is in the negotiation
        boolean isParticipant = negotiation.getParticipants().stream()
                .anyMatch(p -> p.getId().equals(participantId));
        if (!isParticipant) {
            logger.error("Participant {} not found in negotiation {}", participantId, negotiationId);
            return Optional.empty();
        }
        
        // Generate proposal based on strategy
        try {
            Map<String, Object> proposal;
            
            if ("collaborative".equalsIgnoreCase(strategyName)) {
                proposal = generateCollaborativeProposal(negotiation, participantId);
            } else {
                // Default to utility-based strategy
                proposal = generateUtilityBasedProposal(negotiation, participantId);
            }
            
            return Optional.of(proposal);
        } catch (Exception e) {
            logger.error("Error generating proposal: {}", e.getMessage(), e);
            return Optional.empty();
        }
    }

    /**
     * Evaluate a proposal using the specified strategy.
     *
     * @param negotiationId ID of the negotiation session
     * @param proposal The proposal to evaluate
     * @param participantId ID of the participant evaluating the proposal
     * @param strategyName Name of the strategy to use
     * @return Evaluation result, or empty if evaluation failed
     */
    public Optional<NegotiationEvaluation> evaluateProposal(String negotiationId, 
                                                         Map<String, Object> proposal, 
                                                         String participantId, 
                                                         String strategyName) {
        logger.info("Evaluating proposal for participant {} in negotiation {} using {} strategy", 
                  participantId, negotiationId, strategyName);
        
        Optional<Negotiation> optionalNegotiation = negotiationRepository.findById(negotiationId);
        if (optionalNegotiation.isEmpty()) {
            logger.error("Negotiation {} not found", negotiationId);
            return Optional.empty();
        }
        
        Negotiation negotiation = optionalNegotiation.get();
        
        // Check if negotiation is active
        if (!isActive(negotiation)) {
            logger.warn("Cannot evaluate proposal for inactive negotiation {}", negotiationId);
            return Optional.empty();
        }
        
        // Check if participant is in the negotiation
        boolean isParticipant = negotiation.getParticipants().stream()
                .anyMatch(p -> p.getId().equals(participantId));
        if (!isParticipant) {
            logger.error("Participant {} not found in negotiation {}", participantId, negotiationId);
            return Optional.empty();
        }
        
        // Evaluate proposal based on strategy
        try {
            NegotiationEvaluation evaluation;
            
            if ("collaborative".equalsIgnoreCase(strategyName)) {
                evaluation = evaluateCollaborativeProposal(negotiation, proposal, participantId);
            } else {
                // Default to utility-based strategy
                evaluation = evaluateUtilityBasedProposal(negotiation, proposal, participantId);
            }
            
            return Optional.of(evaluation);
        } catch (Exception e) {
            logger.error("Error evaluating proposal: {}", e.getMessage(), e);
            return Optional.empty();
        }
    }

    /**
     * Generate a proposal using utility-based strategy.
     *
     * @param negotiation The negotiation session
     * @param participantId ID of the participant generating the proposal
     * @return Generated proposal
     */
    private Map<String, Object> generateUtilityBasedProposal(Negotiation negotiation, String participantId) {
        // Get participant
        Agent participant = negotiation.getParticipants().stream()
                .filter(p -> p.getId().equals(participantId))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Participant not found"));
        
        // Get participant preferences
        Map<String, Double> preferences = getParticipantPreferences(participant);
        
        // Calculate initial proposal based on preferences
        Map<String, Object> proposal = new HashMap<>();
        
        // Adjust based on negotiation round (make concessions in later rounds)
        int roundNum = negotiation.getMessages().size() / negotiation.getParticipants().size();
        double concessionFactor = 0.1;
        double concession = concessionFactor * roundNum;
        
        // For each resource, allocate based on preferences with concession
        for (Resource resource : negotiation.getResources()) {
            String resourceName = resource.getName();
            double preference = preferences.getOrDefault(resourceName, 0.5);
            
            // Adjust preference based on concession
            double adjustedPreference = Math.max(0.0, preference - concession);
            
            // Calculate requested quantity
            double requestedQuantity;
            if (resource.isDivisible()) {
                // For divisible resources, request a portion based on preference
                requestedQuantity = resource.getQuantity() * adjustedPreference;
            } else {
                // For indivisible resources, request all or nothing based on preference threshold
                requestedQuantity = adjustedPreference > 0.5 ? resource.getQuantity() : 0;
            }
            
            Map<String, Object> resourceProposal = new HashMap<>();
            resourceProposal.put("quantity", requestedQuantity);
            resourceProposal.put("type", resource.getType().toString());
            resourceProposal.put("unit", resource.getUnit());
            
            proposal.put(resourceName, resourceProposal);
        }
        
        return proposal;
    }

    /**
     * Generate a proposal using collaborative strategy.
     *
     * @param negotiation The negotiation session
     * @param participantId ID of the participant generating the proposal
     * @return Generated proposal
     */
    private Map<String, Object> generateCollaborativeProposal(Negotiation negotiation, String participantId) {
        // Get all participants' preferences
        Map<String, Map<String, Double>> allPreferences = new HashMap<>();
        for (Agent participant : negotiation.getParticipants()) {
            allPreferences.put(participant.getId(), getParticipantPreferences(participant));
        }
        
        // Calculate fair allocations based on all preferences
        Map<String, Object> proposal = new HashMap<>();
        
        for (Resource resource : negotiation.getResources()) {
            String resourceName = resource.getName();
            
            // Collect preferences for this resource from all participants
            Map<String, Double> resourcePreferences = new HashMap<>();
            for (Map.Entry<String, Map<String, Double>> entry : allPreferences.entrySet()) {
                String pid = entry.getKey();
                Map<String, Double> prefs = entry.getValue();
                resourcePreferences.put(pid, prefs.getOrDefault(resourceName, 0.1));
            }
            
            // Normalize preferences
            double totalPreference = resourcePreferences.values().stream().mapToDouble(Double::doubleValue).sum();
            Map<String, Double> normalizedPreferences;
            
            if (totalPreference > 0) {
                normalizedPreferences = resourcePreferences.entrySet().stream()
                        .collect(Collectors.toMap(
                                Map.Entry::getKey,
                                e -> e.getValue() / totalPreference
                        ));
            } else {
                // Equal distribution if no preferences
                double equalShare = 1.0 / resourcePreferences.size();
                normalizedPreferences = resourcePreferences.entrySet().stream()
                        .collect(Collectors.toMap(
                                Map.Entry::getKey,
                                e -> equalShare
                        ));
            }
            
            // Allocate resource based on normalized preferences
            Map<String, Double> allocations = new HashMap<>();
            
            if (resource.isDivisible()) {
                for (Map.Entry<String, Double> entry : normalizedPreferences.entrySet()) {
                    String pid = entry.getKey();
                    double normPref = entry.getValue();
                    allocations.put(pid, resource.getQuantity() * normPref);
                }
            } else {
                // For indivisible resources, allocate to participant with highest preference
                String maxPrefId = Collections.max(normalizedPreferences.entrySet(),
                        Map.Entry.comparingByValue()).getKey();
                
                for (String pid : normalizedPreferences.keySet()) {
                    allocations.put(pid, pid.equals(maxPrefId) ? resource.getQuantity() : 0);
                }
            }
            
            Map<String, Object> resourceProposal = new HashMap<>();
            resourceProposal.put("allocations", allocations);
            resourceProposal.put("type", resource.getType().toString());
            resourceProposal.put("unit", resource.getUnit());
            
            proposal.put(resourceName, resourceProposal);
        }
        
        return proposal;
    }

    /**
     * Evaluate a proposal using utility-based strategy.
     *
     * @param negotiation The negotiation session
     * @param proposal The proposal to evaluate
     * @param participantId ID of the participant evaluating the proposal
     * @return Evaluation result
     */
    private NegotiationEvaluation evaluateUtilityBasedProposal(Negotiation negotiation, 
                                                            Map<String, Object> proposal, 
                                                            String participantId) {
        // Get participant
        Agent participant = negotiation.getParticipants().stream()
                .filter(p -> p.getId().equals(participantId))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Participant not found"));
        
        // Calculate utility of the proposal
        double utility = calculateUtility(proposal, participant);
        
        // Parameters
        double minUtilityThreshold = 0.6;
        
        // Check if utility meets minimum threshold
        if (utility >= minUtilityThreshold) {
            // Accept the proposal
            return new NegotiationEvaluation(true, null, utility);
        }
        
        // Check if we're near the deadline
        if (negotiation.getDeadline() != null && 
            LocalDateTime.now().isAfter(negotiation.getDeadline().minusSeconds(10))) {
            // If near deadline, be more likely to accept
            if (utility >= minUtilityThreshold * 0.8) {
                return new NegotiationEvaluation(true, null, utility);
            }
        }
        
        // Generate counter-proposal
        Map<String, Object> counterProposal = generateUtilityBasedProposal(negotiation, participantId);
        
        // Blend the original proposal with our counter to move toward agreement
        int roundNum = negotiation.getMessages().size() / negotiation.getParticipants().size();
        double blendFactor = Math.min(0.3 + (roundNum * 0.1), 0.7);  // Increase blend factor in later rounds
        
        Map<String, Object> blendedProposal = new HashMap<>();
        
        for (Map.Entry<String, Object> entry : counterProposal.entrySet()) {
            String resourceName = entry.getKey();
            @SuppressWarnings("unchecked")
            Map<String, Object> counterDetails = (Map<String, Object>) entry.getValue();
            
            if (proposal.containsKey(resourceName)) {
                @SuppressWarnings("unchecked")
                Map<String, Object> origDetails = (Map<String, Object>) proposal.get(resourceName);
                
                // Blend quantities
                double origQuantity = ((Number) origDetails.get("quantity")).doubleValue();
                double counterQuantity = ((Number) counterDetails.get("quantity")).doubleValue();
                double blendedQuantity = (origQuantity * blendFactor) + (counterQuantity * (1 - blendFactor));
                
                Map<String, Object> blendedDetails = new HashMap<>();
                blendedDetails.put("quantity", blendedQuantity);
                blendedDetails.put("type", counterDetails.get("type"));
                blendedDetails.put("unit", counterDetails.get("unit"));
                
                blendedProposal.put(resourceName, blendedDetails);
            } else {
                blendedProposal.put(resourceName, counterDetails);
            }
        }
        
        return new NegotiationEvaluation(false, blendedProposal, utility);
    }

    /**
     * Evaluate a proposal using collaborative strategy.
     *
     * @param negotiation The negotiation session
     * @param proposal The proposal to evaluate
     * @param participantId ID of the participant evaluating the proposal
     * @return Evaluation result
     */
    private NegotiationEvaluation evaluateCollaborativeProposal(Negotiation negotiation, 
                                                             Map<String, Object> proposal, 
                                                             String participantId) {
        // Get participant
        Agent participant = negotiation.getParticipants().stream()
                .filter(p -> p.getId().equals(participantId))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Participant not found"));
        
        // Parameters
        double fairnessWeight = 0.5;
        double collaborationBonus = 0.2;
        
        // Calculate individual utility
        double individualUtility = calculateCollaborativeUtility(proposal, participant);
        
        // Calculate fairness of the proposal
        double fairness = calculateFairness(proposal, negotiation);
        
        // Calculate collaborative utility
        double collaborativeUtility = (
                (1 - fairnessWeight) * individualUtility + 
                fairnessWeight * fairness
        );
        
        // Add collaboration bonus if the proposal is fair
        if (fairness > 0.7) {
            collaborativeUtility += collaborationBonus;
        }
        
        // Accept if collaborative utility is high enough
        if (collaborativeUtility > 0.7) {
            return new NegotiationEvaluation(true, null, collaborativeUtility);
        }
        
        // Generate a more collaborative counter-proposal
        Map<String, Object> counterProposal = generateCollaborativeProposal(negotiation, participantId);
        
        // If we're in later rounds, try to converge by blending proposals
        int roundNum = negotiation.getMessages().size() / negotiation.getParticipants().size();
        if (roundNum > 2) {
            // Blend the original proposal with our counter
            double blendFactor = Math.min(0.4 + (roundNum * 0.1), 0.8);
            
            Map<String, Object> blendedProposal = new HashMap<>();
            
            for (Map.Entry<String, Object> entry : counterProposal.entrySet()) {
                String resourceName = entry.getKey();
                @SuppressWarnings("unchecked")
                Map<String, Object> counterDetails = (Map<String, Object>) entry.getValue();
                
                if (proposal.containsKey(resourceName)) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> origDetails = (Map<String, Object>) proposal.get(resourceName);
                    
                    // Blend allocations
                    @SuppressWarnings("unchecked")
                    Map<String, Double> counterAllocations = (Map<String, Double>) counterDetails.get("allocations");
                    Map<String, Double> blendedAllocations = new HashMap<>();
                    
                    if (origDetails.containsKey("allocations")) {
                        @SuppressWarnings("unchecked")
                        Map<String, Double> origAllocations = (Map<String, Double>) origDetails.get("allocations");
                        
                        for (Map.Entry<String, Double> allocEntry : counterAllocations.entrySet()) {
                            String pid = allocEntry.getKey();
                            double counterAllocation = allocEntry.getValue();
                            
                            if (origAllocations.containsKey(pid)) {
                                double origAllocation = origAllocations.get(pid);
                                blendedAllocations.put(pid, 
                                        origAllocation * blendFactor + counterAllocation * (1 - blendFactor));
                            } else {
                                blendedAllocations.put(pid, counterAllocation);
                            }
                        }
                    } else {
                        blendedAllocations = counterAllocations;
                    }
                    
                    Map<String, Object> blendedDetails = new HashMap<>();
                    blendedDetails.put("allocations", blendedAllocations);
                    blendedDetails.put("type", counterDetails.get("type"));
                    blendedDetails.put("unit", counterDetails.get("unit"));
                    
                    blendedProposal.put(resourceName, blendedDetails);
                } else {
                    blendedProposal.put(resourceName, counterDetails);
                }
            }
            
            return new NegotiationEvaluation(false, blendedProposal, collaborativeUtility);
        }
        
        return new NegotiationEvaluation(false, counterProposal, collaborativeUtility);
    }

    /**
     * Calculate the utility of a proposal for a participant.
     *
     * @param proposal The proposal to evaluate
     * @param participant The participant evaluating the proposal
     * @return Utility value between 0 and 1
     */
    private double calculateUtility(Map<String, Object> proposal, Agent participant) {
        if (proposal == null || proposal.isEmpty()) {
            return 0.0;
        }
        
        Map<String, Double> preferences = getParticipantPreferences(participant);
        if (preferences.isEmpty()) {
            return 0.0;
        }
        
        double totalUtility = 0.0;
        double totalWeight = 0.0;
        
        for (Map.Entry<String, Double> entry : preferences.entrySet()) {
            String resourceName = entry.getKey();
            double preference = entry.getValue();
            
            if (proposal.containsKey(resourceName)) {
                @SuppressWarnings("unchecked")
                Map<String, Object> resourceProposal = (Map<String, Object>) proposal.get(resourceName);
                
                // Get proposed quantity
                double proposedQuantity = ((Number) resourceProposal.get("quantity")).doubleValue();
                
                // Get maximum possible quantity from participant's resources or constraints
                double maxQuantity = getMaxQuantity(participant, resourceName);
                
                // Calculate utility for this resource
                double resourceUtility;
                if (maxQuantity > 0) {
                    resourceUtility = Math.min(proposedQuantity / maxQuantity, 1.0);
                } else {
                    resourceUtility = proposedQuantity > 0 ? 1.0 : 0.0;
                }
                
                // Add to total utility, weighted by preference
                totalUtility += resourceUtility * preference;
                totalWeight += preference;
            }
        }
        
        // Normalize utility
        if (totalWeight > 0) {
            return totalUtility / totalWeight;
        }
        return 0.0;
    }

    /**
     * Calculate the utility of a collaborative proposal for a participant.
     *
     * @param proposal The proposal to evaluate
     * @param participant The participant evaluating the proposal
     * @return Utility value between 0 and 1
     */
    private double calculateCollaborativeUtility(Map<String, Object> proposal, Agent participant) {
        if (proposal == null || proposal.isEmpty()) {
            return 0.0;
        }
        
        Map<String, Double> preferences = getParticipantPreferences(participant);
        if (preferences.isEmpty()) {
            return 0.0;
        }
        
        double totalUtility = 0.0;
        double totalWeight = 0.0;
        
        for (Map.Entry<String, Double> entry : preferences.entrySet()) {
            String resourceName = entry.getKey();
            double preference = entry.getValue();
            
            if (proposal.containsKey(resourceName)) {
                @SuppressWarnings("unchecked")
                Map<String, Object> resourceProposal = (Map<String, Object>) proposal.get(resourceName);
                
                if (resourceProposal.containsKey("allocations")) {
                    @SuppressWarnings("unchecked")
                    Map<String, Double> allocations = (Map<String, Double>) resourceProposal.get("allocations");
                    
                    // Get allocated quantity for this participant
                    double allocatedQuantity = allocations.getOrDefault(participant.getId(), 0.0);
                    
                    // Get maximum possible quantity from participant's resources or constraints
                    double maxQuantity = getMaxQuantity(participant, resourceName);
                    
                    // Calculate utility for this resource
                    double resourceUtility;
                    if (maxQuantity > 0) {
                        resourceUtility = Math.min(allocatedQuantity / maxQuantity, 1.0);
                    } else {
                        resourceUtility = allocatedQuantity > 0 ? 1.0 : 0.0;
                    }
                    
                    // Add to total utility, weighted by preference
                    totalUtility += resourceUtility * preference;
                    totalWeight += preference;
                }
            }
        }
        
        // Normalize utility
        if (totalWeight > 0) {
            return totalUtility / totalWeight;
        }
        return 0.0;
    }

    /**
     * Calculate the fairness of a proposal across all participants.
     *
     * @param proposal The proposal to evaluate
     * @param negotiation The negotiation session
     * @return Fairness value between 0 and 1
     */
    private double calculateFairness(Map<String, Object> proposal, Negotiation negotiation) {
        // Calculate utility for each participant
        Map<String, Double> utilities = new HashMap<>();
        
        for (Agent participant : negotiation.getParticipants()) {
            utilities.put(participant.getId(), calculateCollaborativeUtility(proposal, participant));
        }
        
        if (utilities.isEmpty()) {
            return 0.0;
        }
        
        // Calculate fairness metrics
        double meanUtility = utilities.values().stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        double maxUtility = utilities.values().stream().mapToDouble(Double::doubleValue).max().orElse(0.0);
        double minUtility = utilities.values().stream().mapToDouble(Double::doubleValue).min().orElse(0.0);
        
        // Calculate variance in utilities
        double variance;
        if (utilities.size() > 1) {
            variance = utilities.values().stream()
                    .mapToDouble(u -> Math.pow(u - meanUtility, 2))
                    .sum() / utilities.size();
        } else {
            variance = 0.0;
        }
        
        // Calculate Jain's fairness index
        double jainsIndex;
        double sumOfUtilities = utilities.values().stream().mapToDouble(Double::doubleValue).sum();
        
        if (sumOfUtilities > 0) {
            double squaredSum = Math.pow(sumOfUtilities, 2);
            double sumOfSquares = utilities.values().stream()
                    .mapToDouble(u -> Math.pow(u, 2))
                    .sum();
            jainsIndex = squaredSum / (utilities.size() * sumOfSquares);
        } else {
            jainsIndex = 0.0;
        }
        
        // Calculate min/max ratio
        double minMaxRatio;
        if (maxUtility > 0) {
            minMaxRatio = minUtility / maxUtility;
        } else {
            minMaxRatio = 1.0;
        }
        
        // Combine metrics (higher is better)
        return 0.4 * jainsIndex + 0.4 * minMaxRatio + 0.2 * (1.0 - Math.min(1.0, variance));
    }

    /**
     * Get the maximum quantity of a resource for a participant.
     *
     * @param participant The participant
     * @param resourceName The resource name
     * @return The maximum quantity
     */
    private double getMaxQuantity(Agent participant, String resourceName) {
        // In a real implementation, this would look up the participant's resources or constraints
        // For now, we'll use a default value
        return 100.0;
    }

    /**
     * Get a participant's preferences.
     *
     * @param participant The participant
     * @return Map of resource names to preference values
     */
    private Map<String, Double> getParticipantPreferences(Agent participant) {
        // In a real implementation, this would look up the participant's preferences
        // For now, we'll use default values
        Map<String, Double> preferences = new HashMap<>();
        preferences.put("computation", 0.7);
        preferences.put("memory", 0.5);
        preferences.put("tokens", 0.8);
        return preferences;
    }

    /**
     * Check if a negotiation session is active.
     *
     * @param negotiation The negotiation session
     * @return True if the negotiation is active
     */
    private boolean isActive(Negotiation negotiation) {
        return negotiation.getStatus() == NegotiationStatus.INITIATED || 
               negotiation.getStatus() == NegotiationStatus.IN_PROGRESS;
    }

    /**
     * Check if a negotiation session has reached completion.
     *
     * @param negotiation The negotiation session to check
     */
    private void checkNegotiationCompletion(Negotiation negotiation) {
        // Check for timeout
        if (negotiation.getDeadline() != null && LocalDateTime.now().isAfter(negotiation.getDeadline())) {
            negotiation.setStatus(NegotiationStatus.TIMEOUT);
            negotiation.setEndTime(LocalDateTime.now());
            logger.info("Negotiation {} timed out", negotiation.getId());
            return;
        }
        
        // Check for successful completion (all participants accepted a proposal)
        NegotiationMessage latestProposalMessage = null;
        Map<String, Object> latestProposal = null;
        
        // Find the latest proposal
        for (int i = negotiation.getMessages().size() - 1; i >= 0; i--) {
            NegotiationMessage message = negotiation.getMessages().get(i);
            if (message.getMessageType() == MessageType.PROPOSAL || 
                message.getMessageType() == MessageType.COUNTER_PROPOSAL) {
                latestProposalMessage = message;
                latestProposal = message.getContent();
                break;
            }
        }
        
        if (latestProposalMessage != null && latestProposal != null) {
            // Check if all other participants accepted this proposal
            boolean allAccepted = true;
            
            for (Agent participant : negotiation.getParticipants()) {
                // Skip the proposer
                if (participant.getId().equals(latestProposalMessage.getSenderId())) {
                    continue;
                }
                
                // Check if this participant accepted the proposal
                boolean accepted = false;
                
                for (int i = negotiation.getMessages().size() - 1; i >= 0; i--) {
                    NegotiationMessage message = negotiation.getMessages().get(i);
                    if (message.getMessageType() == MessageType.ACCEPT && 
                        message.getSenderId().equals(participant.getId()) && 
                        message.getInReplyTo() != null && 
                        message.getInReplyTo().equals(latestProposalMessage.getId())) {
                        accepted = true;
                        break;
                    }
                }
                
                if (!accepted) {
                    allAccepted = false;
                    break;
                }
            }
            
            if (allAccepted) {
                negotiation.setStatus(NegotiationStatus.SUCCESSFUL);
                negotiation.setEndTime(LocalDateTime.now());
                
                Map<String, Object> outcome = new HashMap<>();
                outcome.put("final_proposal", latestProposal);
                outcome.put("proposer_id", latestProposalMessage.getSenderId());
                negotiation.setOutcome(outcome);
                
                logger.info("Negotiation {} completed successfully", negotiation.getId());
            }
        }
    }

    /**
     * Inner class representing the result of evaluating a proposal.
     */
    public static class NegotiationEvaluation {
        private final boolean accept;
        private final Map<String, Object> counterProposal;
        private final double utility;

        public NegotiationEvaluation(boolean accept, Map<String, Object> counterProposal, double utility) {
            this.accept = accept;
            this.counterProposal = counterProposal;
            this.utility = utility;
        }

        public boolean isAccept() {
            return accept;
        }

        public Map<String, Object> getCounterProposal() {
            return counterProposal;
        }

        public double getUtility() {
            return utility;
        }
    }
}
