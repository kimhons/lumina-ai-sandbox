package ai.lumina.learning.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ai.lumina.learning.model.LearningModel;

/**
 * Repository interface for LearningModel entities.
 * Provides CRUD operations and custom queries for learning models.
 */
@Repository
public interface LearningModelRepository extends JpaRepository<LearningModel, String> {
    
    /**
     * Find models by type.
     * 
     * @param type The model type
     * @return List of models with the specified type
     */
    Iterable<LearningModel> findByType(LearningModel.ModelType type);
    
    /**
     * Find models by status.
     * 
     * @param status The model status
     * @return List of models with the specified status
     */
    Iterable<LearningModel> findByStatus(LearningModel.ModelStatus status);
    
    /**
     * Find models by name containing the specified string.
     * 
     * @param name The name substring to search for
     * @return List of models with names containing the specified string
     */
    Iterable<LearningModel> findByNameContaining(String name);
    
    /**
     * Find models by created by.
     * 
     * @param createdBy The creator ID
     * @return List of models created by the specified creator
     */
    Iterable<LearningModel> findByCreatedBy(String createdBy);
}
