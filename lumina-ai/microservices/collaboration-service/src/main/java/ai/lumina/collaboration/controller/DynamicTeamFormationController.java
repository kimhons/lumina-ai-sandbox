package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.Team;
import ai.lumina.collaboration.model.Task;
import ai.lumina.collaboration.model.Agent;
import ai.lumina.collaboration.service.AdvancedTeamFormationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * REST controller for dynamic team formation operations.
 */
@RestController
@RequestMapping("/api/v1/collaboration/teams")
public class DynamicTeamFormationController {

    private static final Logger logger = LoggerFactory.getLogger(DynamicTeamFormationController.class);

    @Autowired
    private AdvancedTeamFormationService teamFormationService;

    /**
     * Form a team for a specific task.
     *
     * @param taskId The ID of the task for which to form a team
     * @return The formed team
     */
    @PostMapping("/form/{taskId}")
    public ResponseEntity<Team> formTeamForTask(@PathVariable Long taskId) {
        logger.info("Received request to form team for task ID: {}", taskId);
        Team team = teamFormationService.formTeamForTask(taskId);
        return ResponseEntity.ok(team);
    }

    /**
     * Asynchronously form a team for a specific task.
     *
     * @param taskId The ID of the task for which to form a team
     * @return A CompletableFuture containing the formed team
     */
    @PostMapping("/form/async/{taskId}")
    public CompletableFuture<ResponseEntity<Team>> formTeamForTaskAsync(@PathVariable Long taskId) {
        logger.info("Received request to asynchronously form team for task ID: {}", taskId);
        return teamFormationService.formTeamForTaskAsync(taskId)
                .thenApply(ResponseEntity::ok);
    }

    /**
     * Optimize an existing team.
     *
     * @param teamId The ID of the team to optimize
     * @return The optimized team
     */
    @PutMapping("/optimize/{teamId}")
    public ResponseEntity<Team> optimizeTeam(@PathVariable Long teamId) {
        logger.info("Received request to optimize team ID: {}", teamId);
        Team optimizedTeam = teamFormationService.optimizeTeam(teamId);
        return ResponseEntity.ok(optimizedTeam);
    }

    /**
     * Get team recommendations for a task.
     *
     * @param taskId The ID of the task for which to get recommendations
     * @param count The number of recommendations to generate (optional)
     * @return A list of recommended teams
     */
    @GetMapping("/recommendations/{taskId}")
    public ResponseEntity<List<Team>> getTeamRecommendations(
            @PathVariable Long taskId,
            @RequestParam(defaultValue = "3") int count) {
        logger.info("Received request for team recommendations for task ID: {}", taskId);
        List<Team> recommendations = teamFormationService.getTeamRecommendations(taskId, count);
        return ResponseEntity.ok(recommendations);
    }

    /**
     * Analyze team formation history.
     *
     * @return Analysis results
     */
    @GetMapping("/analysis")
    public ResponseEntity<Map<String, Object>> analyzeTeamFormationHistory() {
        logger.info("Received request to analyze team formation history");
        Map<String, Object> analysis = teamFormationService.analyzeTeamFormationHistory();
        return ResponseEntity.ok(analysis);
    }

    /**
     * Update agent collaboration scores based on team performance.
     *
     * @param teamId The ID of the team
     * @param successRating A rating of how successful the team was (0.0 to 1.0)
     * @return Success status
     */
    @PutMapping("/{teamId}/collaboration-scores")
    public ResponseEntity<String> updateAgentCollaborationScores(
            @PathVariable Long teamId,
            @RequestParam double successRating) {
        logger.info("Received request to update collaboration scores for team ID: {}", teamId);
        teamFormationService.updateAgentCollaborationScores(teamId, successRating);
        return ResponseEntity.ok("Collaboration scores updated successfully");
    }
}
