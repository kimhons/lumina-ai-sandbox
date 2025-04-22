package ai.lumina.collaboration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Entity representing a learning event in the collaboration system.
 * Contains information about events that can be used for collaborative learning.
 */
@Entity
@Table(name = "learning_events")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LearningEvent {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "event_id", nullable = false, unique = true)
    private String eventId;

    @Column(name = "event_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private LearningEventType eventType;

    @Column(name = "agent_id", nullable = false)
    private String agentId;

    @Column(name = "content_json", columnDefinition = "json", nullable = false)
    private String contentJson;

    @Column(name = "task_id")
    private String taskId;

    @Column(name = "team_id")
    private String teamId;

    @ElementCollection
    @CollectionTable(name = "learning_event_related_events", 
                    joinColumns = @JoinColumn(name = "event_id"))
    @Column(name = "related_event_id")
    private List<String> relatedEvents = new ArrayList<>();

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "importance")
    private Float importance;

    /**
     * Enum representing the type of learning event.
     */
    public enum LearningEventType {
        OBSERVATION,
        ACTION,
        FEEDBACK,
        INSIGHT,
        ERROR,
        TASK_COMPLETION,
        PATTERN_RECOGNITION
    }
}
