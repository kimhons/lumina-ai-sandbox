package ai.lumina.ui.adaptive.model;

import java.util.Date;
import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.io.Serializable;

/**
 * Model class representing a collaboration session in the Adaptive UI system.
 * Used for real-time collaboration between users and AI agents.
 */
public class CollaborationSession implements Serializable {
    private String id;
    private String title;
    private String type;
    private List<Participant> participants;
    private Date createdAt;
    private Date lastActivity;
    private String status;
    private String taskDescription;
    private List<CollaborationAction> actions;

    public CollaborationSession() {
        this.id = UUID.randomUUID().toString();
        this.createdAt = new Date();
        this.lastActivity = new Date();
        this.status = "active";
        this.participants = new ArrayList<>();
        this.actions = new ArrayList<>();
    }

    public CollaborationSession(String title, String type) {
        this();
        this.title = title;
        this.type = type;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public List<Participant> getParticipants() {
        return participants;
    }

    public void setParticipants(List<Participant> participants) {
        this.participants = participants;
    }

    public void addParticipant(Participant participant) {
        this.participants.add(participant);
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }

    public Date getLastActivity() {
        return lastActivity;
    }

    public void setLastActivity(Date lastActivity) {
        this.lastActivity = lastActivity;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getTaskDescription() {
        return taskDescription;
    }

    public void setTaskDescription(String taskDescription) {
        this.taskDescription = taskDescription;
    }

    public List<CollaborationAction> getActions() {
        return actions;
    }

    public void setActions(List<CollaborationAction> actions) {
        this.actions = actions;
    }

    public void addAction(CollaborationAction action) {
        this.actions.add(action);
        this.lastActivity = new Date();
    }

    /**
     * Create a CAPTCHA bypass collaboration session
     * @param userId The user ID
     * @param userName The user name
     * @param agentId The agent ID
     * @param agentName The agent name
     * @return A new collaboration session
     */
    public static CollaborationSession createCaptchaBypassSession(String userId, String userName, String agentId, String agentName) {
        CollaborationSession session = new CollaborationSession();
        session.setTitle("CAPTCHA Assistance");
        session.setType("captcha-bypass");
        session.setTaskDescription("Collaborate with the AI agent to solve CAPTCHA challenges");
        
        // Add user participant
        Participant user = new Participant();
        user.setId(userId);
        user.setName(userName);
        user.setRole("user");
        session.addParticipant(user);
        
        // Add agent participant
        Participant agent = new Participant();
        agent.setId(agentId);
        agent.setName(agentName);
        agent.setRole("agent");
        session.addParticipant(agent);
        
        return session;
    }

    /**
     * Participant in a collaboration session
     */
    public static class Participant implements Serializable {
        private String id;
        private String name;
        private String role;
        private Date joinedAt;
        private String status;

        public Participant() {
            this.joinedAt = new Date();
            this.status = "active";
        }

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getRole() {
            return role;
        }

        public void setRole(String role) {
            this.role = role;
        }

        public Date getJoinedAt() {
            return joinedAt;
        }

        public void setJoinedAt(Date joinedAt) {
            this.joinedAt = joinedAt;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }
    }

    /**
     * Action performed in a collaboration session
     */
    public static class CollaborationAction implements Serializable {
        private String id;
        private String participantId;
        private String type;
        private String content;
        private Date timestamp;
        private String status;

        public CollaborationAction() {
            this.id = UUID.randomUUID().toString();
            this.timestamp = new Date();
            this.status = "completed";
        }

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getParticipantId() {
            return participantId;
        }

        public void setParticipantId(String participantId) {
            this.participantId = participantId;
        }

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }

        public String getContent() {
            return content;
        }

        public void setContent(String content) {
            this.content = content;
        }

        public Date getTimestamp() {
            return timestamp;
        }

        public void setTimestamp(Date timestamp) {
            this.timestamp = timestamp;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }
    }
}
