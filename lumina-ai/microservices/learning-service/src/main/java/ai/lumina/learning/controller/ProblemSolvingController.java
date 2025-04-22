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

import ai.lumina.learning.integration.ProblemSolvingService;
import ai.lumina.learning.model.ProblemSolvingSession;
import ai.lumina.learning.repository.ProblemSolvingSessionRepository;
import lombok.extern.slf4j.Slf4j;

/**
 * Controller for problem solving operations.
 * Provides endpoints for analyzing problems, decomposing them, forming teams, and solving them.
 */
@RestController
@RequestMapping("/api/v1/problem-solving")
@Slf4j
public class ProblemSolvingController {

    @Autowired
    private ProblemSolvingService problemSolvingService;
    
    @Autowired
    private ProblemSolvingSessionRepository sessionRepository;
    
    /**
     * Analyze a problem to determine if it's suitable for collaborative solving.
     * 
     * @param request Problem specification
     * @return Analysis result
     */
    @PostMapping("/analyze")
    public ResponseEntity<Map<String, Object>> analyzeProblem(@RequestBody Map<String, Object> request) {
        log.info("Received problem analysis request: {}", request);
        
        Map<String, Object> result = problemSolvingService.analyzeProblem(request);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Decompose a problem into subtasks.
     * 
     * @param request Request containing problem specification and analysis result
     * @return Decomposition result
     */
    @PostMapping("/decompose")
    public ResponseEntity<Map<String, Object>> decomposeProblem(@RequestBody Map<String, Object> request) {
        log.info("Received problem decomposition request: {}", request);
        
        @SuppressWarnings("unchecked")
        Map<String, Object> problemSpec = (Map<String, Object>) request.get("problem_spec");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> analysisResult = (Map<String, Object>) request.get("analysis_result");
        
        Map<String, Object> result = problemSolvingService.decomposeProblem(
                problemSpec, analysisResult);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Form a team for collaborative problem solving.
     * 
     * @param request Request containing problem specification, decomposition result, and available agents
     * @return Team formation result
     */
    @PostMapping("/teams/form")
    public ResponseEntity<Map<String, Object>> formProblemSolvingTeam(@RequestBody Map<String, Object> request) {
        log.info("Received problem solving team formation request: {}", request);
        
        @SuppressWarnings("unchecked")
        Map<String, Object> problemSpec = (Map<String, Object>) request.get("problem_spec");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> decompositionResult = (Map<String, Object>) request.get("decomposition_result");
        
        @SuppressWarnings("unchecked")
        List<String> availableAgents = (List<String>) request.get("available_agents");
        
        Map<String, Object> result = problemSolvingService.formProblemSolvingTeam(
                problemSpec, decompositionResult, availableAgents);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Create a shared context for collaborative problem solving.
     * 
     * @param request Request containing problem specification, team result, and decomposition result
     * @return Context creation result
     */
    @PostMapping("/contexts")
    public ResponseEntity<Map<String, Object>> createProblemSolvingContext(@RequestBody Map<String, Object> request) {
        log.info("Received problem solving context creation request: {}", request);
        
        @SuppressWarnings("unchecked")
        Map<String, Object> problemSpec = (Map<String, Object>) request.get("problem_spec");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> teamResult = (Map<String, Object>) request.get("team_result");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> decompositionResult = (Map<String, Object>) request.get("decomposition_result");
        
        Map<String, Object> result = problemSolvingService.createProblemSolvingContext(
                problemSpec, teamResult, decompositionResult);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Coordinate the collaborative problem solving process.
     * 
     * @param request Request containing problem specification, team result, context result, and decomposition result
     * @return Problem solving result
     */
    @PostMapping("/coordinate")
    public ResponseEntity<Map<String, Object>> coordinateProblemSolving(@RequestBody Map<String, Object> request) {
        log.info("Received problem solving coordination request: {}", request);
        
        @SuppressWarnings("unchecked")
        Map<String, Object> problemSpec = (Map<String, Object>) request.get("problem_spec");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> teamResult = (Map<String, Object>) request.get("team_result");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> contextResult = (Map<String, Object>) request.get("context_result");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> decompositionResult = (Map<String, Object>) request.get("decomposition_result");
        
        Map<String, Object> result = problemSolvingService.coordinateProblemSolving(
                problemSpec, teamResult, contextResult, decompositionResult);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Solve a problem using collaborative problem solving.
     * 
     * @param request Request containing problem specification and available agents
     * @return Problem solving result
     */
    @PostMapping("/solve")
    public ResponseEntity<Map<String, Object>> solveProblem(@RequestBody Map<String, Object> request) {
        log.info("Received problem solving request: {}", request);
        
        @SuppressWarnings("unchecked")
        Map<String, Object> problemSpec = (Map<String, Object>) request.get("problem_spec");
        
        @SuppressWarnings("unchecked")
        List<String> availableAgents = (List<String>) request.get("available_agents");
        
        Map<String, Object> result = problemSolvingService.solveProblem(
                problemSpec, availableAgents);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Get a problem solving session by ID.
     * 
     * @param sessionId ID of the session
     * @return The problem solving session
     */
    @GetMapping("/sessions/{sessionId}")
    public ResponseEntity<ProblemSolvingSession> getSession(@PathVariable String sessionId) {
        log.info("Received request for problem solving session: {}", sessionId);
        
        ProblemSolvingSession session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("Session not found: " + sessionId));
        
        return ResponseEntity.ok(session);
    }
    
    /**
     * Get all problem solving sessions.
     * 
     * @return List of all problem solving sessions
     */
    @GetMapping("/sessions")
    public ResponseEntity<Iterable<ProblemSolvingSession>> getAllSessions() {
        log.info("Received request for all problem solving sessions");
        
        Iterable<ProblemSolvingSession> sessions = sessionRepository.findAll();
        
        return ResponseEntity.ok(sessions);
    }
    
    /**
     * Get problem solving sessions by team ID.
     * 
     * @param teamId ID of the team
     * @return List of problem solving sessions for the specified team
     */
    @GetMapping("/sessions/team/{teamId}")
    public ResponseEntity<Iterable<ProblemSolvingSession>> getSessionsByTeam(@PathVariable String teamId) {
        log.info("Received request for problem solving sessions for team: {}", teamId);
        
        Iterable<ProblemSolvingSession> sessions = sessionRepository.findByTeamId(teamId);
        
        return ResponseEntity.ok(sessions);
    }
    
    /**
     * Get problem solving sessions by problem type.
     * 
     * @param problemType The problem type
     * @return List of problem solving sessions for the specified problem type
     */
    @GetMapping("/sessions/type/{problemType}")
    public ResponseEntity<Iterable<ProblemSolvingSession>> getSessionsByProblemType(
            @PathVariable ProblemSolvingSession.ProblemType problemType) {
        
        log.info("Received request for problem solving sessions of type: {}", problemType);
        
        Iterable<ProblemSolvingSession> sessions = sessionRepository.findByProblemType(problemType);
        
        return ResponseEntity.ok(sessions);
    }
}
