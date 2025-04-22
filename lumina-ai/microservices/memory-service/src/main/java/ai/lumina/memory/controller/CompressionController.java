package ai.lumina.memory.controller;

import ai.lumina.memory.model.CompressedContext;
import ai.lumina.memory.service.CompressionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST controller for compression operations.
 */
@RestController
@RequestMapping("/api/memory/compression")
@RequiredArgsConstructor
@Slf4j
public class CompressionController {

    private final CompressionService compressionService;

    /**
     * Compress text using neural compression techniques.
     *
     * @param text Text to compress
     * @param compressionRatio Target compression ratio (0-1)
     * @return Compressed text
     */
    @PostMapping("/compress")
    public ResponseEntity<Map<String, String>> compressText(
            @RequestBody String text,
            @RequestParam(defaultValue = "0.5") double compressionRatio) {
        
        log.info("REST request to compress text with ratio {}", compressionRatio);
        String compressed = compressionService.compressText(text, compressionRatio);
        return ResponseEntity.ok(Map.of("compressed", compressed));
    }

    /**
     * Create a compressed context object from text.
     *
     * @param text Text to compress
     * @param compressionRatio Target compression ratio (0-1)
     * @return CompressedContext object
     */
    @PostMapping("/context")
    public ResponseEntity<CompressedContext> createCompressedContext(
            @RequestBody String text,
            @RequestParam(defaultValue = "0.5") double compressionRatio) {
        
        log.info("REST request to create compressed context with ratio {}", compressionRatio);
        CompressedContext context = compressionService.createCompressedContext(text, compressionRatio);
        return ResponseEntity.ok(context);
    }

    /**
     * Calculate similarity between two texts.
     *
     * @param text1 First text
     * @param text2 Second text
     * @return Similarity score (0-1)
     */
    @PostMapping("/similarity")
    public ResponseEntity<Map<String, Double>> calculateSimilarity(
            @RequestParam String text1,
            @RequestParam String text2) {
        
        log.info("REST request to calculate similarity between texts");
        double similarity = compressionService.calculateSimilarity(text1, text2);
        return ResponseEntity.ok(Map.of("similarity", similarity));
    }

    /**
     * Get embedding vector for text.
     *
     * @param text Text to embed
     * @return Embedding vector
     */
    @PostMapping("/embedding")
    public ResponseEntity<double[]> getEmbedding(
            @RequestBody String text) {
        
        log.info("REST request to get embedding for text");
        double[] embedding = compressionService.getEmbedding(text);
        return ResponseEntity.ok(embedding);
    }
}
