package ai.lumina.ui.adaptive.repository;

import ai.lumina.ui.adaptive.model.Notification;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository for managing notifications in the database
 */
@Repository
public interface NotificationRepository extends JpaRepository<Notification, Long> {
    
    /**
     * Find notifications by user ID
     * 
     * @param userId The ID of the user
     * @return List of notifications for the user
     */
    List<Notification> findByUserIdOrderByCreatedAtDesc(String userId);
    
    /**
     * Find unread notifications by user ID
     * 
     * @param userId The ID of the user
     * @return List of unread notifications for the user
     */
    List<Notification> findByUserIdAndReadFalseOrderByCreatedAtDesc(String userId);
    
    /**
     * Delete notifications by user ID
     * 
     * @param userId The ID of the user
     */
    void deleteByUserId(String userId);
}
