package ai.lumina.monitoring.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.boot.web.servlet.FilterRegistrationBean;

import ai.lumina.monitoring.filter.RequestLoggingFilter;

/**
 * Configuration for registering servlet filters.
 */
@Configuration
public class FilterConfig {

    /**
     * Registers the request logging filter.
     *
     * @param requestLoggingFilter The request logging filter
     * @return The filter registration bean
     */
    @Bean
    public FilterRegistrationBean<RequestLoggingFilter> loggingFilterRegistration(RequestLoggingFilter requestLoggingFilter) {
        FilterRegistrationBean<RequestLoggingFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(requestLoggingFilter);
        registration.addUrlPatterns("/*");
        registration.setName("requestLoggingFilter");
        registration.setOrder(1);
        return registration;
    }
}
