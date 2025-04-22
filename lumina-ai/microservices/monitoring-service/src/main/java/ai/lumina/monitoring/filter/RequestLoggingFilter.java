package ai.lumina.monitoring.filter;

import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.UUID;

/**
 * Filter for logging HTTP requests and responses.
 * This filter adds request IDs to each request for traceability and logs request/response details.
 */
@Component
@Slf4j
public class RequestLoggingFilter extends OncePerRequestFilter {

    private static final String REQUEST_ID = "requestId";
    private static final String START_TIME = "startTime";

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        
        // Generate request ID and store in MDC for logging
        String requestId = UUID.randomUUID().toString();
        MDC.put(REQUEST_ID, requestId);
        
        // Store start time for performance measurement
        long startTime = System.currentTimeMillis();
        MDC.put(START_TIME, String.valueOf(startTime));
        
        // Wrap request and response to allow reading the body multiple times
        ContentCachingRequestWrapper requestWrapper = new ContentCachingRequestWrapper(request);
        ContentCachingResponseWrapper responseWrapper = new ContentCachingResponseWrapper(response);
        
        // Add request ID to response headers for client-side tracing
        responseWrapper.setHeader("X-Request-ID", requestId);
        
        try {
            // Log request details
            logRequest(requestWrapper);
            
            // Continue with the filter chain
            filterChain.doFilter(requestWrapper, responseWrapper);
            
            // Log response details
            logResponse(responseWrapper, startTime);
        } finally {
            // Copy content to the original response
            responseWrapper.copyBodyToResponse();
            
            // Clean up MDC
            MDC.remove(REQUEST_ID);
            MDC.remove(START_TIME);
        }
    }

    /**
     * Log request details.
     *
     * @param request The HTTP request
     */
    private void logRequest(ContentCachingRequestWrapper request) {
        String queryString = request.getQueryString() != null ? "?" + request.getQueryString() : "";
        log.info("Request: {} {} {}", request.getMethod(), request.getRequestURI() + queryString, request.getRemoteAddr());
        log.debug("Request headers: {}", getHeadersAsString(request));
    }

    /**
     * Log response details.
     *
     * @param response The HTTP response
     * @param startTime The request start time
     */
    private void logResponse(ContentCachingResponseWrapper response, long startTime) {
        long duration = System.currentTimeMillis() - startTime;
        log.info("Response: {} ({}ms)", response.getStatus(), duration);
        log.debug("Response headers: {}", getResponseHeadersAsString(response));
    }

    /**
     * Get request headers as a string.
     *
     * @param request The HTTP request
     * @return Headers as a string
     */
    private String getHeadersAsString(HttpServletRequest request) {
        StringBuilder headers = new StringBuilder();
        request.getHeaderNames().asIterator().forEachRemaining(headerName -> {
            headers.append(headerName).append("=").append(request.getHeader(headerName)).append(", ");
        });
        return headers.toString();
    }

    /**
     * Get response headers as a string.
     *
     * @param response The HTTP response
     * @return Headers as a string
     */
    private String getResponseHeadersAsString(HttpServletResponse response) {
        StringBuilder headers = new StringBuilder();
        response.getHeaderNames().forEach(headerName -> {
            headers.append(headerName).append("=").append(response.getHeader(headerName)).append(", ");
        });
        return headers.toString();
    }
}
