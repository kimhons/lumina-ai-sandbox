package ai.lumina.memory.service;

import ai.lumina.memory.model.CompressedContext;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Random;

/**
 * Service for neural context compression and embedding generation.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CompressionService {

    private static final int EMBEDDING_DIMENSION = 384;
    private final Random random = new Random();

    /**
     * Compress text using neural compression techniques.
     *
     * @param text Text to compress
     * @param compressionRatio Target compression ratio (0-1)
     * @return Compressed text
     */
    public String compressText(String text, double compressionRatio) {
        log.info("Compressing text with ratio {}", compressionRatio);
        
        if (text == null || text.isEmpty()) {
            return "";
        }
        
        if (compressionRatio >= 1.0) {
            return text;
        }
        
        // Simple implementation - in production this would use a neural model
        // This is a placeholder that extracts sentences based on the compression ratio
        
        // Split text into sentences
        String[] sentences = text.split("(?<=[.!?])\\s+");
        
        if (sentences.length <= 1) {
            return text;
        }
        
        // Calculate number of sentences to keep
        int sentencesToKeep = Math.max(1, (int)(sentences.length * compressionRatio));
        
        // For simplicity, keep the first sentence, the last sentence, and a selection in between
        StringBuilder compressed = new StringBuilder(sentences[0]);
        
        if (sentencesToKeep > 2) {
            // Select sentences from the middle
            int step = (sentences.length - 2) / (sentencesToKeep - 2);
            step = Math.max(1, step);
            
            for (int i = 1; i < sentences.length - 1; i += step) {
                if (compressed.length() > 0) {
                    compressed.append(" ");
                }
                compressed.append(sentences[i]);
                
                // Break if we've selected enough sentences
                if (i / step >= sentencesToKeep - 2) {
                    break;
                }
            }
        }
        
        // Add the last sentence if we have more than one sentence
        if (sentences.length > 1 && sentencesToKeep > 1) {
            if (compressed.length() > 0) {
                compressed.append(" ");
            }
            compressed.append(sentences[sentences.length - 1]);
        }
        
        return compressed.toString();
    }

    /**
     * Create a compressed context object from text.
     *
     * @param text Text to compress
     * @param compressionRatio Target compression ratio (0-1)
     * @return CompressedContext object
     */
    public CompressedContext createCompressedContext(String text, double compressionRatio) {
        log.info("Creating compressed context with ratio {}", compressionRatio);
        
        String compressedText = compressText(text, compressionRatio);
        double[] embedding = getEmbedding(text);
        
        CompressedContext context = new CompressedContext();
        context.setOriginalText(text);
        context.setCompressedText(compressedText);
        context.setCompressionRatio(compressionRatio);
        context.setEmbedding(embedding);
        
        return context;
    }

    /**
     * Get embedding vector for text.
     *
     * @param text Text to embed
     * @return Embedding vector
     */
    public double[] getEmbedding(String text) {
        log.debug("Generating embedding for text");
        
        if (text == null || text.isEmpty()) {
            // Return zero vector for empty text
            return new double[EMBEDDING_DIMENSION];
        }
        
        // This is a placeholder implementation
        // In production, this would call a real embedding model
        
        // Create a deterministic embedding based on text hash
        double[] embedding = new double[EMBEDDING_DIMENSION];
        int hash = text.hashCode();
        random.setSeed(hash);
        
        for (int i = 0; i < EMBEDDING_DIMENSION; i++) {
            embedding[i] = random.nextGaussian();
        }
        
        // Normalize the vector
        double norm = 0.0;
        for (double v : embedding) {
            norm += v * v;
        }
        norm = Math.sqrt(norm);
        
        if (norm > 0) {
            for (int i = 0; i < embedding.length; i++) {
                embedding[i] /= norm;
            }
        }
        
        return embedding;
    }

    /**
     * Calculate similarity between two texts.
     *
     * @param text1 First text
     * @param text2 Second text
     * @return Similarity score (0-1)
     */
    public double calculateSimilarity(String text1, String text2) {
        log.debug("Calculating similarity between texts");
        
        double[] embedding1 = getEmbedding(text1);
        double[] embedding2 = getEmbedding(text2);
        
        return cosineSimilarity(embedding1, embedding2);
    }

    /**
     * Calculate cosine similarity between two vectors.
     *
     * @param vector1 First vector
     * @param vector2 Second vector
     * @return Cosine similarity (0-1)
     */
    public double cosineSimilarity(double[] vector1, double[] vector2) {
        if (vector1.length != vector2.length) {
            return 0.0;
        }
        
        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;
        
        for (int i = 0; i < vector1.length; i++) {
            dotProduct += vector1[i] * vector2[i];
            norm1 += Math.pow(vector1[i], 2);
            norm2 += Math.pow(vector2[i], 2);
        }
        
        if (norm1 == 0.0 || norm2 == 0.0) {
            return 0.0;
        }
        
        return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }
}
