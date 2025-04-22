package ai.lumina.collaboration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Entity representing a team of agents in the collaboration system.
 * Contains information about team members, roles, and associated task.
 */
@Entity
@Table(name = "agent_teams")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AgentTeam {

    @Id
    @Column(name = "team_id", nullable = false)
    private String teamId;

    @Column(name = "name")
    private String name;

    @Column(name = "task_id", nullable = false)
    private String taskId;

    @Column(name = "formation_strategy")
    private String formationStrategy;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    /**
     * Set of agent IDs that are members of this team
     */
    @ElementCollection
    @CollectionTable(name = "team_members", 
                    joinColumns = @JoinColumn(name = "team_id"))
    @Column(name = "agent_id")
    private Set<String> members = new HashSet<>();

    /**
     * Map of agent IDs to their roles in the team
     * Each agent can have multiple roles, each with a capability level
     */
    @ElementCollection
    @CollectionTable(name = "team_roles", 
                    joinColumns = @JoinColumn(name = "team_id"))
    @MapKeyJoinColumn(name = "agent_id")
    @Column(name = "roles_json", columnDefinition = "json")
    private Map<String, Map<String, Float>> roles = new HashMap<>();

    @Column(name = "status")
    @Enumerated(EnumType.STRING)
    private TeamStatus status;

    @Column(name = "performance_score")
    private Float performanceScore;

    @Column(name = "leader_id")
    private String leaderId;

    /**
     * Enum representing the status of a team.
     */
    public enum TeamStatus {
        FORMING,
        ACTIVE,
        DISBANDED
    }
}
