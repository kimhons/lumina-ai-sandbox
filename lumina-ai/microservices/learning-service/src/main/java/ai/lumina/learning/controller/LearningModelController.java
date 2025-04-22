package ai.lumina.learning.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.PathVariable;

import ai.lumina.learning.model.LearningModel;
import ai.lumina.learning.repository.LearningModelRepository;
import ai.lumina.learning.service.LearningModelService;

import java.util.Map;
import java.util.Optional;
import java.util.List;
import lombok.extern.slf4j.Slf4j;

/**
 * Controller for managing learning models.
 * Provides endpoints for creating, retrieving, updating, and using learning models.
 */
@RestController
@RequestMapping("/api/v1/learning/models")
@Slf4j
public class LearningModelController {

    @Autowired
    private LearningModelRepository modelRepository;
    
    @Autowired
    private LearningModelService modelService;
    
    /**
     * Get all learning models.
     * 
     * @return List of all learning models
     */
    @GetMapping
    public ResponseEntity<Iterable<LearningModel>> getAllModels() {
        log.info("Received request for all learning models");
        
        Iterable<LearningModel> models = modelRepository.findAll();
        
        return ResponseEntity.ok(models);
    }
    
    /**
     * Get a learning model by ID.
     * 
     * @param modelId ID of the model
     * @return The learning model
     */
    @GetMapping("/{modelId}")
    public ResponseEntity<LearningModel> getModel(@PathVariable String modelId) {
        log.info("Received request for learning model: {}", modelId);
        
        Optional<LearningModel> model = modelRepository.findById(modelId);
        
        if (model.isPresent()) {
            return ResponseEntity.ok(model.get());
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * Create a new learning model.
     * 
     * @param request Model creation request
     * @return The created model
     */
    @PostMapping
    public ResponseEntity<LearningModel> createModel(@RequestBody Map<String, Object> request) {
        log.info("Received learning model creation request: {}", request);
        
        LearningModel model = modelService.createModel(request);
        
        return ResponseEntity.ok(model);
    }
    
    /**
     * Train a learning model.
     * 
     * @param modelId ID of the model to train
     * @param request Training request
     * @return Training result
     */
    @PostMapping("/{modelId}/train")
    public ResponseEntity<Map<String, Object>> trainModel(
            @PathVariable String modelId,
            @RequestBody Map<String, Object> request) {
        
        log.info("Received training request for model {}: {}", modelId, request);
        
        Map<String, Object> result = modelService.trainModel(modelId, request);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Make predictions using a learning model.
     * 
     * @param modelId ID of the model to use
     * @param request Prediction request
     * @return Prediction result
     */
    @PostMapping("/{modelId}/predict")
    public ResponseEntity<Map<String, Object>> predict(
            @PathVariable String modelId,
            @RequestBody Map<String, Object> request) {
        
        log.info("Received prediction request for model {}: {}", modelId, request);
        
        Map<String, Object> result = modelService.predict(modelId, request);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Get explanations for model predictions.
     * 
     * @param modelId ID of the model
     * @param request Explanation request
     * @return Explanation result
     */
    @PostMapping("/{modelId}/explain")
    public ResponseEntity<Map<String, Object>> explain(
            @PathVariable String modelId,
            @RequestBody Map<String, Object> request) {
        
        log.info("Received explanation request for model {}: {}", modelId, request);
        
        Map<String, Object> result = modelService.explain(modelId, request);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Update a learning model.
     * 
     * @param modelId ID of the model to update
     * @param request Update request
     * @return Update result
     */
    @PostMapping("/{modelId}/update")
    public ResponseEntity<Map<String, Object>> updateModel(
            @PathVariable String modelId,
            @RequestBody Map<String, Object> request) {
        
        log.info("Received update request for model {}: {}", modelId, request);
        
        Map<String, Object> result = modelService.updateModel(modelId, request);
        
        return ResponseEntity.ok(result);
    }
    
    /**
     * Get models by type.
     * 
     * @param type Model type
     * @return List of models of the specified type
     */
    @GetMapping("/type/{type}")
    public ResponseEntity<List<LearningModel>> getModelsByType(@PathVariable String type) {
        log.info("Received request for models of type: {}", type);
        
        List<LearningModel> models = modelRepository.findByType(type);
        
        return ResponseEntity.ok(models);
    }
    
    /**
     * Get models by domain.
     * 
     * @param domain Model domain
     * @return List of models for the specified domain
     */
    @GetMapping("/domain/{domain}")
    public ResponseEntity<List<LearningModel>> getModelsByDomain(@PathVariable String domain) {
        log.info("Received request for models in domain: {}", domain);
        
        List<LearningModel> models = modelRepository.findByDomain(domain);
        
        return ResponseEntity.ok(models);
    }
}
