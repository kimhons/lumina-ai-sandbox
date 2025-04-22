package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.*;
import ai.lumina.collaboration.service.NegotiationService;
import ai.lumina.collaboration.service.NegotiationService.NegotiationEvaluation;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * REST controller for negotiation protocol operations.
 */
@RestController
@RequestMapping("/api/v1/negotiation")
public class NegotiationController {

    private static final Logger logger = LoggerFactory.getLogger(NegotiationController.class);

    private final NegotiationService negotiationService;

    @Autowired
    public NegotiationController(NegotiationService negotiationService) {
        this.negotiationService = negotiationService;
    }

    /**
     * Create a new negotiation session.
     *
     * @param request Request containing negotiation parameters
     * @return The created negotiation session
     */
    @PostMapping
    public ResponseEntity<Negotiation> createSession(@RequestBody NegotiationRequest request) {
        logger.info("Received request to create negotiation session: {}", request);
        
        try {
            Negotiation negotiation = negotiationService.createSession(
                    request.getTopic(),
                    request.getInitiatorId(),
                    request.getParticipants(),
                    request.getResources(),
                    request.getConstraints(),
                    request.getPreferences(),
                    request.getDeadline()
            );
            
            return ResponseEntity.ok(negotiation);
        } catch (Exception e) {
            logger.error("Error creating negotiation session: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get a negotiation session by ID.
     *
     * @param id ID of the negotiation session
     * @return The negotiation session
     */
    @GetMapping("/{id}")
    public ResponseEntity<Negotiation> getSession(@PathVariable String id) {
        logger.info("Received request to get negotiation session: {}", id);
        
        Optional<Negotiation> negotiation = negotiationService.getSession(id);
        
        return negotiation
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all active negotiation sessions.
     *
     * @return List of active negotiation sessions
     */
    @GetMapping("/active")
    public ResponseEntity<List<Negotiation>> getActiveSessions() {
        logger.info("Received request to get active negotiation sessions");
        
        List<Negotiation> activeSessions = negotiationService.getActiveSessions();
        
        return ResponseEntity.ok(activeSessions);
    }

    /**
     * Send a message in a negotiation session.
     *
     * @param id ID of the negotiation session
     * @param message The message to send
     * @return Success status
     */
    @PostMapping("/{id}/message")
    public ResponseEntity<Boolean> sendMessage(@PathVariable String id, @RequestBody NegotiationMessage message) {
        logger.info("Received request to send message in negotiation {}: {}", id, message);
        
        boolean success = negotiationService.sendMessage(id, message);
        
        if (success) {
            return ResponseEntity.ok(true);
        } else {
            return ResponseEntity.badRequest().body(false);
        }
    }

    /**
     * End a negotiation session.
     *
     * @param id ID of the negotiation session
     * @param request Request containing end parameters
     * @return Success status
     */
    @PostMapping("/{id}/end")
    public ResponseEntity<Boolean> endSession(@PathVariable String id, @RequestBody NegotiationEndRequest request) {
        logger.info("Received request to end negotiation {}: {}", id, request);
        
        boolean success = negotiationService.endSession(id, request.getStatus(), request.getOutcome());
        
        if (success) {
            return ResponseEntity.ok(true);
        } else {
            return ResponseEntity.badRequest().body(false);
        }
    }

    /**
     * Generate a proposal.
     *
     * @param id ID of the negotiation session
     * @param request Request containing proposal parameters
     * @return Generated proposal
     */
    @PostMapping("/{id}/generate-proposal")
    public ResponseEntity<Map<String, Object>> generateProposal(
            @PathVariable String id,
            @RequestBody ProposalGenerationRequest request) {
        logger.info("Received request to generate proposal in negotiation {}: {}", id, request);
        
        Optional<Map<String, Object>> proposal = negotiationService.generateProposal(
                id,
                request.getParticipantId(),
                request.getStrategyName()
        );
        
        return proposal
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.badRequest().build());
    }

    /**
     * Evaluate a proposal.
     *
     * @param id ID of the negotiation session
     * @param request Request containing evaluation parameters
     * @return Evaluation result
     */
    @PostMapping("/{id}/evaluate-proposal")
    public ResponseEntity<EvaluationResponse> evaluateProposal(
            @PathVariable String id,
            @RequestBody ProposalEvaluationRequest request) {
        logger.info("Received request to evaluate proposal in negotiation {}: {}", id, request);
        
        Optional<NegotiationEvaluation> evaluation = negotiationService.evaluateProposal(
                id,
                request.getProposal(),
                request.getParticipantId(),
                request.getStrategyName()
        );
        
        if (evaluation.isPresent()) {
            NegotiationEvaluation result = evaluation.get();
            EvaluationResponse response = new EvaluationResponse(
                    result.isAccept(),
                    result.getCounterProposal(),
                    result.getUtility()
            );
            return ResponseEntity.ok(response);
        } else {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Request class for creating a negotiation session.
     */
    public static class NegotiationRequest {
        private String topic;
        private String initiatorId;
        private List<Agent> participants;
        private List<Resource> resources;
        private Map<String, Object> constraints;
        private Map<String, Double> preferences;
        private LocalDateTime deadline;

        public String getTopic() {
            return topic;
        }

        public void setTopic(String topic) {
            this.topic = topic;
        }

        public String getInitiatorId() {
            return initiatorId;
        }

        public void setInitiatorId(String initiatorId) {
            this.initiatorId = initiatorId;
        }

        public List<Agent> getParticipants() {
            return participants;
        }

        public void setParticipants(List<Agent> participants) {
            this.participants = participants;
        }

        public List<Resource> getResources() {
            return resources;
        }

        public void setResources(List<Resource> resources) {
            this.resources = resources;
        }

        public Map<String, Object> getConstraints() {
            return constraints;
        }

        public void setConstraints(Map<String, Object> constraints) {
            this.constraints = constraints;
        }

        public Map<String, Double> getPreferences() {
            return preferences;
        }

        public void setPreferences(Map<String, Double> preferences) {
            this.preferences = preferences;
        }

        public LocalDateTime getDeadline() {
            return deadline;
        }

        public void setDeadline(LocalDateTime deadline) {
            this.deadline = deadline;
        }
    }

    /**
     * Request class for ending a negotiation session.
     */
    public static class NegotiationEndRequest {
        private NegotiationStatus status;
        private Map<String, Object> outcome;

        public NegotiationStatus getStatus() {
            return status;
        }

        public void setStatus(NegotiationStatus status) {
            this.status = status;
        }

        public Map<String, Object> getOutcome() {
            return outcome;
        }

        public void setOutcome(Map<String, Object> outcome) {
            this.outcome = outcome;
        }
    }

    /**
     * Request class for generating a proposal.
     */
    public static class ProposalGenerationRequest {
        private String participantId;
        private String strategyName;

        public String getParticipantId() {
            return participantId;
        }

        public void setParticipantId(String participantId) {
            this.participantId = participantId;
        }

        public String getStrategyName() {
            return strategyName;
        }

        public void setStrategyName(String strategyName) {
            this.strategyName = strategyName;
        }
    }

    /**
     * Request class for evaluating a proposal.
     */
    public static class ProposalEvaluationRequest {
        private Map<String, Object> proposal;
        private String participantId;
        private String strategyName;

        public Map<String, Object> getProposal() {
            return proposal;
        }

        public void setProposal(Map<String, Object> proposal) {
            this.proposal = proposal;
        }

        public String getParticipantId() {
            return participantId;
        }

        public void setParticipantId(String participantId) {
            this.participantId = participantId;
        }

        public String getStrategyName() {
            return strategyName;
        }

        public void setStrategyName(String strategyName) {
            this.strategyName = strategyName;
        }
    }

    /**
     * Response class for proposal evaluation.
     */
    public static class EvaluationResponse {
        private final boolean accept;
        private final Map<String, Object> counterProposal;
        private final double utility;

        public EvaluationResponse(boolean accept, Map<String, Object> counterProposal, double utility) {
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
