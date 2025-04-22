package ai.lumina.monitoring.aspect;

import io.opentracing.Span;
import io.opentracing.Tracer;
import io.opentracing.tag.Tags;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.stream.Collectors;

/**
 * Aspect for distributed tracing.
 * This aspect automatically creates spans for methods in service and controller classes.
 */
@Aspect
@Component
@RequiredArgsConstructor
@Slf4j
public class TracingAspect {

    private final Tracer tracer;

    /**
     * Creates spans for service methods.
     *
     * @param joinPoint The join point for the intercepted method
     * @return The result of the method execution
     * @throws Throwable If an error occurs during method execution
     */
    @Around("execution(* ai.lumina..service.*.*(..))")
    public Object traceServiceMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        return traceMethod(joinPoint, "service");
    }

    /**
     * Creates spans for controller methods.
     *
     * @param joinPoint The join point for the intercepted method
     * @return The result of the method execution
     * @throws Throwable If an error occurs during method execution
     */
    @Around("execution(* ai.lumina..controller.*.*(..))")
    public Object traceControllerMethod(ProceedingJoinPoint joinPoint) throws Throwable {
        return traceMethod(joinPoint, "controller");
    }

    /**
     * Helper method to create spans and trace method execution.
     *
     * @param joinPoint The join point for the intercepted method
     * @param componentType The type of component (service, controller)
     * @return The result of the method execution
     * @throws Throwable If an error occurs during method execution
     */
    private Object traceMethod(ProceedingJoinPoint joinPoint, String componentType) throws Throwable {
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = method.getName();
        String operationName = className + "." + methodName;
        
        Span span = tracer.buildSpan(operationName).start();
        span.setTag("component", componentType);
        span.setTag("class", className);
        span.setTag("method", methodName);
        
        // Add method parameters as tags (be careful with sensitive data)
        Object[] args = joinPoint.getArgs();
        if (args != null && args.length > 0) {
            String argsStr = Arrays.stream(args)
                    .map(arg -> arg == null ? "null" : arg.toString())
                    .collect(Collectors.joining(", "));
            span.setTag("args", argsStr);
        }
        
        try (io.opentracing.Scope scope = tracer.scopeManager().activate(span)) {
            return joinPoint.proceed();
        } catch (Throwable t) {
            Tags.ERROR.set(span, true);
            span.log(t.getMessage());
            throw t;
        } finally {
            span.finish();
        }
    }
}
