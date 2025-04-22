package ai.lumina.streaming.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Value("${openai.api.url:https://api.openai.com}")
    private String openaiApiUrl;
    
    @Value("${openai.api.key:}")
    private String openaiApiKey;
    
    @Value("${claude.api.url:https://api.anthropic.com}")
    private String claudeApiUrl;
    
    @Value("${claude.api.key:}")
    private String claudeApiKey;
    
    @Value("${gemini.api.url:https://generativelanguage.googleapis.com}")
    private String geminiApiUrl;
    
    @Value("${gemini.api.key:}")
    private String geminiApiKey;

    @Bean(name = "openaiWebClient")
    public WebClient openaiWebClient() {
        return WebClient.builder()
                .baseUrl(openaiApiUrl)
                .defaultHeader("Authorization", "Bearer " + openaiApiKey)
                .defaultHeader("Content-Type", "application/json")
                .build();
    }
    
    @Bean(name = "claudeWebClient")
    public WebClient claudeWebClient() {
        return WebClient.builder()
                .baseUrl(claudeApiUrl)
                .defaultHeader("x-api-key", claudeApiKey)
                .defaultHeader("anthropic-version", "2023-06-01")
                .defaultHeader("Content-Type", "application/json")
                .build();
    }
    
    @Bean(name = "geminiWebClient")
    public WebClient geminiWebClient() {
        return WebClient.builder()
                .baseUrl(geminiApiUrl)
                .defaultHeader("x-goog-api-key", geminiApiKey)
                .defaultHeader("Content-Type", "application/json")
                .build();
    }
}
