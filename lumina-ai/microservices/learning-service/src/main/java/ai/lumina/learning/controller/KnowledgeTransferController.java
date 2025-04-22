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

import ai.lumina.learning.integration.KnowledgeTransferIntegrationService;
import ai.lumina.learning.model.KnowledgeItem;
import lombok.extern.slf4j.Slf4j;

/**
 * Controller for knowledge transfer operations.
 * Provides endpoints for transferring knowledge between agents and teams.
 */
@RestController
@RequestMapping("/api/v1/knowledge")
@Slf4j
public class KnowledgeTransferController {

    @Autowired
    private KnowledgeTransferIntegrationService knowledgeTransferService;
    
    /**
     * Transfer knowledge between agents.
     * 
     * @param request Transfer request containing knowledge ID, source agent, target agent, and permissions
     * @return Result of the transfer operation
     */
    @PostMapping("/transfer")
    public ResponseEntity<Map<String, Object>> transferKnowledge(@RequestBody Map<String, Object> request) {
        log.info("Received knowledge transfer request: {}", request);
        
        String knowledgeId = (String) request.get("knowledge_id");
        String sourceAgentId = (String) request.get("source_agent");
        String targetAgentId = (String) request.get("target_agent");
        
        @SuppressWarnings("unchecked")
        Map<String, List<String>> permissions = (Map<String, List<String>>) request.get("permissions");
        
        Map<String, Object> result = knowledgeTransferService.transferKnowledgeBetweenAgents(
                knowledgeId, sourceAgentId, targetAgentId, permissions);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Broadcast knowledge to a team.
     * 
     * @param request Broadcast request containing knowledge ID, source agent, team ID, and permissions
     * @return Result of the broadcast operation
     */
    @PostMapping("/broadcast")
    public ResponseEntity<Map<String, Object>> broadcastKnowledge(@RequestBody Map<String, Object> request) {
        log.info("Received knowledge broadcast request: {}", request);
        
        String knowledgeId = (String) request.get("knowledge_id");
        String sourceAgentId = (String) request.get("source_agent");
        String teamId = (String) request.get("team_id");
        
        @SuppressWarnings("unchecked")
        Map<String, List<String>> permissions = (Map<String, List<String>>) request.get("permissions");
        
        Map<String, Object> result = knowledgeTransferService.broadcastKnowledgeToTeam(
                knowledgeId, sourceAgentId, teamId, permissions);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Query an agent's knowledge.
     * 
     * @param agentId ID of the agent
     * @param request Query parameters
     * @return Result of the query operation
     */
    @PostMapping("/query/{agentId}")
    public ResponseEntity<Map<String, Object>> queryKnowledge(
            @PathVariable String agentId,
            @RequestBody Map<String, Object> request) {
        
        log.info("Received knowledge query request for agent {}: {}", agentId, request);
        
        Map<String, Object> result = knowledgeTransferService.queryAgentKnowledge(agentId, request);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Create a new knowledge item.
     * 
     * @param request Knowledge item creation request
     * @return The created knowledge item
     */
    @PostMapping
    public ResponseEntity<KnowledgeItem> createKnowledgeItem(@RequestBody Map<String, Object> request) {
        log.info("Received knowledge item creation request: {}", request);
        
        KnowledgeItem.KnowledgeType type = KnowledgeItem.KnowledgeType.valueOf((String) request.get("type"));
        String name = (String) request.get("name");
        String description = (String) request.get("description");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> content = (Map<String, Object>) request.get("content");
        
        String sourceAgentId = (String) request.get("source_agent");
        
        @SuppressWarnings("unchecked")
        Map<String, Object> metadata = (Map<String, Object>) request.get("metadata");
        
        KnowledgeItem knowledgeItem = knowledgeTransferService.createKnowledgeItem(
                type, name, description, content, sourceAgentId, metadata);
        
        return ResponseEntity.ok(knowledgeItem);
    }
}
