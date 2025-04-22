package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.Negotiation;
import ai.lumina.collaboration.service.AdvancedNegotiationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

/**
 * REST controller for negotiation operations.
 */
@RestController
@RequestMapping("/api/v1/collaboration/negotiations")
public class NegotiationProtocolController {

    private static final Logger logger = LoggerFactory.getLogger(NegotiationProtocolController.class);

    @Autowired
    private AdvancedNegotiationService negotiationService;

    /**
     * Initiate a new negotiation.
     *
     * @param request The negotiation request containing initiator, participants, subject, resources, and initial proposal
     * @return The created negotiation
     */
    @PostMapping
    public ResponseEntity<Negotiation> initiateNegotiation(@RequestBody Map<String, Object> request) {
        logger.info("Received request to initiate negotiation: {}", request.get("subject"));
        
        String initiatorId = (String) request.get("initiatorId");
        @SuppressWarnings("unchecked")
        List<String> participantIds = (List<String>) request.get("participantIds");
        String subject = (String) request.get("subject");
        @SuppressWarnings("unchecked")
        Map<String, Object> resources = (Map<String, Object>) request.get("resources");
        @SuppressWarnings("unchecked")
        Map<String, Object> initialProposal = (Map<String, Object>) request.get("initialProposal");
        
        Negotiation negotiation = negotiationService.initiateNegotiation(
                initiatorId, participantIds, subject, resources, initialProposal);
        
        return ResponseEntity.ok(negotiation);
    }

    /**
     * Submit a response to an ongoing negotiation.
     *
     * @param negotiationId The ID of the negotiation
     * @param request The response containing agent ID, response type, and content
     * @return The updated negotiation
     */
    @PostMapping("/{negotiationId}/responses")
    public ResponseEntity<Negotiation> submitNegotiationResponse(
            @PathVariable String negotiationId,
            @RequestBody Map<String, Object> request) {
        
        logger.info("Received response for negotiation ID: {}", negotiationId);
        
        String agentId = (String) request.get("agentId");
        String responseType = (String) request.get("responseType");
        @SuppressWarnings("unchecked")
        Map<String, Object> content = (Map<String, Object>) request.get("content");
        
        try {
            Negotiation negotiation = negotiationService.submitNegotiationResponse(
                    negotiationId, agentId, responseType, content);
            return ResponseEntity.ok(negotiation);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (IllegalArgumentException | IllegalStateException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Get a negotiation by ID.
     *
     * @param negotiationId The ID of the negotiation
     * @return The negotiation
     */
    @GetMapping("/{negotiationId}")
    public ResponseEntity<Negotiation> getNegotiation(@PathVariable String negotiationId) {
        logger.info("Received request to get negotiation ID: {}", negotiationId);
        
        try {
            Negotiation negotiation = negotiationService.getNegotiation(negotiationId);
            return ResponseEntity.ok(negotiation);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Analyze a completed negotiation.
     *
     * @param negotiationId The ID of the negotiation to analyze
     * @return Analysis results
     */
    @GetMapping("/{negotiationId}/analysis")
    public ResponseEntity<Map<String, Object>> analyzeNegotiation(@PathVariable String negotiationId) {
        logger.info("Received request to analyze negotiation ID: {}", negotiationId);
        
        try {
            Map<String, Object> analysis = negotiationService.analyzeNegotiation(negotiationId);
            return ResponseEntity.ok(analysis);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (IllegalStateException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Suggest a concession for a participant in a negotiation.
     *
     * @param negotiationId The ID of the negotiation
     * @param agentId The ID of the agent for whom to suggest a concession
     * @return A suggested concession
     */
    @GetMapping("/{negotiationId}/suggest-concession")
    public ResponseEntity<Map<String, Object>> suggestConcession(
            @PathVariable String negotiationId,
            @RequestParam String agentId) {
        
        logger.info("Received request to suggest concession for agent {} in negotiation {}", 
                   agentId, negotiationId);
        
        try {
            Map<String, Object> concession = negotiationService.suggestConcession(negotiationId, agentId);
            return ResponseEntity.ok(concession);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * Calculate the fairness of a negotiation outcome.
     *
     * @param negotiationId The ID of the negotiation
     * @return A fairness score between 0 and 1
     */
    @GetMapping("/{negotiationId}/fairness")
    public ResponseEntity<Map<String, Object>> calculateFairness(@PathVariable String negotiationId) {
        logger.info("Received request to calculate fairness for negotiation ID: {}", negotiationId);
        
        try {
            double fairness = negotiationService.calculateFairness(negotiationId);
            return ResponseEntity.ok(Map.of("fairness", fairness));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Predict the likelihood of a negotiation succeeding.
     *
     * @param negotiationId The ID of the negotiation
     * @return A probability between 0 and 1
     */
    @GetMapping("/{negotiationId}/predict-success")
    public ResponseEntity<Map<String, Object>> predictNegotiationSuccess(@PathVariable String negotiationId) {
        logger.info("Received request to predict success for negotiation ID: {}", negotiationId);
        
        try {
            double probability = negotiationService.predictNegotiationSuccess(negotiationId);
            return ResponseEntity.ok(Map.of("successProbability", probability));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Resolve a negotiation using a specific conflict resolution strategy.
     *
     * @param negotiationId The ID of the negotiation
     * @param strategy The conflict resolution strategy to use
     * @return The resolved negotiation
     */
    @PostMapping("/{negotiationId}/resolve")
    public ResponseEntity<Negotiation> resolveNegotiation(
            @PathVariable String negotiationId,
            @RequestParam(required = false) String strategy) {
        
        logger.info("Received request to resolve negotiation ID: {} using strategy: {}", 
                   negotiationId, strategy);
        
        try {
            Negotiation negotiation = negotiationService.resolveNegotiation(negotiationId, strategy);
            return ResponseEntity.ok(negotiation);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (IllegalArgumentException | IllegalStateException e) {
            return ResponseEntity.badRequest().build();
        }
    }
}
