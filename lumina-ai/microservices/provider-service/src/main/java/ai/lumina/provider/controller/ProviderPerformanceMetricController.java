package ai.lumina.provider.controller;

import ai.lumina.provider.dto.ProviderPerformanceMetricDto;
import ai.lumina.provider.service.ProviderPerformanceMetricService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/providers/metrics")
@RequiredArgsConstructor
public class ProviderPerformanceMetricController {

    private final ProviderPerformanceMetricService metricService;

    @GetMapping
    public ResponseEntity<List<ProviderPerformanceMetricDto>> getAllMetrics() {
        List<ProviderPerformanceMetricDto> metrics = metricService.getAllMetrics();
        return ResponseEntity.ok(metrics);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProviderPerformanceMetricDto> getMetricById(@PathVariable Long id) {
        return metricService.getMetricById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/provider/{providerId}")
    public ResponseEntity<List<ProviderPerformanceMetricDto>> getMetricsByProviderId(@PathVariable Long providerId) {
        List<ProviderPerformanceMetricDto> metrics = metricService.getMetricsByProviderId(providerId);
        return ResponseEntity.ok(metrics);
    }

    @GetMapping("/model/{modelId}")
    public ResponseEntity<List<ProviderPerformanceMetricDto>> getMetricsByModelId(@PathVariable Long modelId) {
        List<ProviderPerformanceMetricDto> metrics = metricService.getMetricsByModelId(modelId);
        return ResponseEntity.ok(metrics);
    }

    @GetMapping("/name/{metricName}")
    public ResponseEntity<List<ProviderPerformanceMetricDto>> getMetricsByName(@PathVariable String metricName) {
        List<ProviderPerformanceMetricDto> metrics = metricService.getMetricsByName(metricName);
        return ResponseEntity.ok(metrics);
    }

    @GetMapping("/provider/{providerId}/timerange")
    public ResponseEntity<List<ProviderPerformanceMetricDto>> getMetricsByProviderIdAndTimeRange(
            @PathVariable Long providerId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTime) {
        List<ProviderPerformanceMetricDto> metrics = metricService.getMetricsByProviderIdAndTimeRange(providerId, startTime, endTime);
        return ResponseEntity.ok(metrics);
    }

    @GetMapping("/model/{modelId}/timerange")
    public ResponseEntity<List<ProviderPerformanceMetricDto>> getMetricsByModelIdAndTimeRange(
            @PathVariable Long modelId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTime) {
        List<ProviderPerformanceMetricDto> metrics = metricService.getMetricsByModelIdAndTimeRange(modelId, startTime, endTime);
        return ResponseEntity.ok(metrics);
    }

    @GetMapping("/provider/{providerId}/average/{metricName}")
    public ResponseEntity<Double> getAverageMetricForProvider(
            @PathVariable Long providerId,
            @PathVariable String metricName) {
        Double average = metricService.getAverageMetricForProvider(providerId, metricName);
        return average != null ? ResponseEntity.ok(average) : ResponseEntity.notFound().build();
    }

    @GetMapping("/model/{modelId}/average/{metricName}")
    public ResponseEntity<Double> getAverageMetricForModel(
            @PathVariable Long modelId,
            @PathVariable String metricName) {
        Double average = metricService.getAverageMetricForModel(modelId, metricName);
        return average != null ? ResponseEntity.ok(average) : ResponseEntity.notFound().build();
    }

    @PostMapping
    public ResponseEntity<ProviderPerformanceMetricDto> createMetric(@RequestBody ProviderPerformanceMetricDto metricDto) {
        return metricService.createMetric(metricDto)
                .map(created -> ResponseEntity.status(HttpStatus.CREATED).body(created))
                .orElse(ResponseEntity.badRequest().build());
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProviderPerformanceMetricDto> updateMetric(
            @PathVariable Long id, 
            @RequestBody ProviderPerformanceMetricDto metricDto) {
        return metricService.updateMetric(id, metricDto)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteMetric(@PathVariable Long id) {
        boolean deleted = metricService.deleteMetric(id);
        return deleted ? 
                ResponseEntity.noContent().build() : 
                ResponseEntity.notFound().build();
    }
}
