package ai.lumina.monitoring.aspect;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;
import java.util.concurrent.TimeUnit;

/**
 * Aspect for measuring method execution time and recording metrics.
 * This aspect automatically instruments methods in service and controller classes.
 */
@Aspect
@Component
@RequiredArgsConstructor
@Slf4j
public class PerformanceMonitoringAspect {

    private final MeterRegistry meterRegistry;

    /**
     * Measures execution time for service methods and records metrics.
     *
     * @param joinPoint The join point for the intercepted method
     * @return The result of the method execution
     * @throws Throwable If an error occurs during method execution
     */
    @Around("execution(* ai.lumina..service.*.*(..))")
    public Object measureServiceMethodExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        return measureExecutionTime(joinPoint, "service");
    }

    /**
     * Measures execution time for controller methods and records metrics.
     *
     * @param joinPoint The join point for the intercepted method
     * @return The result of the method execution
     * @throws Throwable If an error occurs during method execution
     */
    @Around("execution(* ai.lumina..controller.*.*(..))")
    public Object measureControllerMethodExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        return measureExecutionTime(joinPoint, "controller");
    }

    /**
     * Measures execution time for repository methods and records metrics.
     *
     * @param joinPoint The join point for the intercepted method
     * @return The result of the method execution
     * @throws Throwable If an error occurs during method execution
     */
    @Around("execution(* ai.lumina..repository.*.*(..))")
    public Object measureRepositoryMethodExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        return measureExecutionTime(joinPoint, "repository");
    }

    /**
     * Helper method to measure execution time and record metrics.
     *
     * @param joinPoint The join point for the intercepted method
     * @param componentType The type of component (service, controller, repository)
     * @return The result of the method execution
     * @throws Throwable If an error occurs during method execution
     */
    private Object measureExecutionTime(ProceedingJoinPoint joinPoint, String componentType) throws Throwable {
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = method.getName();
        String metricName = "method.execution.time";
        
        Timer timer = Timer.builder(metricName)
                .tag("class", className)
                .tag("method", methodName)
                .tag("component", componentType)
                .description("Execution time of " + className + "." + methodName)
                .register(meterRegistry);
        
        long startTime = System.nanoTime();
        boolean success = false;
        
        try {
            Object result = joinPoint.proceed();
            success = true;
            return result;
        } finally {
            long duration = System.nanoTime() - startTime;
            timer.record(duration, TimeUnit.NANOSECONDS);
            
            // Record success/failure count
            meterRegistry.counter("method.execution.count", 
                    "class", className, 
                    "method", methodName, 
                    "component", componentType, 
                    "success", String.valueOf(success)).increment();
            
            if (duration > TimeUnit.MILLISECONDS.toNanos(500)) {
                log.warn("Slow method execution: {}.{} took {}ms", 
                        className, methodName, TimeUnit.NANOSECONDS.toMillis(duration));
            }
        }
    }
}
