package ai.lumina.collaboration.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents a negotiation process between agents for task allocation or resource management.
 */
@Entity
@Table(name = "negotiations")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Negotiation {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String type;  // TASK_ALLOCATION, RESOURCE_MANAGEMENT, etc.

    @Column(nullable = false)
    private String status;  // PENDING, IN_PROGRESS, COMPLETED, FAILED

    @ManyToOne
    @JoinColumn(name = "initiator_id")
    private Agent initiator;

    @ManyToMany
    @JoinTable(
        name = "negotiation_participants",
        joinColumns = @JoinColumn(name = "negotiation_id"),
        inverseJoinColumns = @JoinColumn(name = "agent_id")
    )
    private List<Agent> participants = new ArrayList<>();

    @ManyToOne
    @JoinColumn(name = "task_id")
    private Task task;

    @Column(nullable = false)
    private int currentRound;

    @Column(nullable = false)
    private int maxRounds;

    @Column(nullable = true)
    private String outcome;

    @Column(nullable = false)
    private LocalDateTime startedAt;

    @Column(nullable = true)
    private LocalDateTime completedAt;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "negotiation_id")
    private List<NegotiationRound> rounds = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        startedAt = LocalDateTime.now();
        currentRound = 0;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Add a participant to the negotiation.
     * 
     * @param agent The agent to add as participant
     * @return True if the agent was added, false if already a participant
     */
    public boolean addParticipant(Agent agent) {
        if (!participants.contains(agent)) {
            participants.add(agent);
            return true;
        }
        return false;
    }

    /**
     * Start a new negotiation round.
     * 
     * @return The new round if successful, null if max rounds reached or negotiation completed
     */
    public NegotiationRound startNewRound() {
        if (status.equals("COMPLETED") || status.equals("FAILED")) {
            return null;
        }
        
        if (currentRound >= maxRounds) {
            status = "FAILED";
            outcome = "MAX_ROUNDS_REACHED";
            completedAt = LocalDateTime.now();
            return null;
        }
        
        status = "IN_PROGRESS";
        currentRound++;
        
        NegotiationRound round = new NegotiationRound();
        round.setRoundNumber(currentRound);
        round.setStartedAt(LocalDateTime.now());
        round.setStatus("ACTIVE");
        
        rounds.add(round);
        return round;
    }

    /**
     * Complete the current negotiation round.
     * 
     * @param consensus Whether consensus was reached
     * @param result The result of the round
     * @return True if the round was completed, false if no active round
     */
    public boolean completeCurrentRound(boolean consensus, String result) {
        if (rounds.isEmpty() || currentRound == 0) {
            return false;
        }
        
        NegotiationRound currentRound = rounds.get(rounds.size() - 1);
        if (!currentRound.getStatus().equals("ACTIVE")) {
            return false;
        }
        
        currentRound.setStatus(consensus ? "CONSENSUS" : "NO_CONSENSUS");
        currentRound.setResult(result);
        currentRound.setCompletedAt(LocalDateTime.now());
        
        if (consensus) {
            this.status = "COMPLETED";
            this.outcome = result;
            this.completedAt = LocalDateTime.now();
        } else if (this.currentRound >= this.maxRounds) {
            this.status = "FAILED";
            this.outcome = "NO_CONSENSUS";
            this.completedAt = LocalDateTime.now();
        }
        
        return true;
    }

    /**
     * Check if the negotiation is active.
     * 
     * @return True if the negotiation is active, false otherwise
     */
    @Transient
    public boolean isActive() {
        return status.equals("PENDING") || status.equals("IN_PROGRESS");
    }

    /**
     * Check if the negotiation is successful.
     * 
     * @return True if the negotiation is completed successfully, false otherwise
     */
    @Transient
    public boolean isSuccessful() {
        return status.equals("COMPLETED");
    }

    /**
     * Get the duration of the negotiation in seconds.
     * 
     * @return The duration in seconds
     */
    @Transient
    public long getDurationSeconds() {
        LocalDateTime endTime = completedAt != null ? completedAt : LocalDateTime.now();
        return java.time.Duration.between(startedAt, endTime).getSeconds();
    }

    /**
     * Nested entity class representing a round in the negotiation process.
     */
    @Entity
    @Table(name = "negotiation_rounds")
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class NegotiationRound {
        
        @Id
        @GeneratedValue(strategy = GenerationType.UUID)
        private String id;
        
        @Column(nullable = false)
        private int roundNumber;
        
        @Column(nullable = false)
        private String status;  // ACTIVE, CONSENSUS, NO_CONSENSUS
        
        @Column(nullable = true)
        private String result;
        
        @Column(nullable = false)
        private LocalDateTime startedAt;
        
        @Column(nullable = true)
        private LocalDateTime completedAt;
        
        @ElementCollection
        @CollectionTable(name = "negotiation_round_proposals", 
                        joinColumns = @JoinColumn(name = "round_id"))
        private List<Proposal> proposals = new ArrayList<>();
        
        /**
         * Add a proposal to this negotiation round.
         * 
         * @param agentId The ID of the agent making the proposal
         * @param content The content of the proposal
         * @return True if the proposal was added
         */
        public boolean addProposal(String agentId, String content) {
            Proposal proposal = new Proposal();
            proposal.setAgentId(agentId);
            proposal.setContent(content);
            proposal.setTimestamp(LocalDateTime.now());
            return proposals.add(proposal);
        }
    }
    
    /**
     * Embeddable class representing a proposal in a negotiation round.
     */
    @Embeddable
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Proposal {
        
        @Column(nullable = false)
        private String agentId;
        
        @Column(nullable = false, length = 1000)
        private String content;
        
        @Column(nullable = false)
        private LocalDateTime timestamp;
    }
}
