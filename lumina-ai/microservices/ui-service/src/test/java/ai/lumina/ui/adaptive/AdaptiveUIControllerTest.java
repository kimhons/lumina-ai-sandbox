package ai.lumina.ui.adaptive;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import ai.lumina.ui.adaptive.controller.AdaptiveUIController;
import ai.lumina.ui.adaptive.service.AdaptiveUIService;
import ai.lumina.ui.adaptive.model.UIPreferences;
import ai.lumina.ui.adaptive.model.Notification;
import ai.lumina.ui.adaptive.model.CollaborationSession;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;

@WebMvcTest(AdaptiveUIController.class)
public class AdaptiveUIControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AdaptiveUIService adaptiveUIService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    public void testGetUserPreferences() throws Exception {
        String userId = "user-123";
        UIPreferences preferences = new UIPreferences(userId);
        
        when(adaptiveUIService.getUserPreferences(userId)).thenReturn(preferences);

        mockMvc.perform(get("/api/ui/adaptive/preferences/{userId}", userId))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.userId").value(userId))
               .andExpect(jsonPath("$.appearance").exists())
               .andExpect(jsonPath("$.behavior").exists())
               .andExpect(jsonPath("$.accessibility").exists())
               .andExpect(jsonPath("$.notifications").exists())
               .andExpect(jsonPath("$.privacy").exists());
               
        verify(adaptiveUIService).getUserPreferences(userId);
    }

    @Test
    public void testUpdateUserPreferences() throws Exception {
        String userId = "user-123";
        UIPreferences preferences = new UIPreferences(userId);
        Map<String, Object> appearanceUpdate = new HashMap<>();
        appearanceUpdate.put("theme", "dark");
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("category", "appearance");
        requestBody.put("values", appearanceUpdate);
        
        when(adaptiveUIService.updatePreferenceCategory(eq(userId), eq("appearance"), any(Map.class)))
            .thenReturn(preferences);

        mockMvc.perform(put("/api/ui/adaptive/preferences/{userId}", userId)
               .contentType(MediaType.APPLICATION_JSON)
               .content(objectMapper.writeValueAsString(requestBody)))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.userId").value(userId));
               
        verify(adaptiveUIService).updatePreferenceCategory(eq(userId), eq("appearance"), any(Map.class));
    }

    @Test
    public void testGetUserNotifications() throws Exception {
        String userId = "user-123";
        Notification notification = new Notification(userId, "warning", "Test Title", "Test Message");
        
        when(adaptiveUIService.getUserNotifications(userId))
            .thenReturn(Arrays.asList(notification));

        mockMvc.perform(get("/api/ui/adaptive/notifications/{userId}", userId))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$[0].userId").value(userId))
               .andExpect(jsonPath("$[0].type").value("warning"))
               .andExpect(jsonPath("$[0].title").value("Test Title"))
               .andExpect(jsonPath("$[0].message").value("Test Message"));
               
        verify(adaptiveUIService).getUserNotifications(userId);
    }

    @Test
    public void testCreateNotification() throws Exception {
        String userId = "user-123";
        Notification notification = new Notification(userId, "warning", "Test Title", "Test Message");
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("type", "warning");
        requestBody.put("title", "Test Title");
        requestBody.put("message", "Test Message");
        
        when(adaptiveUIService.addNotification(any(Notification.class)))
            .thenReturn(notification);

        mockMvc.perform(post("/api/ui/adaptive/notifications/{userId}", userId)
               .contentType(MediaType.APPLICATION_JSON)
               .content(objectMapper.writeValueAsString(requestBody)))
               .andExpect(status().isCreated())
               .andExpect(jsonPath("$.userId").value(userId))
               .andExpect(jsonPath("$.type").value("warning"))
               .andExpect(jsonPath("$.title").value("Test Title"))
               .andExpect(jsonPath("$.message").value("Test Message"));
               
        verify(adaptiveUIService).addNotification(any(Notification.class));
    }

    @Test
    public void testCreateChatTerminationWarning() throws Exception {
        String userId = "user-123";
        String sessionId = "session-456";
        int timeRemaining = 30;
        
        Notification notification = Notification.createChatTerminationWarning(userId, sessionId, timeRemaining);
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("sessionId", sessionId);
        requestBody.put("timeRemaining", timeRemaining);
        
        when(adaptiveUIService.createChatTerminationWarning(userId, sessionId, timeRemaining))
            .thenReturn(notification);

        mockMvc.perform(post("/api/ui/adaptive/notifications/{userId}/chat-termination", userId)
               .contentType(MediaType.APPLICATION_JSON)
               .content(objectMapper.writeValueAsString(requestBody)))
               .andExpect(status().isCreated())
               .andExpect(jsonPath("$.userId").value(userId))
               .andExpect(jsonPath("$.type").value("warning"))
               .andExpect(jsonPath("$.title").value("Chat Session Ending Soon"))
               .andExpect(jsonPath("$.sessionId").value(sessionId));
               
        verify(adaptiveUIService).createChatTerminationWarning(userId, sessionId, timeRemaining);
    }

    @Test
    public void testCreateCollaborationSession() throws Exception {
        String userId = "user-123";
        String userName = "John Doe";
        String agentId = "agent-456";
        String agentName = "Lumina AI";
        
        CollaborationSession session = CollaborationSession.createCaptchaBypassSession(
            userId, userName, agentId, agentName);
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("userName", userName);
        requestBody.put("agentId", agentId);
        requestBody.put("agentName", agentName);
        requestBody.put("type", "captcha-bypass");
        
        when(adaptiveUIService.createCaptchaBypassSession(userId, userName, agentId, agentName))
            .thenReturn(session);

        mockMvc.perform(post("/api/ui/adaptive/collaboration/sessions/{userId}", userId)
               .contentType(MediaType.APPLICATION_JSON)
               .content(objectMapper.writeValueAsString(requestBody)))
               .andExpect(status().isCreated())
               .andExpect(jsonPath("$.title").value("CAPTCHA Assistance"))
               .andExpect(jsonPath("$.type").value("captcha-bypass"))
               .andExpect(jsonPath("$.participants[0].id").value(userId))
               .andExpect(jsonPath("$.participants[0].name").value(userName))
               .andExpect(jsonPath("$.participants[1].id").value(agentId))
               .andExpect(jsonPath("$.participants[1].name").value(agentName));
               
        verify(adaptiveUIService).createCaptchaBypassSession(userId, userName, agentId, agentName);
    }
}
