package ai.lumina.memory.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

/**
 * Async configuration for the Memory Service.
 */
@Configuration
@EnableScheduling
public class AsyncConfig {

    /**
     * Configure the async executor for memory operations.
     *
     * @return Executor for async operations
     */
    @Bean(name = "memoryTaskExecutor")
    public Executor memoryTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(4);
        executor.setMaxPoolSize(8);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("memory-");
        executor.initialize();
        return executor;
    }
}
