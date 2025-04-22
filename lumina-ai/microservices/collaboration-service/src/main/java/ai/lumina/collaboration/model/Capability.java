package ai.lumina.collaboration.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Represents a capability that agents can possess and roles can require.
 */
@Entity
@Table(name = "capabilities")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Capability {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(nullable = false)
    private String description;

    @Column(nullable = false)
    private String category;

    @Column(nullable = false)
    private int complexityLevel;

    @Column(nullable = false)
    private boolean isCore;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Check if this capability is compatible with another capability.
     * 
     * @param other The other capability to check compatibility with
     * @return True if compatible, false otherwise
     */
    public boolean isCompatibleWith(Capability other) {
        // In a real implementation, this would check for compatibility rules
        // For now, we'll consider capabilities in the same category as compatible
        return this.category.equals(other.getCategory());
    }

    /**
     * Check if this capability subsumes another capability.
     * 
     * @param other The other capability to check
     * @return True if this capability subsumes the other, false otherwise
     */
    public boolean subsumes(Capability other) {
        // In a real implementation, this would check capability hierarchies
        // For now, we'll consider higher complexity levels as subsuming lower ones in the same category
        return this.category.equals(other.getCategory()) && 
               this.complexityLevel >= other.getComplexityLevel();
    }
}
