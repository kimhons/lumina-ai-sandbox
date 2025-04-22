package ai.lumina.learning.controller;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import ai.lumina.learning.integration.CollaborativeLearningService;
import ai.lumina.learning.model.CollaborativeLearningSession;
import ai.lumina.learning.repository.CollaborativeLearningSessionRepository;
import lombok.extern.slf4j.Slf4j;

/**
 * Controller for collaborative learning operations.
 * Provides endpoints for team formation, context creation, and task distribution.
 */
@RestController
@RequestMapping("/api/v1/learning/collaborative")
@Slf4j
public class CollaborativeLearningController {

    @Autowired
    private CollaborativeLearningService collaborativeLearningService;
    
    @Autowired
    private CollaborativeLearningSessionRepository sessionRepository;
    
    /**
     * Form a learning team for collaborative learning.
     * 
     * @param request Team formation request containing learning task and available agents
     * @return Result of the team formation operation
     */
    @PostMapping("/teams/form")
    public ResponseEntity<Map<String, Object>> formLearningTeam(@RequestBody Map<String, Object> request) {
        log.info("Received learning team formation request: {}", request);
        
        @SuppressWarnings("unchecked")
        Map<String, Object> learningTask = (Map<String, Object>) request.get("learning_task");
        
        @SuppressWarnings("unchecked")
        List<String> availableAgents = (List<String>) request.get("available_agents");
        
        Map<String, Object> result = collaborativeLearningService.formLearningTeam(
                learningTask, availableAgents);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Create a learning context for collaborative learning.
     * 
     * @param request Context creation request containing team ID and learning task
     * @return Result of the context creation operation
     */
    @PostMapping("/contexts")
    public ResponseEntity<Map<String, Object>> createLearningContext(@RequestBody Map<String, Object> request) {
        log.info("Received learning context creation request: {}", request);
        
        String teamId = (String) request.get("team_id");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> learningTask = (Map<String, Object>) request.get("learning_task");
        
        Map<String, Object> result = collaborativeLearningService.createLearningContext(
                teamId, learningTask);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Distribute a learning task to team members.
     * 
     * @param request Task distribution request containing team ID, context ID, and learning task
     * @return Result of the task distribution operation
     */
    @PostMapping("/tasks/distribute")
    public ResponseEntity<Map<String, Object>> distributeLearningTask(@RequestBody Map<String, Object> request) {
        log.info("Received learning task distribution request: {}", request);
        
        String teamId = (String) request.get("team_id");
        String contextId = (String) request.get("context_id");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> learningTask = (Map<String, Object>) request.get("learning_task");
        
        Map<String, Object> result = collaborativeLearningService.distributeLearningTask(
                teamId, contextId, learningTask);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Coordinate federated learning across agents.
     * 
     * @param request Federated learning request containing team ID, context ID, learning task, and federation config
     * @return Result of the federated learning operation
     */
    @PostMapping("/federated")
    public ResponseEntity<Map<String, Object>> coordinateFederatedLearning(@RequestBody Map<String, Object> request) {
        log.info("Received federated learning coordination request: {}", request);
        
        String teamId = (String) request.get("team_id");
        String contextId = (String) request.get("context_id");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> learningTask = (Map<String, Object>) request.get("learning_task");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> federationConfig = (Map<String, Object>) request.get("federation_config");
        
        Map<String, Object> result = collaborativeLearningService.coordinateFederatedLearning(
                teamId, contextId, learningTask, federationConfig);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Complete a collaborative learning session.
     * 
     * @param contextId ID of the context
     * @param request Completion request containing learning results
     * @return Result of the completion operation
     */
    @PostMapping("/complete/{contextId}")
    public ResponseEntity<Map<String, Object>> completeCollaborativeLearning(
            @PathVariable String contextId,
            @RequestBody Map<String, Object> request) {
        
        log.info("Received collaborative learning completion request for context {}: {}", contextId, request);
        
        @SuppressWarnings("unchecked")
        Map<String, Object> results = (Map<String, Object>) request.get("results");
        
        Map<String, Object> result = collaborativeLearningService.completeCollaborativeLearning(
                contextId, results);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Get a collaborative learning session by ID.
     * 
     * @param sessionId ID of the session
     * @return The collaborative learning session
     */
    @GetMapping("/sessions/{sessionId}")
    public ResponseEntity<CollaborativeLearningSession> getSession(@PathVariable String sessionId) {
        log.info("Received request for collaborative learning session: {}", sessionId);
        
        CollaborativeLearningSession session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("Session not found: " + sessionId));
        
        return ResponseEntity.ok(session);
    }
    
    /**
     * Get all collaborative learning sessions.
     * 
     * @return List of all collaborative learning sessions
     */
    @GetMapping("/sessions")
    public ResponseEntity<Iterable<CollaborativeLearningSession>> getAllSessions() {
        log.info("Received request for all collaborative learning sessions");
        
        Iterable<CollaborativeLearningSession> sessions = sessionRepository.findAll();
        
        return ResponseEntity.ok(sessions);
    }
    
    /**
     * Get collaborative learning sessions by team ID.
     * 
     * @param teamId ID of the team
     * @return List of collaborative learning sessions for the specified team
     */
    @GetMapping("/sessions/team/{teamId}")
    public ResponseEntity<Iterable<CollaborativeLearningSession>> getSessionsByTeam(@PathVariable String teamId) {
        log.info("Received request for collaborative learning sessions for team: {}", teamId);
        
        Iterable<CollaborativeLearningSession> sessions = sessionRepository.findByTeamId(teamId);
        
        return ResponseEntity.ok(sessions);
    }
}
