package ai.lumina.learning.integration;

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

import ai.lumina.learning.model.KnowledgeItem;
import ai.lumina.learning.repository.KnowledgeItemRepository;
import lombok.extern.slf4j.Slf4j;

/**
 * Service for integrating knowledge transfer capabilities with the collaboration system.
 * This service enables knowledge sharing between agents and teams.
 */
@Service
@Slf4j
public class KnowledgeTransferIntegrationService {

    @Autowired
    private RestTemplate restTemplate;
    
    @Autowired
    private KnowledgeItemRepository knowledgeItemRepository;
    
    @Value("${lumina.collaboration.api.url}")
    private String collaborationApiUrl;
    
    /**
     * Transfer knowledge between agents.
     * 
     * @param knowledgeId ID of the knowledge to transfer
     * @param sourceAgentId ID of the source agent
     * @param targetAgentId ID of the target agent
     * @param permissions Permissions for the transferred knowledge
     * @return Result of the transfer operation
     */
    public Map<String, Object> transferKnowledgeBetweenAgents(
            String knowledgeId,
            String sourceAgentId,
            String targetAgentId,
            Map<String, List<String>> permissions) {
        
        try {
            log.info("Transferring knowledge {} from agent {} to agent {}", 
                    knowledgeId, sourceAgentId, targetAgentId);
            
            // Retrieve knowledge item
            KnowledgeItem knowledgeItem = knowledgeItemRepository.findById(knowledgeId)
                    .orElseThrow(() -> new RuntimeException("Knowledge item not found: " + knowledgeId));
            
            // Prepare transfer request
            Map<String, Object> transferRequest = new HashMap<>();
            transferRequest.put("knowledge_id", knowledgeId);
            transferRequest.put("source_agent", sourceAgentId);
            transferRequest.put("target_agent", targetAgentId);
            transferRequest.put("permissions", permissions);
            transferRequest.put("knowledge_type", knowledgeItem.getType().toString());
            transferRequest.put("knowledge_content", knowledgeItem.getContent());
            transferRequest.put("metadata", knowledgeItem.getMetadata());
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create HTTP entity
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(transferRequest, headers);
            
            // Call collaboration API
            ResponseEntity<Map> response = restTemplate.exchange(
                    collaborationApiUrl + "/knowledge/transfer",
                    HttpMethod.POST,
                    entity,
                    Map.class);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> result = response.getBody();
            
            log.info("Knowledge transfer completed: {}", result);
            
            return result;
            
        } catch (Exception e) {
            log.error("Error transferring knowledge between agents", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("message", e.getMessage());
            errorResult.put("knowledge_id", knowledgeId);
            errorResult.put("source_agent", sourceAgentId);
            errorResult.put("target_agent", targetAgentId);
            
            return errorResult;
        }
    }
    
    /**
     * Broadcast knowledge to a team.
     * 
     * @param knowledgeId ID of the knowledge to broadcast
     * @param sourceAgentId ID of the source agent
     * @param teamId ID of the target team
     * @param permissions Permissions for the broadcasted knowledge
     * @return Result of the broadcast operation
     */
    public Map<String, Object> broadcastKnowledgeToTeam(
            String knowledgeId,
            String sourceAgentId,
            String teamId,
            Map<String, List<String>> permissions) {
        
        try {
            log.info("Broadcasting knowledge {} from agent {} to team {}", 
                    knowledgeId, sourceAgentId, teamId);
            
            // Retrieve knowledge item
            KnowledgeItem knowledgeItem = knowledgeItemRepository.findById(knowledgeId)
                    .orElseThrow(() -> new RuntimeException("Knowledge item not found: " + knowledgeId));
            
            // Prepare broadcast request
            Map<String, Object> broadcastRequest = new HashMap<>();
            broadcastRequest.put("knowledge_id", knowledgeId);
            broadcastRequest.put("source_agent", sourceAgentId);
            broadcastRequest.put("team_id", teamId);
            broadcastRequest.put("permissions", permissions);
            broadcastRequest.put("knowledge_type", knowledgeItem.getType().toString());
            broadcastRequest.put("knowledge_content", knowledgeItem.getContent());
            broadcastRequest.put("metadata", knowledgeItem.getMetadata());
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create HTTP entity
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(broadcastRequest, headers);
            
            // Call collaboration API
            ResponseEntity<Map> response = restTemplate.exchange(
                    collaborationApiUrl + "/knowledge/broadcast",
                    HttpMethod.POST,
                    entity,
                    Map.class);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> result = response.getBody();
            
            log.info("Knowledge broadcast completed: {}", result);
            
            return result;
            
        } catch (Exception e) {
            log.error("Error broadcasting knowledge to team", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("message", e.getMessage());
            errorResult.put("knowledge_id", knowledgeId);
            errorResult.put("source_agent", sourceAgentId);
            errorResult.put("team_id", teamId);
            
            return errorResult;
        }
    }
    
    /**
     * Query an agent's knowledge.
     * 
     * @param agentId ID of the agent
     * @param queryParams Query parameters
     * @return Result of the query operation
     */
    public Map<String, Object> queryAgentKnowledge(
            String agentId,
            Map<String, Object> queryParams) {
        
        try {
            log.info("Querying knowledge for agent {}", agentId);
            
            // Prepare query request
            Map<String, Object> queryRequest = new HashMap<>();
            queryRequest.put("agent_id", agentId);
            queryRequest.put("query_params", queryParams);
            
            // Set up headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Create HTTP entity
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(queryRequest, headers);
            
            // Call collaboration API
            ResponseEntity<Map> response = restTemplate.exchange(
                    collaborationApiUrl + "/knowledge/query",
                    HttpMethod.POST,
                    entity,
                    Map.class);
            
            @SuppressWarnings("unchecked")
            Map<String, Object> result = response.getBody();
            
            log.info("Knowledge query completed: {}", result);
            
            return result;
            
        } catch (Exception e) {
            log.error("Error querying agent knowledge", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("status", "error");
            errorResult.put("message", e.getMessage());
            errorResult.put("agent_id", agentId);
            
            return errorResult;
        }
    }
    
    /**
     * Create a new knowledge item.
     * 
     * @param type Type of knowledge
     * @param name Name of the knowledge item
     * @param description Description of the knowledge item
     * @param content Content of the knowledge item
     * @param sourceAgentId ID of the source agent
     * @param metadata Metadata for the knowledge item
     * @return The created knowledge item
     */
    public KnowledgeItem createKnowledgeItem(
            KnowledgeItem.KnowledgeType type,
            String name,
            String description,
            Map<String, Object> content,
            String sourceAgentId,
            Map<String, Object> metadata) {
        
        try {
            log.info("Creating knowledge item: {}", name);
            
            // Create new knowledge item
            KnowledgeItem knowledgeItem = KnowledgeItem.createNew();
            knowledgeItem.setType(type);
            knowledgeItem.setName(name);
            knowledgeItem.setDescription(description);
            knowledgeItem.setContent(content);
            knowledgeItem.setSourceAgentId(sourceAgentId);
            knowledgeItem.setMetadata(metadata);
            knowledgeItem.setStatus(KnowledgeItem.KnowledgeStatus.VALIDATED);
            knowledgeItem.setConfidenceScore(1.0);
            
            // Save knowledge item
            knowledgeItem = knowledgeItemRepository.save(knowledgeItem);
            
            log.info("Knowledge item created: {}", knowledgeItem.getId());
            
            return knowledgeItem;
            
        } catch (Exception e) {
            log.error("Error creating knowledge item", e);
            throw new RuntimeException("Error creating knowledge item: " + e.getMessage(), e);
        }
    }
}
