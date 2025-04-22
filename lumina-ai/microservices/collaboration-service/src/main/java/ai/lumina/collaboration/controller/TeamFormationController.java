package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.Agent;
import ai.lumina.collaboration.model.Task;
import ai.lumina.collaboration.model.Team;
import ai.lumina.collaboration.service.TeamFormationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Set;

/**
 * REST controller for team formation operations.
 */
@RestController
@RequestMapping("/api/v1/teams")
public class TeamFormationController {

    private static final Logger logger = LoggerFactory.getLogger(TeamFormationController.class);

    private final TeamFormationService teamFormationService;

    @Autowired
    public TeamFormationController(TeamFormationService teamFormationService) {
        this.teamFormationService = teamFormationService;
    }

    /**
     * Form a team for a task using the specified strategy.
     *
     * @param task The task requiring a team
     * @param strategy The team formation strategy to use (capability or diversity)
     * @return The formed team
     */
    @PostMapping("/form")
    public ResponseEntity<Team> formTeam(@RequestBody Task task, 
                                        @RequestParam(defaultValue = "capability") String strategy) {
        logger.info("Received request to form team for task {} using strategy {}", 
                   task.getId(), strategy);
        
        try {
            Team team = teamFormationService.formTeam(task, strategy);
            return ResponseEntity.ok(team);
        } catch (Exception e) {
            logger.error("Error forming team: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get all teams.
     *
     * @return List of all teams
     */
    @GetMapping
    public ResponseEntity<List<Team>> getAllTeams() {
        try {
            List<Team> teams = teamFormationService.getAllTeams();
            return ResponseEntity.ok(teams);
        } catch (Exception e) {
            logger.error("Error retrieving teams: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get a team by ID.
     *
     * @param teamId The team ID
     * @return The team, or 404 if not found
     */
    @GetMapping("/{teamId}")
    public ResponseEntity<Team> getTeamById(@PathVariable String teamId) {
        try {
            Team team = teamFormationService.getTeamById(teamId);
            if (team != null) {
                return ResponseEntity.ok(team);
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            logger.error("Error retrieving team {}: {}", teamId, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Disband a team.
     *
     * @param teamId The ID of the team to disband
     * @return 200 OK if successful, 404 if team not found
     */
    @PostMapping("/{teamId}/disband")
    public ResponseEntity<Void> disbandTeam(@PathVariable String teamId) {
        try {
            boolean success = teamFormationService.disbandTeam(teamId);
            if (success) {
                return ResponseEntity.ok().build();
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            logger.error("Error disbanding team {}: {}", teamId, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Find suitable teams for a task based on required capabilities.
     *
     * @param requiredCapabilities The set of required capabilities
     * @return List of suitable teams, sorted by performance rating
     */
    @PostMapping("/find-suitable")
    public ResponseEntity<List<Team>> findSuitableTeams(@RequestBody Set<String> requiredCapabilities) {
        try {
            List<Team> suitableTeams = teamFormationService.findSuitableTeamsForTask(requiredCapabilities);
            return ResponseEntity.ok(suitableTeams);
        } catch (Exception e) {
            logger.error("Error finding suitable teams: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
