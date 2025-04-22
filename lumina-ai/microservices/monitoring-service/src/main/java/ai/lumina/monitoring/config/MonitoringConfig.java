package ai.lumina.monitoring.config;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.prometheus.PrometheusConfig;
import io.micrometer.prometheus.PrometheusMeterRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.boot.actuate.autoconfigure.metrics.MeterRegistryCustomizer;

import io.opentracing.Tracer;
import io.jaegertracing.Configuration.ReporterConfiguration;
import io.jaegertracing.Configuration.SamplerConfiguration;
import io.jaegertracing.Configuration.SenderConfiguration;
import io.jaegertracing.internal.samplers.ConstSampler;

import org.springframework.beans.factory.annotation.Value;

/**
 * Configuration for monitoring instrumentation.
 * Sets up metrics collection with Prometheus and distributed tracing with Jaeger.
 */
@Configuration
public class MonitoringConfig {

    @Value("${spring.application.name}")
    private String applicationName;

    /**
     * Configures the Jaeger tracer.
     *
     * @return The configured Jaeger tracer
     */
    @Bean
    public Tracer jaegerTracer() {
        return new io.jaegertracing.Configuration(applicationName)
                .withSampler(
                        SamplerConfiguration.fromEnv()
                                .withType(ConstSampler.TYPE)
                                .withParam(1))
                .withReporter(
                        ReporterConfiguration.fromEnv()
                                .withLogSpans(true)
                                .withSender(
                                        SenderConfiguration.fromEnv()
                                                .withEndpoint("http://jaeger:14268/api/traces")))
                .getTracer();
    }

    /**
     * Customizes the meter registry with common tags.
     *
     * @return The meter registry customizer
     */
    @Bean
    MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> registry.config()
                .commonTags("application", applicationName)
                .commonTags("environment", "${spring.profiles.active:default}");
    }

    /**
     * Creates a Prometheus meter registry.
     *
     * @return The Prometheus meter registry
     */
    @Bean
    public PrometheusMeterRegistry prometheusMeterRegistry() {
        return new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
    }
}
