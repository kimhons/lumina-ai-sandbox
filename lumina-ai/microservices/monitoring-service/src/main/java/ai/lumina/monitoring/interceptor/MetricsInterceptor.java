package ai.lumina.monitoring.interceptor;

import io.micrometer.core.instrument.MeterRegistry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.concurrent.TimeUnit;

/**
 * Interceptor for measuring and recording API endpoint performance metrics.
 * This interceptor tracks request counts, response times, and error rates for each endpoint.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class MetricsInterceptor implements HandlerInterceptor {

    private final MeterRegistry meterRegistry;
    private static final String REQUEST_START_TIME = "requestStartTime";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        request.setAttribute(REQUEST_START_TIME, System.nanoTime());
        return true;
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) {
        // Not used
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        Long startTime = (Long) request.getAttribute(REQUEST_START_TIME);
        if (startTime == null) {
            return;
        }

        long duration = System.nanoTime() - startTime;
        String uri = request.getRequestURI();
        String method = request.getMethod();
        int status = response.getStatus();
        boolean isError = status >= 400;
        String outcome = isError ? "ERROR" : "SUCCESS";

        // Record request count
        meterRegistry.counter("http.requests.total", 
                "uri", uri, 
                "method", method, 
                "status", String.valueOf(status), 
                "outcome", outcome).increment();

        // Record request duration
        meterRegistry.timer("http.requests.duration", 
                "uri", uri, 
                "method", method, 
                "status", String.valueOf(status), 
                "outcome", outcome).record(duration, TimeUnit.NANOSECONDS);

        // Log slow requests
        if (duration > TimeUnit.MILLISECONDS.toNanos(500)) {
            log.warn("Slow request: {} {} took {}ms with status {}", 
                    method, uri, TimeUnit.NANOSECONDS.toMillis(duration), status);
        }
    }
}
