package ai.lumina.learning.integration;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import ai.lumina.learning.model.ProblemSolvingSession;
import ai.lumina.learning.repository.ProblemSolvingSessionRepository;
import lombok.extern.slf4j.Slf4j;

/**
 * Service for integrating problem solving capabilities with the collaboration system.
 * This service enables collaborative problem solving between agents.
 */
@Service
@Slf4j
public class ProblemSolvingService {

    @Autowired
    private RestTemplate restTemplate;
    
    @Autowired
    private ProblemSolvingSessionRepository sessionRepository;
    
    @Value("${lumina.collaboration.api.url}")
    private String collaborationApiUrl;
    
    /**
     * Analyze a problem to determine if it's suitable for collaborative solving.
     * 
     * @param problemSpec The problem specification
     * @return Analysis result
     */
    public Map<String, Object> analyzeProblem(Map<String, Object> problemSpec) {
        try {
            log.info("Analyzing problem: {}", problemSpec.get("problem_id"));
            
            // Extract problem details
            String problemId = (String) problemSpec.get("problem_id");
            String problemType = (String) problemSpec.get("problem_type");
            String domain = (String) problemSpec.get("domain");
            String description = (String) problemSpec.get("description");
            String complexity = (String) problemSpec.get("complexity");
            
            // Determine if problem is suitable for collaborative solving
            boolean isCollaborative = determineIfCollaborative(problemSpec);
            
            // Create analysis result
            Map<String, Object> analysisResult = new HashMap<>();
            analysisResult.put("problem_id", problemId);
            analysisResult.put("problem_type", problemType);
            analysisResult.put("domain", domain);
            analysisResult.put("is_collaborative", isCollaborative);
            
            if (isCollaborative) {
                // Identify required capabilities
                List<Map<String, Object>> requiredCapabilities = identifyRequiredCapabilities(problemSpec);
                analysisResult.put("required_capabilities", requiredCapabilities);
                
                // Determine decomposition approach
                Map<String, Object> decompositionApproach = determineDecompositionApproach(problemSpec);
                analysisResult.put("decomposition_approach", decompositionApproach);
                
                // Estimate resource requirements
                Map<String, Object> resourceRequirements = estimateResourceRequirements(problemSpec);
                analysisResult.put("resource_requirements", resourceRequirements);
                
                // Identify relevant knowledge
                List<Map<String, Object>> relevantKnowledge = identifyRelevantKnowledge(problemSpec);
                analysisResult.put("relevant_knowledge", relevantKnowledge);
                
                // Determine verification approach
                Map<String, Object> verificationApproach = determineVerificationApproach(problemSpec);
                analysisResult.put("verification_approach", verificationApproach);
                
                // Provide overall recommendation
                analysisResult.put("recommendation", "collaborative_solving");
                analysisResult.put("approach", determineSolvingApproach(problemSpec, requiredCapabilities));
            } else {
                analysisResult.put("recommendation", "single_agent_solving");
                analysisResult.put("reason", "Problem is not complex enough to warrant collaborative solving");
            }
            
            log.info("Problem analysis completed: {}", analysisResult);
            
            return analysisResult;
            
        } catch (Exception e) {
            log.error("Error analyzing problem", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("problem_id", problemSpec.get("problem_id"));
            errorResult.put("message", e.getMessage());
            errorResult.put("timestamp", LocalDateTime.now().toString());
            
            return errorResult;
        }
    }
    
    /**
     * Decompose a problem into subtasks.
     * 
     * @param problemSpec The problem specification
     * @param analysisResult Result of problem analysis
     * @return Decomposition result
     */
    public Map<String, Object> decomposeProblem(
            Map<String, Object> problemSpec,
            Map<String, Object> analysisResult) {
        
        try {
            log.info("Decomposing problem: {}", problemSpec.get("problem_id"));
            
            // Extract problem details
            String problemId = (String) problemSpec.get("problem_id");
            
            // Check if problem is suitable for decomposition
            Boolean isCollaborative = (Boolean) analysisResult.get("is_collaborative");
            
            if (isCollaborative == null || !isCollaborative) {
                Map<String, Object> result = new HashMap<>();
                result.put("status", "warning");
                result.put("problem_id", problemId);
                result.put("message", "Problem is not suitable for decomposition");
                result.put("subtasks", List.of());
                result.put("timestamp", LocalDateTime.now().toString());
                return result;
            }
            
            // Get decomposition approach
            @SuppressWarnings("unchecked")
            Map<String, Object> decompositionApproach = (Map<String, Object>) analysisResult.get("decomposition_approach");
            
            // Create subtasks based on approach
            List<Map<String, Object>> subtasks = createSubtasks(problemSpec, decompositionApproach);
            
            // Create dependency graph
            Map<String, List<String>> dependencyGraph = createDependencyGraph(subtasks);
            
            // Create decomposition result
            Map<String, Object> result = new HashMap<>();
            result.put("status", "success");
            result.put("problem_id", problemId);
            result.put("subtasks", subtasks);
            result.put("dependency_graph", dependencyGraph);
            result.put("timestamp", LocalDateTime.now().toString());
            
            log.info("Problem decomposition completed: {} subtasks", subtasks.size());
            
            return result;
            
        } catch (Exception e) {
            log.error("Error decomposing problem", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("problem_id", problemSpec.get("problem_id"));
            errorResult.put("message", e.getMessage());
            errorResult.put("timestamp", LocalDateTime.now().toString());
            
            return errorResult;
        }
    }
    
    /**
     * Form a team for collaborative problem solving.
     * 
     * @param problemSpec The problem specification
     * @param decompositionResult Result of problem decomposition
     * @param availableAgents List of available agent IDs
     * @return Team formation result
     */
    public Map<String, Object> formProblemSolvingTeam(
            Map<String, Object> problemSpec,
            Map<String, Object> decompositionResult,
            List<String> availableAgents) {
        
        try {
            log.info("Forming problem solving team for problem: {}", problemSpec.get("problem_id"));
            
            // Extract problem details
            String problemId = (String) problemSpec.get("problem_id");
            
            // Extract subtasks
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> subtasks = (List<Map<String, Object>>) decompositionResult.get("subtasks");
            
            if (subtasks == null || subtasks.isEmpty()) {
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("status", "error");
                errorResult.put("problem_id", problemId);
                errorResult.put("message", "No subtasks found in decomposition result");
                errorResult.put("timestamp", LocalDateTime.now().toString());
                return errorResult;
            }
            
            // Collect all required capabilities
            List<String> allCapabilities = collectRequiredCapabilities(subtasks);
            
            // Create team formation request
            Map<String, Object> formationRequest = new HashMap<>();
            formationRequest.put("task_type", "problem_solving");
            formationRequest.put("required_capabilities", allCapabilities);
            formationRequest.put("available_agents", availableAgents);
            
            Map<String, Object> taskMetadata = new HashMap<>();
            taskMetadata.put("problem_id", problemId);
            taskMetadata.put("problem_type", problemSpec.get("problem_type"));
            taskMetadata.put("domain", problemSpec.get("domain"));
            taskMetadata.put("priority", problemSpec.get("priority", "medium"));
            
            formationRequest.put("task_metadata", taskMetadata);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create HTTP entity
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(formationRequest, headers);
            
            // Call collaboration API
            ResponseEntity<Map> response = restTemplate.exchange(
                    collaborationApiUrl + "/teams/form",
                    HttpMethod.POST,
                    entity,
                    Map.class);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> teamResult = response.getBody();
            
            // Create agent-subtask assignments
            @SuppressWarnings("unchecked")
            List<String> members = (List<String>) teamResult.get("members");
            
            @SuppressWarnings("unchecked")
            Map<String, List<String>> capabilitiesCoverage = (Map<String, List<String>>) teamResult.get("capabilities_coverage");
            
            Map<String, List<String>> assignments = assignSubtasksToAgents(subtasks, members, capabilitiesCoverage);
            
            // Create team formation result
            Map<String, Object> result = new HashMap<>();
            result.put("status", "success");
            result.put("problem_id", problemId);
            result.put("team_id", teamResult.get("team_id"));
            result.put("members", members);
            result.put("capabilities_coverage", capabilitiesCoverage);
            result.put("assignments", assignments);
            result.put("timestamp", LocalDateTime.now().toString());
            
            log.info("Problem solving team formation completed: {}", teamResult.get("team_id"));
            
            return result;
            
        } catch (Exception e) {
            log.error("Error forming problem solving team", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("problem_id", problemSpec.get("problem_id"));
            errorResult.put("message", e.getMessage());
            errorResult.put("timestamp", LocalDateTime.now().toString());
            
            return errorResult;
        }
    }
    
    /**
     * Create a shared context for collaborative problem solving.
     * 
     * @param problemSpec The problem specification
     * @param teamResult Result of team formation
     * @param decompositionResult Result of problem decomposition
     * @return Context creation result
     */
    public Map<String, Object> createProblemSolvingContext(
            Map<String, Object> problemSpec,
            Map<String, Object> teamResult,
            Map<String, Object> decompositionResult) {
        
        try {
            log.info("Creating problem solving context for problem: {}", problemSpec.get("problem_id"));
            
            // Extract details
            String problemId = (String) problemSpec.get("problem_id");
            String teamId = (String) teamResult.get("team_id");
            
            if (teamId == null) {
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("status", "error");
                errorResult.put("problem_id", problemId);
                errorResult.put("message", "No team ID found in team formation result");
                errorResult.put("timestamp", LocalDateTime.now().toString());
                return errorResult;
            }
            
            // Create initial context data
            Map<String, Object> initialData = new HashMap<>();
            initialData.put("problem", problemSpec);
            initialData.put("decomposition", decompositionResult);
            initialData.put("team", teamResult);
            initialData.put("status", "initialized");
            
            Map<String, Object> progress = new HashMap<>();
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> subtasks = (List<Map<String, Object>>) decompositionResult.get("subtasks");
            
            progress.put("completed_subtasks", 0);
            progress.put("total_subtasks", subtasks.size());
            progress.put("status_by_subtask", new HashMap<>());
            
            initialData.put("progress", progress);
            initialData.put("solutions", new HashMap<>());
            initialData.put("created_at", LocalDateTime.now().toString());
            
            // Create context request
            Map<String, Object> contextRequest = new HashMap<>();
            contextRequest.put("team_id", teamId);
            contextRequest.put("context_type", "problem_solving");
            contextRequest.put("task_id", problemId);
            
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("problem_id", problemId);
            metadata.put("problem_type", problemSpec.get("problem_type"));
            metadata.put("domain", problemSpec.get("domain"));
            metadata.put("created_at", LocalDateTime.now().toString());
            
            contextRequest.put("metadata", metadata);
            contextRequest.put("initial_data", initialData);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create HTTP entity
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(contextRequest, headers);
            
            // Call collaboration API
            ResponseEntity<Map> response = restTemplate.exchange(
                    collaborationApiUrl + "/contexts",
                    HttpMethod.POST,
                    entity,
                    Map.class);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> contextResult = response.getBody();
            
            // Create and save session
            ProblemSolvingSession session = ProblemSolvingSession.createNew();
            session.setProblemId(problemId);
            session.setTeamId(teamId);
            session.setContextId((String) contextResult.get("context_id"));
            session.setProblemType(determineProblemType(problemSpec));
            session.setDomain((String) problemSpec.get("domain"));
            session.setProblemSpec(problemSpec);
            session.setStatus(ProblemSolvingSession.SessionStatus.INITIALIZED);
            
            sessionRepository.save(session);
            
            // Create context creation result
            Map<String, Object> result = new HashMap<>();
            result.put("status", "success");
            result.put("problem_id", problemId);
            result.put("team_id", teamId);
            result.put("context_id", contextResult.get("context_id"));
            result.put("session_id", session.getId());
            result.put("timestamp", LocalDateTime.now().toString());
            
            log.info("Problem solving context creation completed: {}", contextResult.get("context_id"));
            
            return result;
            
        } catch (Exception e) {
            log.error("Error creating problem solving context", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("problem_id", problemSpec.get("problem_id"));
            errorResult.put("message", e.getMessage());
            errorResult.put("timestamp", LocalDateTime.now().toString());
            
            return errorResult;
        }
    }
    
    /**
     * Coordinate the collaborative problem solving process.
     * 
     * @param problemSpec The problem specification
     * @param teamResult Result of team formation
     * @param contextResult Result of context creation
     * @param decompositionResult Result of problem decomposition
     * @return Problem solving result
     */
    public Map<String, Object> coordinateProblemSolving(
            Map<String, Object> problemSpec,
            Map<String, Object> teamResult,
            Map<String, Object> contextResult,
            Map<String, Object> decompositionResult) {
        
        try {
            log.info("Coordinating problem solving for problem: {}", problemSpec.get("problem_id"));
            
            // Extract details
            String problemId = (String) problemSpec.get("problem_id");
            String teamId = (String) teamResult.get("team_id");
            String contextId = (String) contextResult.get("context_id");
            String sessionId = (String) contextResult.get("session_id");
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> subtasks = (List<Map<String, Object>>) decompositionResult.get("subtasks");
            
            @SuppressWarnings("unchecked")
            Map<String, List<String>> assignments = (Map<String, List<String>>) teamResult.get("assignments");
            
            if (teamId == null || contextId == null) {
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("status", "error");
                errorResult.put("problem_id", problemId);
                errorResult.put("message", "Missing team ID or context ID");
                errorResult.put("timestamp", LocalDateTime.now().toString());
                return errorResult;
            }
            
            // Update session status
            ProblemSolvingSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Session not found: " + sessionId));
            
            session.setStatus(ProblemSolvingSession.SessionStatus.SOLVING);
            sessionRepository.save(session);
            
            // Update context with session start
            updateProblemContext(contextId, Map.of(
                    "solving_session", Map.of(
                            "session_id", sessionId,
                            "status", "started",
                            "start_time", LocalDateTime.now().toString()
                    )
            ));
            
            // Create execution plan based on dependency graph
            @SuppressWarnings("unchecked")
            Map<String, List<String>> dependencyGraph = (Map<String, List<String>>) decompositionResult.get("dependency_graph");
            
            List<List<String>> executionPlan = createExecutionPlan(subtasks, dependencyGraph);
            
            // Update context with execution plan
            updateProblemContext(contextId, Map.of(
                    "solving_session", Map.of(
                            "session_id", sessionId,
                            "execution_plan", executionPlan,
                            "timestamp", LocalDateTime.now().toString()
                    )
            ));
            
            // Execute subtasks according to plan
            Map<String, Map<String, Object>> subtaskResults = new HashMap<>();
            
            for (int phaseIdx = 0; phaseIdx < executionPlan.size(); phaseIdx++) {
                List<String> phase = executionPlan.get(phaseIdx);
                
                // Update context with phase start
                updateProblemContext(contextId, Map.of(
                        "solving_session", Map.of(
                                "session_id", sessionId,
                                "status", "executing_phase_" + phaseIdx,
                                "current_phase", phaseIdx,
                                "timestamp", LocalDateTime.now().toString()
                        )
                ));
                
                // Execute all subtasks in this phase
                Map<String, Map<String, Object>> phaseResults = new HashMap<>();
                
                for (String subtaskId : phase) {
                    // Find subtask details
                    Map<String, Object> subtask = findSubtaskById(subtasks, subtaskId);
                    
                    if (subtask == null) {
                        log.warning("Subtask {} not found in decomposition result", subtaskId);
                        continue;
                    }
                    
                    // Find assigned agent
                    String agentId = findAgentForSubtask(assignments, subtaskId);
                    
                    if (agentId == null) {
                        log.warning("No agent assigned to subtask {}", subtaskId);
                        continue;
                    }
                    
                    // Prepare subtask inputs
                    Map<String, Object> subtaskInputs = new HashMap<>();
                    
                    @SuppressWarnings("unchecked")
                    List<String> dependencies = (List<String>) subtask.get("dependencies");
                    
                    if (dependencies != null) {
                        for (String dependency : dependencies) {
                            if (subtaskResults.containsKey(dependency)) {
                                @SuppressWarnings("unchecked")
                                Map<String, Object> outputs = (Map<String, Object>) subtaskResults.get(dependency).get("outputs");
                                subtaskInputs.put(dependency, outputs);
                            }
                        }
                    }
                    
                    // Execute subtask
                    Map<String, Object> subtaskResult = executeSubtask(
                            agentId,
                            teamId,
                            contextId,
                            subtask,
                            subtaskInputs,
                            problemSpec
                    );
                    
                    // Store result
                    phaseResults.put(subtaskId, subtaskResult);
                    subtaskResults.put(subtaskId, subtaskResult);
                    
                    // Update context with subtask completion
                    updateProblemContext(contextId, Map.of(
                            "progress", Map.of(
                                    "status_by_subtask", Map.of(
                                            subtaskId, Map.of(
                                                    "status", "completed",
                                                    "agent_id", agentId,
                                                    "timestamp", LocalDateTime.now().toString()
                                            )
                                    )
                            )
                    ));
                }
                
                // Update context with phase completion
                updateProblemContext(contextId, Map.of(
                        "solving_session", Map.of(
                                "session_id", sessionId,
                                "status", "completed_phase_" + phaseIdx,
                                "phase_results", phaseResults,
                                "timestamp", LocalDateTime.now().toString()
                        )
                ));
            }
            
            // Check if we have an integration subtask
            Map<String, Object> integrationSubtask = findIntegrationSubtask(subtasks);
            
            Map<String, Object> finalSolution = null;
            
            if (integrationSubtask != null) {
                // Find assigned agent
                String agentId = findAgentForSubtask(assignments, (String) integrationSubtask.get("subtask_id"));
                
                if (agentId != null) {
                    // Prepare integration inputs
                    Map<String, Object> integrationInputs = new HashMap<>();
                    
                    @SuppressWarnings("unchecked")
                    List<String> dependencies = (List<String>) integrationSubtask.get("dependencies");
                    
                    if (dependencies != null) {
                        for (String dependency : dependencies) {
                            if (subtaskResults.containsKey(dependency)) {
                                @SuppressWarnings("unchecked")
                                Map<String, Object> outputs = (Map<String, Object>) subtaskResults.get(dependency).get("outputs");
                                integrationInputs.put(dependency, outputs);
                            }
                        }
                    }
                    
                    // Execute integration subtask
                    Map<String, Object> integrationResult = executeSubtask(
                            agentId,
                            teamId,
                            contextId,
                            integrationSubtask,
                            integrationInputs,
                            problemSpec
                    );
                    
                    // Store result
                    subtaskResults.put((String) integrationSubtask.get("subtask_id"), integrationResult);
                    
                    @SuppressWarnings("unchecked")
                    Map<String, Object> outputs = (Map<String, Object>) integrationResult.get("outputs");
                    
                    finalSolution = outputs != null ? outputs.get("integrated_solution") : null;
                    
                    // Update context with integration completion
                    updateProblemContext(contextId, Map.of(
                            "progress", Map.of(
                                    "status_by_subtask", Map.of(
                                            integrationSubtask.get("subtask_id"), Map.of(
                                                    "status", "completed",
                                                    "agent_id", agentId,
                                                    "timestamp", LocalDateTime.now().toString()
                                            )
                                    )
                            )
                    ));
                }
            } else if (!subtasks.isEmpty()) {
                // If no integration subtask, use the result of the last subtask
                String lastSubtaskId = (String) subtasks.get(subtasks.size() - 1).get("subtask_id");
                
                if (subtaskResults.containsKey(lastSubtaskId)) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> outputs = (Map<String, Object>) subtaskResults.get(lastSubtaskId).get("outputs");
                    finalSolution = outputs;
                }
            }
            
            // Update session with solution
            session.setStatus(ProblemSolvingSession.SessionStatus.COMPLETED);
            session.setCompletedAt(LocalDateTime.now());
            session.setSolution(finalSolution != null ? finalSolution : new HashMap<>());
            sessionRepository.save(session);
            
            // Update context with session completion
            updateProblemContext(contextId, Map.of(
                    "solving_session", Map.of(
                            "session_id", sessionId,
                            "status", "completed",
                            "end_time", LocalDateTime.now().toString()
                    ),
                    "status", "completed",
                    "solutions", Map.of(
                            "final_solution", finalSolution,
                            "subtask_results", subtaskResults
                    )
            ));
            
            // Create problem solving result
            Map<String, Object> result = new HashMap<>();
            result.put("status", "success");
            result.put("problem_id", problemId);
            result.put("team_id", teamId);
            result.put("context_id", contextId);
            result.put("session_id", sessionId);
            result.put("solution", finalSolution);
            result.put("timestamp", LocalDateTime.now().toString());
            
            log.info("Problem solving coordination completed for problem: {}", problemId);
            
            return result;
            
        } catch (Exception e) {
            log.error("Error coordinating problem solving", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("problem_id", problemSpec.get("problem_id"));
            errorResult.put("message", e.getMessage());
            errorResult.put("timestamp", LocalDateTime.now().toString());
            
            return errorResult;
        }
    }
    
    /**
     * Solve a problem using collaborative problem solving.
     * 
     * @param problemSpec The problem specification
     * @param availableAgents List of available agent IDs
     * @return Problem solving result
     */
    public Map<String, Object> solveProblem(
            Map<String, Object> problemSpec,
            List<String> availableAgents) {
        
        try {
            log.info("Solving problem: {}", problemSpec.get("problem_id"));
            
            // Step 1: Analyze problem
            Map<String, Object> analysisResult = analyzeProblem(problemSpec);
            
            if ("error".equals(analysisResult.get("status"))) {
                return analysisResult;
            }
            
            // Check if problem is suitable for collaborative solving
            Boolean isCollaborative = (Boolean) analysisResult.get("is_collaborative");
            
            if (isCollaborative == null || !isCollaborative) {
                Map<String, Object> result = new HashMap<>();
                result.put("status", "warning");
                result.put("problem_id", problemSpec.get("problem_id"));
                result.put("message", "Problem is not suitable for collaborative solving");
                result.put("recommendation", "single_agent_solving");
                result.put("timestamp", LocalDateTime.now().toString());
                return result;
            }
            
            // Step 2: Decompose problem
            Map<String, Object> decompositionResult = decomposeProblem(problemSpec, analysisResult);
            
            if ("error".equals(decompositionResult.get("status"))) {
                return decompositionResult;
            }
            
            // Step 3: Form problem solving team
            Map<String, Object> teamResult = formProblemSolvingTeam(
                    problemSpec,
                    decompositionResult,
                    availableAgents
            );
            
            if ("error".equals(teamResult.get("status"))) {
                return teamResult;
            }
            
            // Step 4: Create problem solving context
            Map<String, Object> contextResult = createProblemSolvingContext(
                    problemSpec,
                    teamResult,
                    decompositionResult
            );
            
            if ("error".equals(contextResult.get("status"))) {
                return contextResult;
            }
            
            // Step 5: Coordinate problem solving
            return coordinateProblemSolving(
                    problemSpec,
                    teamResult,
                    contextResult,
                    decompositionResult
            );
            
        } catch (Exception e) {
            log.error("Error solving problem", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("problem_id", problemSpec.get("problem_id"));
            errorResult.put("message", e.getMessage());
            errorResult.put("timestamp", LocalDateTime.now().toString());
            
            return errorResult;
        }
    }
    
    /**
     * Determine if a problem is suitable for collaborative solving.
     * 
     * @param problemSpec The problem specification
     * @return Whether the problem is suitable for collaborative solving
     */
    private boolean determineIfCollaborative(Map<String, Object> problemSpec) {
        // Check complexity indicators
        @SuppressWarnings("unchecked")
        List<String> constraints = (List<String>) problemSpec.get("constraints");
        
        @SuppressWarnings("unchecked")
        List<String> requirements = (List<String>) problemSpec.get("requirements");
        
        String complexity = (String) problemSpec.get("complexity");
        
        @SuppressWarnings("unchecked")
        List<String> domains = (List<String>) problemSpec.get("domains");
        
        Integer estimatedTime = (Integer) problemSpec.get("estimated_time");
        
        int complexityScore = 0;
        int totalIndicators = 0;
        
        // Check constraints
        if (constraints != null && constraints.size() > 2) {
            complexityScore++;
        }
        totalIndicators++;
        
        // Check requirements
        if (requirements != null && requirements.size() > 3) {
            complexityScore++;
        }
        totalIndicators++;
        
        // Check complexity
        if ("medium".equals(complexity) || "high".equals(complexity)) {
            complexityScore++;
        }
        totalIndicators++;
        
        // Check domains
        if (domains != null && domains.size() > 1) {
            complexityScore++;
        }
        totalIndicators++;
        
        // Check estimated time
        if (estimatedTime != null && estimatedTime > 60) {
            complexityScore++;
        }
        totalIndicators++;
        
        // Problem is collaborative if majority of indicators suggest complexity
        return complexityScore >= totalIndicators / 2;
    }
    
    /**
     * Identify capabilities required to solve a problem.
     * 
     * @param problemSpec The problem specification
     * @return List of required capabilities
     */
    private List<Map<String, Object>> identifyRequiredCapabilities(Map<String, Object> problemSpec) {
        String problemType = (String) problemSpec.get("problem_type");
        
        @SuppressWarnings("unchecked")
        List<String> domains = (List<String>) problemSpec.get("domains");
        
        List<Map<String, Object>> capabilities = new ArrayList<>();
        
        // Add capabilities based on problem type
        if ("classification".equals(problemType)) {
            capabilities.add(Map.of(
                    "name", "classification",
                    "importance", "high",
                    "description", "Ability to classify data into categories"
            ));
        } else if ("regression".equals(problemType)) {
            capabilities.add(Map.of(
                    "name", "regression",
                    "importance", "high",
                    "description", "Ability to predict continuous values"
            ));
        } else if ("clustering".equals(problemType)) {
            capabilities.add(Map.of(
                    "name", "clustering",
                    "importance", "high",
                    "description", "Ability to group similar data points"
            ));
        } else if ("optimization".equals(problemType)) {
            capabilities.add(Map.of(
                    "name", "optimization",
                    "importance", "high",
                    "description", "Ability to find optimal solutions"
            ));
        } else if ("recommendation".equals(problemType)) {
            capabilities.add(Map.of(
                    "name", "recommendation",
                    "importance", "high",
                    "description", "Ability to recommend items or actions"
            ));
        } else if ("natural_language".equals(problemType)) {
            capabilities.add(Map.of(
                    "name", "natural_language_processing",
                    "importance", "high",
                    "description", "Ability to process and understand natural language"
            ));
        } else if ("computer_vision".equals(problemType)) {
            capabilities.add(Map.of(
                    "name", "computer_vision",
                    "importance", "high",
                    "description", "Ability to process and understand visual data"
            ));
        }
        
        // Add capabilities based on domains
        if (domains != null) {
            for (String domain : domains) {
                capabilities.add(Map.of(
                        "name", "domain_" + domain,
                        "importance", "medium",
                        "description", "Knowledge of " + domain + " domain"
                ));
            }
        }
        
        // Add general capabilities
        capabilities.add(Map.of(
                "name", "data_analysis",
                "importance", "medium",
                "description", "Ability to analyze and interpret data"
        ));
        
        capabilities.add(Map.of(
                "name", "problem_decomposition",
                "importance", "medium",
                "description", "Ability to break down complex problems"
        ));
        
        capabilities.add(Map.of(
                "name", "solution_integration",
                "importance", "medium",
                "description", "Ability to integrate partial solutions"
        ));
        
        capabilities.add(Map.of(
                "name", "verification",
                "importance", "medium",
                "description", "Ability to verify solutions"
        ));
        
        return capabilities;
    }
    
    /**
     * Determine the approach for decomposing a problem.
     * 
     * @param problemSpec The problem specification
     * @return Decomposition approach
     */
    private Map<String, Object> determineDecompositionApproach(Map<String, Object> problemSpec) {
        String problemType = (String) problemSpec.get("problem_type");
        
        @SuppressWarnings("unchecked")
        List<String> domains = (List<String>) problemSpec.get("domains");
        
        Integer dataSize = (Integer) problemSpec.get("data_size");
        String complexity = (String) problemSpec.get("complexity");
        
        Map<String, Object> approach = new HashMap<>();
        
        // Determine approach type based on problem characteristics
        if (domains != null && domains.size() > 1) {
            // Multiple domains suggest domain decomposition
            approach.put("type", "domain");
            
            List<Map<String, Object>> domainsList = new ArrayList<>();
            
            for (String domain : domains) {
                domainsList.add(Map.of(
                        "name", domain,
                        "description", "Solve aspects related to " + domain,
                        "inputs", List.of(),
                        "outputs", List.of(),
                        "dependencies", List.of(),
                        "required_capabilities", List.of("domain_" + domain)
                ));
            }
            
            approach.put("domains", domainsList);
            
        } else if (("classification".equals(problemType) || 
                   "regression".equals(problemType) || 
                   "clustering".equals(problemType)) && 
                   dataSize != null && dataSize > 1000) {
            // Large data problems suggest data decomposition
            approach.put("type", "data");
            
            @SuppressWarnings("unchecked")
            List<String> featureGroups = (List<String>) problemSpec.get("feature_groups");
            
            if (featureGroups == null) {
                featureGroups = List.of("group1", "group2");
            }
            
            List<Map<String, Object>> partitions = new ArrayList<>();
            
            for (String group : featureGroups) {
                partitions.add(Map.of(
                        "name", group,
                        "description", "Process features in " + group,
                        "filter", "features.group == '" + group + "'",
                        "inputs", List.of(),
                        "outputs", List.of(),
                        "dependencies", List.of(),
                        "required_capabilities", List.of("data_analysis")
                ));
            }
            
            approach.put("partitions", partitions);
            
        } else if ("high".equals(complexity)) {
            // High complexity suggests hierarchical decomposition
            approach.put("type", "hierarchical");
            
            List<Map<String, Object>> levels = new ArrayList<>();
            
            // Create 3 levels
            for (int i = 0; i < 3; i++) {
                List<Map<String, Object>> levelSubtasks = new ArrayList<>();
                
                // Create 2 subtasks per level
                for (int j = 0; j < 2; j++) {
                    levelSubtasks.add(Map.of(
                            "description", "Level " + i + " subtask " + j,
                            "inputs", List.of(),
                            "outputs", List.of(),
                            "dependencies", List.of(),
                            "required_capabilities", List.of()
                    ));
                }
                
                levels.add(Map.of(
                        "level", i,
                        "subtasks", levelSubtasks
                ));
            }
            
            approach.put("levels", levels);
            
        } else {
            // Default to functional decomposition
            approach.put("type", "functional");
            
            List<Map<String, Object>> functions = new ArrayList<>();
            
            // Create functions based on problem type
            if ("classification".equals(problemType)) {
                functions.add(Map.of(
                        "name", "data_preprocessing",
                        "description", "Preprocess and clean data",
                        "inputs", List.of("raw_data"),
                        "outputs", List.of("preprocessed_data"),
                        "dependencies", List.of(),
                        "required_capabilities", List.of("data_analysis")
                ));
                
                functions.add(Map.of(
                        "name", "feature_engineering",
                        "description", "Engineer features for classification",
                        "inputs", List.of("preprocessed_data"),
                        "outputs", List.of("engineered_features"),
                        "dependencies", List.of("data_preprocessing"),
                        "required_capabilities", List.of("feature_engineering")
                ));
                
                functions.add(Map.of(
                        "name", "model_training",
                        "description", "Train classification model",
                        "inputs", List.of("engineered_features"),
                        "outputs", List.of("trained_model"),
                        "dependencies", List.of("feature_engineering"),
                        "required_capabilities", List.of("classification")
                ));
                
                functions.add(Map.of(
                        "name", "model_evaluation",
                        "description", "Evaluate classification model",
                        "inputs", List.of("trained_model", "engineered_features"),
                        "outputs", List.of("evaluation_results"),
                        "dependencies", List.of("model_training"),
                        "required_capabilities", List.of("model_evaluation")
                ));
                
            } else if ("optimization".equals(problemType)) {
                functions.add(Map.of(
                        "name", "problem_formulation",
                        "description", "Formulate optimization problem",
                        "inputs", List.of("problem_description"),
                        "outputs", List.of("formulated_problem"),
                        "dependencies", List.of(),
                        "required_capabilities", List.of("optimization")
                ));
                
                functions.add(Map.of(
                        "name", "constraint_analysis",
                        "description", "Analyze constraints",
                        "inputs", List.of("formulated_problem"),
                        "outputs", List.of("analyzed_constraints"),
                        "dependencies", List.of("problem_formulation"),
                        "required_capabilities", List.of("constraint_analysis")
                ));
                
                functions.add(Map.of(
                        "name", "algorithm_selection",
                        "description", "Select optimization algorithm",
                        "inputs", List.of("formulated_problem", "analyzed_constraints"),
                        "outputs", List.of("selected_algorithm"),
                        "dependencies", List.of("constraint_analysis"),
                        "required_capabilities", List.of("algorithm_selection")
                ));
                
                functions.add(Map.of(
                        "name", "solution_computation",
                        "description", "Compute optimal solution",
                        "inputs", List.of("formulated_problem", "selected_algorithm"),
                        "outputs", List.of("computed_solution"),
                        "dependencies", List.of("algorithm_selection"),
                        "required_capabilities", List.of("optimization")
                ));
                
            } else {
                // Generic functional decomposition
                functions.add(Map.of(
                        "name", "problem_analysis",
                        "description", "Analyze problem requirements",
                        "inputs", List.of("problem_description"),
                        "outputs", List.of("analyzed_problem"),
                        "dependencies", List.of(),
                        "required_capabilities", List.of("problem_analysis")
                ));
                
                functions.add(Map.of(
                        "name", "solution_design",
                        "description", "Design solution approach",
                        "inputs", List.of("analyzed_problem"),
                        "outputs", List.of("solution_design"),
                        "dependencies", List.of("problem_analysis"),
                        "required_capabilities", List.of("solution_design")
                ));
                
                functions.add(Map.of(
                        "name", "solution_implementation",
                        "description", "Implement designed solution",
                        "inputs", List.of("solution_design"),
                        "outputs", List.of("implemented_solution"),
                        "dependencies", List.of("solution_design"),
                        "required_capabilities", List.of("implementation")
                ));
                
                functions.add(Map.of(
                        "name", "solution_testing",
                        "description", "Test implemented solution",
                        "inputs", List.of("implemented_solution"),
                        "outputs", List.of("tested_solution"),
                        "dependencies", List.of("solution_implementation"),
                        "required_capabilities", List.of("testing")
                ));
            }
            
            approach.put("functions", functions);
        }
        
        return approach;
    }
    
    /**
     * Estimate resources required to solve a problem.
     * 
     * @param problemSpec The problem specification
     * @return Resource requirements
     */
    private Map<String, Object> estimateResourceRequirements(Map<String, Object> problemSpec) {
        String complexity = (String) problemSpec.get("complexity");
        Integer dataSize = (Integer) problemSpec.get("data_size");
        
        Map<String, Object> requirements = new HashMap<>();
        
        // Initialize requirements
        requirements.put("computation", "low");
        requirements.put("memory", "low");
        requirements.put("time", "low");
        requirements.put("agents", 2);
        
        // Adjust based on complexity
        if ("medium".equals(complexity)) {
            requirements.put("computation", "medium");
            requirements.put("memory", "medium");
            requirements.put("time", "medium");
            requirements.put("agents", 3);
        } else if ("high".equals(complexity)) {
            requirements.put("computation", "high");
            requirements.put("memory", "high");
            requirements.put("time", "high");
            requirements.put("agents", 5);
        }
        
        // Adjust based on data size
        if (dataSize != null) {
            if (dataSize > 1000) {
                requirements.put("memory", "medium");
            }
            if (dataSize > 10000) {
                requirements.put("memory", "high");
                requirements.put("computation", "high");
            }
        }
        
        // Add specific estimates
        Map<String, Integer> timeMap = Map.of(
                "low", 30,
                "medium", 120,
                "high", 360
        );
        
        requirements.put("estimated_time_minutes", timeMap.get(requirements.get("time")));
        
        Map<String, Integer> memoryMap = Map.of(
                "low", 512,
                "medium", 2048,
                "high", 8192
        );
        
        requirements.put("estimated_memory_mb", memoryMap.get(requirements.get("memory")));
        
        return requirements;
    }
    
    /**
     * Identify knowledge relevant to solving a problem.
     * 
     * @param problemSpec The problem specification
     * @return List of relevant knowledge items
     */
    private List<Map<String, Object>> identifyRelevantKnowledge(Map<String, Object> problemSpec) {
        String problemType = (String) problemSpec.get("problem_type");
        
        @SuppressWarnings("unchecked")
        List<String> domains = (List<String>) problemSpec.get("domains");
        
        List<Map<String, Object>> knowledge = new ArrayList<>();
        
        // Add knowledge based on problem type
        if ("classification".equals(problemType)) {
            knowledge.add(Map.of(
                    "type", "model",
                    "name", "classification_models",
                    "description", "Models for classification tasks",
                    "relevance", "high"
            ));
        } else if ("regression".equals(problemType)) {
            knowledge.add(Map.of(
                    "type", "model",
                    "name", "regression_models",
                    "description", "Models for regression tasks",
                    "relevance", "high"
            ));
        } else if ("clustering".equals(problemType)) {
            knowledge.add(Map.of(
                    "type", "model",
                    "name", "clustering_models",
                    "description", "Models for clustering tasks",
                    "relevance", "high"
            ));
        } else if ("optimization".equals(problemType)) {
            knowledge.add(Map.of(
                    "type", "algorithm",
                    "name", "optimization_algorithms",
                    "description", "Algorithms for optimization problems",
                    "relevance", "high"
            ));
        }
        
        // Add knowledge based on domains
        if (domains != null) {
            for (String domain : domains) {
                knowledge.add(Map.of(
                        "type", "domain",
                        "name", domain + "_knowledge",
                        "description", "Knowledge about " + domain,
                        "relevance", "medium"
                ));
            }
        }
        
        // Add general knowledge
        knowledge.add(Map.of(
                "type", "methodology",
                "name", "problem_solving_methodology",
                "description", "Methodologies for solving complex problems",
                "relevance", "medium"
        ));
        
        return knowledge;
    }
    
    /**
     * Determine the approach for verifying a solution.
     * 
     * @param problemSpec The problem specification
     * @return Verification approach
     */
    private Map<String, Object> determineVerificationApproach(Map<String, Object> problemSpec) {
        String problemType = (String) problemSpec.get("problem_type");
        
        Map<String, Object> approach = new HashMap<>();
        
        // Determine verification method based on problem type
        if ("classification".equals(problemType)) {
            approach.put("method", "performance_metrics");
            approach.put("metrics", List.of("accuracy", "precision", "recall", "f1"));
            approach.put("thresholds", Map.of(
                    "accuracy", 0.8,
                    "precision", 0.8,
                    "recall", 0.8,
                    "f1", 0.8
            ));
        } else if ("regression".equals(problemType)) {
            approach.put("method", "performance_metrics");
            approach.put("metrics", List.of("mse", "mae", "r2"));
            approach.put("thresholds", Map.of(
                    "mse", 0.2,
                    "mae", 0.3,
                    "r2", 0.7
            ));
        } else if ("clustering".equals(problemType)) {
            approach.put("method", "performance_metrics");
            approach.put("metrics", List.of("silhouette", "davies_bouldin", "calinski_harabasz"));
            approach.put("thresholds", Map.of(
                    "silhouette", 0.6,
                    "davies_bouldin", 0.5,
                    "calinski_harabasz", 10
            ));
        } else if ("optimization".equals(problemType)) {
            approach.put("method", "constraint_satisfaction");
            approach.put("metrics", List.of("objective_value", "constraint_violation"));
            approach.put("thresholds", Map.of(
                    "constraint_violation", 0.001
            ));
        } else {
            // Default to testing
            approach.put("method", "testing");
            approach.put("metrics", List.of("test_coverage", "test_success_rate"));
            approach.put("thresholds", Map.of(
                    "test_coverage", 0.9,
                    "test_success_rate", 0.95
            ));
        }
        
        return approach;
    }
    
    /**
     * Determine the overall approach for solving a problem.
     * 
     * @param problemSpec The problem specification
     * @param requiredCapabilities List of required capabilities
     * @return Solving approach
     */
    private Map<String, Object> determineSolvingApproach(
            Map<String, Object> problemSpec,
            List<Map<String, Object>> requiredCapabilities) {
        
        String problemType = (String) problemSpec.get("problem_type");
        String complexity = (String) problemSpec.get("complexity");
        
        Map<String, Object> approach = new HashMap<>();
        
        // Determine strategy based on problem type and complexity
        if ("high".equals(complexity)) {
            approach.put("strategy", "divide_and_conquer");
        } else if ("classification".equals(problemType) || 
                  "regression".equals(problemType) || 
                  "clustering".equals(problemType)) {
            approach.put("strategy", "model_ensemble");
        } else if ("optimization".equals(problemType)) {
            approach.put("strategy", "constraint_decomposition");
        } else {
            approach.put("strategy", "functional_decomposition");
        }
        
        // Determine coordination approach
        if (requiredCapabilities.size() > 5) {
            approach.put("coordination", "hierarchical");
        } else {
            approach.put("coordination", "centralized");
        }
        
        // Determine learning integration approach
        if ("classification".equals(problemType) || 
            "regression".equals(problemType) || 
            "clustering".equals(problemType)) {
            approach.put("learning_integration", "federated");
        } else {
            approach.put("learning_integration", "knowledge_sharing");
        }
        
        return approach;
    }
    
    /**
     * Create subtasks based on decomposition approach.
     * 
     * @param problemSpec The problem specification
     * @param decompositionApproach Decomposition approach
     * @return List of subtasks
     */
    private List<Map<String, Object>> createSubtasks(
            Map<String, Object> problemSpec,
            Map<String, Object> decompositionApproach) {
        
        String problemId = (String) problemSpec.get("problem_id");
        String approachType = (String) decompositionApproach.get("type");
        
        List<Map<String, Object>> subtasks = new ArrayList<>();
        
        if ("functional".equals(approachType)) {
            // Functional decomposition
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> functions = (List<Map<String, Object>>) decompositionApproach.get("functions");
            
            if (functions != null) {
                for (int i = 0; i < functions.size(); i++) {
                    Map<String, Object> function = functions.get(i);
                    
                    Map<String, Object> subtask = new HashMap<>();
                    subtask.put("subtask_id", problemId + "_subtask_" + i);
                    subtask.put("type", "functional");
                    subtask.put("function", function.get("name"));
                    subtask.put("description", function.get("description"));
                    subtask.put("inputs", function.get("inputs"));
                    subtask.put("outputs", function.get("outputs"));
                    subtask.put("dependencies", function.get("dependencies"));
                    subtask.put("required_capabilities", function.get("required_capabilities"));
                    subtask.put("priority", function.get("priority", "medium"));
                    
                    subtasks.add(subtask);
                }
            }
            
        } else if ("domain".equals(approachType)) {
            // Domain decomposition
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> domains = (List<Map<String, Object>>) decompositionApproach.get("domains");
            
            if (domains != null) {
                for (int i = 0; i < domains.size(); i++) {
                    Map<String, Object> domain = domains.get(i);
                    
                    Map<String, Object> subtask = new HashMap<>();
                    subtask.put("subtask_id", problemId + "_subtask_" + i);
                    subtask.put("type", "domain");
                    subtask.put("domain", domain.get("name"));
                    subtask.put("description", domain.get("description"));
                    subtask.put("inputs", domain.get("inputs"));
                    subtask.put("outputs", domain.get("outputs"));
                    subtask.put("dependencies", domain.get("dependencies"));
                    subtask.put("required_capabilities", domain.get("required_capabilities"));
                    subtask.put("priority", domain.get("priority", "medium"));
                    
                    subtasks.add(subtask);
                }
            }
            
        } else if ("data".equals(approachType)) {
            // Data decomposition
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> partitions = (List<Map<String, Object>>) decompositionApproach.get("partitions");
            
            if (partitions != null) {
                for (int i = 0; i < partitions.size(); i++) {
                    Map<String, Object> partition = partitions.get(i);
                    
                    Map<String, Object> subtask = new HashMap<>();
                    subtask.put("subtask_id", problemId + "_subtask_" + i);
                    subtask.put("type", "data");
                    subtask.put("partition", partition.get("name"));
                    subtask.put("description", partition.get("description"));
                    subtask.put("data_filter", partition.get("filter"));
                    subtask.put("inputs", partition.get("inputs"));
                    subtask.put("outputs", partition.get("outputs"));
                    subtask.put("dependencies", partition.get("dependencies"));
                    subtask.put("required_capabilities", partition.get("required_capabilities"));
                    subtask.put("priority", partition.get("priority", "medium"));
                    
                    subtasks.add(subtask);
                }
            }
            
        } else if ("hierarchical".equals(approachType)) {
            // Hierarchical decomposition
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> levels = (List<Map<String, Object>>) decompositionApproach.get("levels");
            
            if (levels != null) {
                for (int levelIdx = 0; levelIdx < levels.size(); levelIdx++) {
                    Map<String, Object> level = levels.get(levelIdx);
                    
                    @SuppressWarnings("unchecked")
                    List<Map<String, Object>> levelSubtasks = (List<Map<String, Object>>) level.get("subtasks");
                    
                    if (levelSubtasks != null) {
                        for (int i = 0; i < levelSubtasks.size(); i++) {
                            Map<String, Object> levelSubtask = levelSubtasks.get(i);
                            
                            Map<String, Object> subtask = new HashMap<>();
                            subtask.put("subtask_id", problemId + "_level_" + levelIdx + "_subtask_" + i);
                            subtask.put("type", "hierarchical");
                            subtask.put("level", levelIdx);
                            subtask.put("description", levelSubtask.get("description"));
                            subtask.put("inputs", levelSubtask.get("inputs"));
                            subtask.put("outputs", levelSubtask.get("outputs"));
                            subtask.put("dependencies", levelSubtask.get("dependencies"));
                            subtask.put("required_capabilities", levelSubtask.get("required_capabilities"));
                            subtask.put("priority", levelSubtask.get("priority", "medium"));
                            
                            subtasks.add(subtask);
                        }
                    }
                }
            }
        }
        
        // Add integration subtask if needed
        if (subtasks.size() > 1) {
            Map<String, Object> integrationSubtask = new HashMap<>();
            integrationSubtask.put("subtask_id", problemId + "_integration");
            integrationSubtask.put("type", "integration");
            integrationSubtask.put("description", "Integrate solutions from all subtasks");
            
            List<String> subtaskIds = new ArrayList<>();
            for (Map<String, Object> subtask : subtasks) {
                subtaskIds.add((String) subtask.get("subtask_id"));
            }
            
            integrationSubtask.put("inputs", subtaskIds);
            integrationSubtask.put("outputs", List.of("integrated_solution"));
            integrationSubtask.put("dependencies", subtaskIds);
            integrationSubtask.put("required_capabilities", List.of("solution_integration", "verification"));
            integrationSubtask.put("priority", "high");
            
            subtasks.add(integrationSubtask);
        }
        
        return subtasks;
    }
    
    /**
     * Create a dependency graph for subtasks.
     * 
     * @param subtasks List of subtasks
     * @return Dependency graph
     */
    private Map<String, List<String>> createDependencyGraph(List<Map<String, Object>> subtasks) {
        Map<String, List<String>> graph = new HashMap<>();
        
        // Create nodes for all subtasks
        for (Map<String, Object> subtask : subtasks) {
            String subtaskId = (String) subtask.get("subtask_id");
            graph.put(subtaskId, new ArrayList<>());
        }
        
        // Add edges based on dependencies
        for (Map<String, Object> subtask : subtasks) {
            String subtaskId = (String) subtask.get("subtask_id");
            
            @SuppressWarnings("unchecked")
            List<String> dependencies = (List<String>) subtask.get("dependencies");
            
            if (dependencies != null) {
                for (String dependency : dependencies) {
                    if (graph.containsKey(dependency)) {
                        graph.get(dependency).add(subtaskId);
                    }
                }
            }
        }
        
        return graph;
    }
    
    /**
     * Collect required capabilities from subtasks.
     * 
     * @param subtasks List of subtasks
     * @return List of required capabilities
     */
    private List<String> collectRequiredCapabilities(List<Map<String, Object>> subtasks) {
        Set<String> capabilities = new HashSet<>();
        
        for (Map<String, Object> subtask : subtasks) {
            @SuppressWarnings("unchecked")
            List<String> requiredCapabilities = (List<String>) subtask.get("required_capabilities");
            
            if (requiredCapabilities != null) {
                capabilities.addAll(requiredCapabilities);
            }
        }
        
        return new ArrayList<>(capabilities);
    }
    
    /**
     * Assign subtasks to agents based on capabilities.
     * 
     * @param subtasks List of subtasks
     * @param agents List of agent IDs
     * @param capabilitiesCoverage Map of capabilities to agents
     * @return Map of agent IDs to assigned subtask IDs
     */
    private Map<String, List<String>> assignSubtasksToAgents(
            List<Map<String, Object>> subtasks,
            List<String> agents,
            Map<String, List<String>> capabilitiesCoverage) {
        
        Map<String, List<String>> assignments = new HashMap<>();
        
        // Initialize assignments
        for (String agentId : agents) {
            assignments.put(agentId, new ArrayList<>());
        }
        
        // Track assigned subtasks
        Set<String> assignedSubtasks = new HashSet<>();
        
        // First pass: assign based on capabilities
        for (Map<String, Object> subtask : subtasks) {
            String subtaskId = (String) subtask.get("subtask_id");
            
            @SuppressWarnings("unchecked")
            List<String> requiredCapabilities = (List<String>) subtask.get("required_capabilities");
            
            // Find best agent for this subtask
            String bestAgent = null;
            double bestScore = -1;
            
            for (String agentId : agents) {
                // Skip agents with too many subtasks
                if (assignments.get(agentId).size() >= 5) {
                    continue;
                }
                
                // Calculate capability match score
                double score = 0;
                
                if (requiredCapabilities != null) {
                    for (String capability : requiredCapabilities) {
                        @SuppressWarnings("unchecked")
                        List<String> agentsWithCapability = capabilitiesCoverage.get(capability);
                        
                        if (agentsWithCapability != null && agentsWithCapability.contains(agentId)) {
                            score += 1;
                        }
                    }
                }
                
                // Adjust score based on current workload
                score = score / (1 + assignments.get(agentId).size());
                
                if (score > bestScore) {
                    bestScore = score;
                    bestAgent = agentId;
                }
            }
            
            // Assign subtask to best agent
            if (bestAgent != null) {
                assignments.get(bestAgent).add(subtaskId);
                assignedSubtasks.add(subtaskId);
            }
        }
        
        // Second pass: assign remaining subtasks
        for (Map<String, Object> subtask : subtasks) {
            String subtaskId = (String) subtask.get("subtask_id");
            
            if (!assignedSubtasks.contains(subtaskId)) {
                // Find agent with fewest assignments
                String bestAgent = null;
                int minAssignments = Integer.MAX_VALUE;
                
                for (String agentId : agents) {
                    int numAssignments = assignments.get(agentId).size();
                    
                    if (numAssignments < minAssignments) {
                        minAssignments = numAssignments;
                        bestAgent = agentId;
                    }
                }
                
                // Assign subtask
                if (bestAgent != null) {
                    assignments.get(bestAgent).add(subtaskId);
                    assignedSubtasks.add(subtaskId);
                }
            }
        }
        
        return assignments;
    }
    
    /**
     * Create an execution plan for subtasks based on dependencies.
     * 
     * @param subtasks List of subtasks
     * @param dependencyGraph Dependency graph
     * @return Execution plan as list of phases, each containing subtask IDs
     */
    private List<List<String>> createExecutionPlan(
            List<Map<String, Object>> subtasks,
            Map<String, List<String>> dependencyGraph) {
        
        // Create reverse dependency graph
        Map<String, List<String>> reverseGraph = new HashMap<>();
        
        for (Map<String, Object> subtask : subtasks) {
            String subtaskId = (String) subtask.get("subtask_id");
            reverseGraph.put(subtaskId, new ArrayList<>());
        }
        
        for (Map<String, Object> subtask : subtasks) {
            String subtaskId = (String) subtask.get("subtask_id");
            
            @SuppressWarnings("unchecked")
            List<String> dependencies = (List<String>) subtask.get("dependencies");
            
            if (dependencies != null) {
                for (String dependency : dependencies) {
                    if (reverseGraph.containsKey(dependency)) {
                        reverseGraph.get(dependency).add(subtaskId);
                    }
                }
            }
        }
        
        // Calculate in-degree for each subtask
        Map<String, Integer> inDegree = new HashMap<>();
        
        for (Map<String, Object> subtask : subtasks) {
            String subtaskId = (String) subtask.get("subtask_id");
            
            @SuppressWarnings("unchecked")
            List<String> dependencies = (List<String>) subtask.get("dependencies");
            
            inDegree.put(subtaskId, dependencies != null ? dependencies.size() : 0);
        }
        
        // Create execution plan
        List<List<String>> plan = new ArrayList<>();
        Set<String> remaining = new HashSet<>();
        
        for (Map<String, Object> subtask : subtasks) {
            remaining.add((String) subtask.get("subtask_id"));
        }
        
        while (!remaining.isEmpty()) {
            // Find subtasks with no dependencies
            List<String> currentPhase = new ArrayList<>();
            
            for (String subtaskId : new ArrayList<>(remaining)) {
                if (inDegree.get(subtaskId) == 0) {
                    currentPhase.add(subtaskId);
                    remaining.remove(subtaskId);
                }
            }
            
            if (currentPhase.isEmpty()) {
                // Circular dependency detected
                log.warning("Circular dependency detected in subtasks");
                
                // Break the cycle by selecting a random subtask
                String subtaskId = remaining.iterator().next();
                currentPhase.add(subtaskId);
                remaining.remove(subtaskId);
            }
            
            // Add phase to plan
            plan.add(currentPhase);
            
            // Update in-degree for remaining subtasks
            for (String subtaskId : currentPhase) {
                for (String dependent : reverseGraph.get(subtaskId)) {
                    if (inDegree.containsKey(dependent)) {
                        inDegree.put(dependent, inDegree.get(dependent) - 1);
                    }
                }
            }
        }
        
        return plan;
    }
    
    /**
     * Find a subtask by ID.
     * 
     * @param subtasks List of subtasks
     * @param subtaskId Subtask ID
     * @return Subtask with the specified ID, or null if not found
     */
    private Map<String, Object> findSubtaskById(List<Map<String, Object>> subtasks, String subtaskId) {
        for (Map<String, Object> subtask : subtasks) {
            if (subtaskId.equals(subtask.get("subtask_id"))) {
                return subtask;
            }
        }
        
        return null;
    }
    
    /**
     * Find the agent assigned to a subtask.
     * 
     * @param assignments Map of agent IDs to assigned subtask IDs
     * @param subtaskId Subtask ID
     * @return Agent ID assigned to the subtask, or null if not found
     */
    private String findAgentForSubtask(Map<String, List<String>> assignments, String subtaskId) {
        for (Map.Entry<String, List<String>> entry : assignments.entrySet()) {
            if (entry.getValue().contains(subtaskId)) {
                return entry.getKey();
            }
        }
        
        return null;
    }
    
    /**
     * Find the integration subtask.
     * 
     * @param subtasks List of subtasks
     * @return Integration subtask, or null if not found
     */
    private Map<String, Object> findIntegrationSubtask(List<Map<String, Object>> subtasks) {
        for (Map<String, Object> subtask : subtasks) {
            if ("integration".equals(subtask.get("type"))) {
                return subtask;
            }
        }
        
        return null;
    }
    
    /**
     * Execute a subtask using an agent.
     * 
     * @param agentId ID of the agent
     * @param teamId ID of the team
     * @param contextId ID of the context
     * @param subtask Subtask specification
     * @param inputs Inputs for the subtask
     * @param problemSpec Original problem specification
     * @return Subtask execution result
     */
    private Map<String, Object> executeSubtask(
            String agentId,
            String teamId,
            String contextId,
            Map<String, Object> subtask,
            Map<String, Object> inputs,
            Map<String, Object> problemSpec) {
        
        try {
            log.info("Executing subtask {} using agent {}", subtask.get("subtask_id"), agentId);
            
            // Create execution request
            Map<String, Object> executionRequest = new HashMap<>();
            executionRequest.put("agent_id", agentId);
            executionRequest.put("team_id", teamId);
            executionRequest.put("context_id", contextId);
            executionRequest.put("subtask_id", subtask.get("subtask_id"));
            executionRequest.put("subtask_type", subtask.get("type"));
            executionRequest.put("description", subtask.get("description"));
            executionRequest.put("inputs", inputs);
            executionRequest.put("problem_spec", problemSpec);
            executionRequest.put("timeout_seconds", 300);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create HTTP entity
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(executionRequest, headers);
            
            // Call collaboration API
            ResponseEntity<Map> response = restTemplate.exchange(
                    collaborationApiUrl + "/agents/" + agentId + "/execute",
                    HttpMethod.POST,
                    entity,
                    Map.class);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> executionResult = response.getBody();
            
            log.info("Subtask execution completed: {}", executionResult);
            
            // Return execution result
            Map<String, Object> result = new HashMap<>();
            result.put("status", executionResult.get("status"));
            result.put("subtask_id", subtask.get("subtask_id"));
            result.put("agent_id", agentId);
            result.put("outputs", executionResult.get("outputs"));
            result.put("metrics", executionResult.get("metrics"));
            result.put("timestamp", LocalDateTime.now().toString());
            
            return result;
            
        } catch (Exception e) {
            log.error("Error executing subtask", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("subtask_id", subtask.get("subtask_id"));
            errorResult.put("message", e.getMessage());
            errorResult.put("outputs", new HashMap<>());
            errorResult.put("timestamp", LocalDateTime.now().toString());
            
            return errorResult;
        }
    }
    
    /**
     * Update the problem solving context with new data.
     * 
     * @param contextId ID of the context to update
     * @param updateData Data to update in the context
     * @return Whether the update was successful
     */
    private boolean updateProblemContext(String contextId, Map<String, Object> updateData) {
        try {
            // Create update request
            Map<String, Object> updateRequest = new HashMap<>();
            updateRequest.put("context_id", contextId);
            updateRequest.put("update_data", updateData);
            updateRequest.put("timestamp", LocalDateTime.now().toString());
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create HTTP entity
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(updateRequest, headers);
            
            // Call collaboration API
            ResponseEntity<Map> response = restTemplate.exchange(
                    collaborationApiUrl + "/contexts/" + contextId,
                    HttpMethod.PATCH,
                    entity,
                    Map.class);
            
            return response.getStatusCode().is2xxSuccessful();
            
        } catch (Exception e) {
            log.error("Error updating problem context", e);
            return false;
        }
    }
    
    /**
     * Determine the problem type from a problem specification.
     * 
     * @param problemSpec The problem specification
     * @return The problem type
     */
    private ProblemSolvingSession.ProblemType determineProblemType(Map<String, Object> problemSpec) {
        String problemType = (String) problemSpec.get("problem_type");
        
        if ("classification".equals(problemType)) {
            return ProblemSolvingSession.ProblemType.CLASSIFICATION;
        } else if ("regression".equals(problemType)) {
            return ProblemSolvingSession.ProblemType.REGRESSION;
        } else if ("clustering".equals(problemType)) {
            return ProblemSolvingSession.ProblemType.CLUSTERING;
        } else if ("optimization".equals(problemType)) {
            return ProblemSolvingSession.ProblemType.OPTIMIZATION;
        } else if ("recommendation".equals(problemType)) {
            return ProblemSolvingSession.ProblemType.RECOMMENDATION;
        } else if ("natural_language".equals(problemType)) {
            return ProblemSolvingSession.ProblemType.NATURAL_LANGUAGE;
        } else if ("computer_vision".equals(problemType)) {
            return ProblemSolvingSession.ProblemType.COMPUTER_VISION;
        } else {
            return ProblemSolvingSession.ProblemType.CUSTOM;
        }
    }
}
