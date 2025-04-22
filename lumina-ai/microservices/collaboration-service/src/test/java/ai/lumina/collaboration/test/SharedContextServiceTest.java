package ai.lumina.collaboration.test;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.boot.test.context.SpringBootTest;

import ai.lumina.collaboration.model.ContextAccess;
import ai.lumina.collaboration.model.ContextChange;
import ai.lumina.collaboration.model.ContextVersion;
import ai.lumina.collaboration.model.SharedContext;
import ai.lumina.collaboration.repository.ContextAccessRepository;
import ai.lumina.collaboration.repository.ContextVersionRepository;
import ai.lumina.collaboration.repository.SharedContextRepository;
import ai.lumina.collaboration.service.MemoryIntegrationService;
import ai.lumina.collaboration.service.SharedContextService;

/**
 * Unit tests for the SharedContextService.
 */
@SpringBootTest
public class SharedContextServiceTest {

    @Mock
    private SharedContextRepository contextRepository;

    @Mock
    private ContextVersionRepository versionRepository;

    @Mock
    private ContextAccessRepository accessRepository;

    @Mock
    private MemoryIntegrationService memoryService;

    @InjectMocks
    private SharedContextService contextService;

    private String ownerId;
    private String agentId;
    private String contextId;
    private String versionId;

    @BeforeEach
    public void setup() {
        MockitoAnnotations.openMocks(this);
        
        ownerId = "owner-" + UUID.randomUUID().toString();
        agentId = "agent-" + UUID.randomUUID().toString();
        contextId = "context-" + UUID.randomUUID().toString();
        versionId = "version-" + UUID.randomUUID().toString();
        
        // Set memory integration to false for tests
        setField(contextService, "memoryIntegrationEnabled", false);
    }

    @Test
    public void testCreateContext() {
        // Prepare test data
        String name = "Test Context";
        String contextType = "TASK";
        Map<String, Object> initialContent = new HashMap<>();
        initialContent.put("key", "value");
        
        // Mock repository behavior
        when(contextRepository.save(any(SharedContext.class))).thenAnswer(invocation -> {
            SharedContext savedContext = invocation.getArgument(0);
            savedContext.setId(contextId);
            return savedContext;
        });
        
        when(versionRepository.save(any(ContextVersion.class))).thenAnswer(invocation -> {
            return invocation.getArgument(0);
        });
        
        // Call the service method
        SharedContext result = contextService.createContext(
                name, contextType, ownerId, initialContent, null);
        
        // Verify the result
        assertNotNull(result);
        assertEquals(name, result.getName());
        assertEquals(contextType, result.getContextType());
        assertEquals(ownerId, result.getOwnerId());
        assertEquals(initialContent, result.getContent());
        assertNotNull(result.getCurrentVersionId());
        assertTrue(result.getSubscribers().contains(ownerId));
        
        // Verify repository calls
        verify(contextRepository).save(any(SharedContext.class));
        verify(versionRepository).save(any(ContextVersion.class));
    }

    @Test
    public void testGetContext() {
        // Prepare test data
        SharedContext context = createTestContext();
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(context));
        
        // Call the service method
        SharedContext result = contextService.getContext(contextId, ownerId);
        
        // Verify the result
        assertNotNull(result);
        assertEquals(contextId, result.getId());
        assertEquals(ownerId, result.getOwnerId());
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
    }

    @Test
    public void testGetContextWithAccessControl() {
        // Prepare test data
        SharedContext context = createTestContext();
        ContextAccess access = new ContextAccess();
        access.setAgentId(agentId);
        access.setAccessLevel("READ_ONLY");
        access.setGrantedAt(LocalDateTime.now());
        access.setGrantedBy(ownerId);
        access.setContext(context);
        context.getAccessControl().add(access);
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(context));
        
        // Call the service method
        SharedContext result = contextService.getContext(contextId, agentId);
        
        // Verify the result
        assertNotNull(result);
        assertEquals(contextId, result.getId());
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
    }

    @Test
    public void testUpdateContext() {
        // Prepare test data
        SharedContext context = createTestContext();
        Map<String, Object> updates = new HashMap<>();
        updates.put("newKey", "newValue");
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(context));
        when(contextRepository.save(any(SharedContext.class))).thenReturn(context);
        when(versionRepository.save(any(ContextVersion.class))).thenAnswer(invocation -> {
            return invocation.getArgument(0);
        });
        
        // Call the service method
        SharedContext result = contextService.updateContext(
                contextId, ownerId, updates, null);
        
        // Verify the result
        assertNotNull(result);
        assertEquals("newValue", result.getContent().get("newKey"));
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
        verify(contextRepository).save(any(SharedContext.class));
        verify(versionRepository).save(any(ContextVersion.class));
    }

    @Test
    public void testMergeContexts() {
        // Prepare test data
        SharedContext targetContext = createTestContext();
        
        SharedContext sourceContext = new SharedContext();
        sourceContext.setId("source-" + UUID.randomUUID().toString());
        sourceContext.setName("Source Context");
        sourceContext.setContextType("TASK");
        sourceContext.setOwnerId(ownerId);
        sourceContext.setCreatedAt(LocalDateTime.now());
        sourceContext.setUpdatedAt(LocalDateTime.now());
        Map<String, Object> sourceContent = new HashMap<>();
        sourceContent.put("sourceKey", "sourceValue");
        sourceContext.setContent(sourceContent);
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(targetContext));
        when(contextRepository.findById(sourceContext.getId())).thenReturn(Optional.of(sourceContext));
        when(contextRepository.save(any(SharedContext.class))).thenReturn(targetContext);
        when(versionRepository.save(any(ContextVersion.class))).thenAnswer(invocation -> {
            return invocation.getArgument(0);
        });
        
        // Call the service method
        SharedContext result = contextService.mergeContexts(
                contextId, sourceContext.getId(), ownerId, "latest");
        
        // Verify the result
        assertNotNull(result);
        assertEquals("sourceValue", result.getContent().get("sourceKey"));
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
        verify(contextRepository).findById(sourceContext.getId());
        verify(contextRepository).save(any(SharedContext.class));
        verify(versionRepository).save(any(ContextVersion.class));
    }

    @Test
    public void testForkContext() {
        // Prepare test data
        SharedContext sourceContext = createTestContext();
        String newName = "Forked Context";
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(sourceContext));
        when(contextRepository.save(any(SharedContext.class))).thenAnswer(invocation -> {
            SharedContext savedContext = invocation.getArgument(0);
            savedContext.setId("forked-" + UUID.randomUUID().toString());
            return savedContext;
        });
        when(versionRepository.save(any(ContextVersion.class))).thenAnswer(invocation -> {
            return invocation.getArgument(0);
        });
        
        // Call the service method
        SharedContext result = contextService.forkContext(contextId, agentId, newName);
        
        // Verify the result
        assertNotNull(result);
        assertEquals(newName, result.getName());
        assertEquals(agentId, result.getOwnerId());
        assertEquals(sourceContext.getContextType(), result.getContextType());
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
        verify(contextRepository, times(2)).save(any(SharedContext.class));
        verify(versionRepository).save(any(ContextVersion.class));
    }

    @Test
    public void testGrantAccess() {
        // Prepare test data
        SharedContext context = createTestContext();
        String accessLevel = "READ_WRITE";
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(context));
        when(contextRepository.save(any(SharedContext.class))).thenReturn(context);
        when(accessRepository.save(any(ContextAccess.class))).thenAnswer(invocation -> {
            return invocation.getArgument(0);
        });
        
        // Call the service method
        boolean result = contextService.grantAccess(
                contextId, ownerId, agentId, accessLevel, null);
        
        // Verify the result
        assertTrue(result);
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
        verify(contextRepository).save(any(SharedContext.class));
        verify(accessRepository).save(any(ContextAccess.class));
    }

    @Test
    public void testRevokeAccess() {
        // Prepare test data
        SharedContext context = createTestContext();
        ContextAccess access = new ContextAccess();
        access.setAgentId(agentId);
        access.setAccessLevel("READ_WRITE");
        access.setGrantedAt(LocalDateTime.now());
        access.setGrantedBy(ownerId);
        access.setContext(context);
        context.getAccessControl().add(access);
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(context));
        when(contextRepository.save(any(SharedContext.class))).thenReturn(context);
        
        // Call the service method
        boolean result = contextService.revokeAccess(contextId, ownerId, agentId);
        
        // Verify the result
        assertTrue(result);
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
        verify(contextRepository).save(any(SharedContext.class));
        verify(accessRepository).delete(any(ContextAccess.class));
    }

    @Test
    public void testSubscribe() {
        // Prepare test data
        SharedContext context = createTestContext();
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(context));
        when(contextRepository.save(any(SharedContext.class))).thenReturn(context);
        
        // Call the service method
        boolean result = contextService.subscribe(contextId, agentId);
        
        // Verify the result
        assertTrue(result);
        assertTrue(context.getSubscribers().contains(agentId));
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
        verify(contextRepository).save(any(SharedContext.class));
    }

    @Test
    public void testUnsubscribe() {
        // Prepare test data
        SharedContext context = createTestContext();
        context.getSubscribers().add(agentId);
        
        // Mock repository behavior
        when(contextRepository.findById(contextId)).thenReturn(Optional.of(context));
        when(contextRepository.save(any(SharedContext.class))).thenReturn(context);
        
        // Call the service method
        boolean result = contextService.unsubscribe(contextId, agentId);
        
        // Verify the result
        assertTrue(result);
        assertFalse(context.getSubscribers().contains(agentId));
        
        // Verify repository calls
        verify(contextRepository).findById(contextId);
        verify(contextRepository).save(any(SharedContext.class));
    }

    @Test
    public void testSearchContexts() {
        // Prepare test data
        SharedContext context = createTestContext();
        
        // Mock repository behavior
        when(contextRepository.findByNameContainingIgnoreCase(anyString()))
            .thenReturn(Collections.singletonList(context));
        
        // Call the service method
        java.util.List<SharedContext> results = contextService.searchContexts("Test", null, null);
        
        // Verify the result
        assertNotNull(results);
        assertEquals(1, results.size());
        assertEquals(contextId, results.get(0).getId());
        
        // Verify repository calls
        verify(contextRepository).findByNameContainingIgnoreCase(anyString());
    }

    /**
     * Helper method to create a test context.
     */
    private SharedContext createTestContext() {
        SharedContext context = new SharedContext();
        context.setId(contextId);
        context.setName("Test Context");
        context.setContextType("TASK");
        context.setOwnerId(ownerId);
        context.setCreatedAt(LocalDateTime.now());
        context.setUpdatedAt(LocalDateTime.now());
        context.setCurrentVersionId(versionId);
        context.getSubscribers().add(ownerId);
        
        Map<String, Object> content = new HashMap<>();
        content.put("key", "value");
        context.setContent(content);
        
        return context;
    }

    /**
     * Helper method to set a private field using reflection.
     */
    private void setField(Object target, String fieldName, Object value) {
        try {
            java.lang.reflect.Field field = target.getClass().getDeclaredField(fieldName);
            field.setAccessible(true);
            field.set(target, value);
        } catch (Exception e) {
            throw new RuntimeException("Failed to set field: " + fieldName, e);
        }
    }
}
