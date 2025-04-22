package ai.lumina.monitoring.util;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.OperatingSystemMXBean;
import java.lang.management.ThreadMXBean;

/**
 * Utility class for collecting system resource metrics.
 * This class provides methods to monitor CPU, memory, and thread usage.
 */
@Component
@Slf4j
public class SystemResourceMonitor {

    private final OperatingSystemMXBean osBean;
    private final MemoryMXBean memoryBean;
    private final ThreadMXBean threadBean;
    private final Runtime runtime;

    /**
     * Constructor initializes the MX beans for system monitoring.
     */
    public SystemResourceMonitor() {
        this.osBean = ManagementFactory.getOperatingSystemMXBean();
        this.memoryBean = ManagementFactory.getMemoryMXBean();
        this.threadBean = ManagementFactory.getThreadMXBean();
        this.runtime = Runtime.getRuntime();
    }

    /**
     * Get the current CPU load.
     *
     * @return The system CPU load as a percentage (0-100)
     */
    public double getCpuLoad() {
        double load = osBean.getSystemLoadAverage();
        if (load < 0) {
            // Not available on some platforms
            return -1;
        }
        return (load / osBean.getAvailableProcessors()) * 100;
    }

    /**
     * Get the current heap memory usage.
     *
     * @return The heap memory usage in bytes
     */
    public long getHeapMemoryUsage() {
        return memoryBean.getHeapMemoryUsage().getUsed();
    }

    /**
     * Get the maximum heap memory.
     *
     * @return The maximum heap memory in bytes
     */
    public long getMaxHeapMemory() {
        return memoryBean.getHeapMemoryUsage().getMax();
    }

    /**
     * Get the heap memory usage as a percentage.
     *
     * @return The heap memory usage as a percentage (0-100)
     */
    public double getHeapMemoryPercentage() {
        long used = memoryBean.getHeapMemoryUsage().getUsed();
        long max = memoryBean.getHeapMemoryUsage().getMax();
        return ((double) used / max) * 100;
    }

    /**
     * Get the non-heap memory usage.
     *
     * @return The non-heap memory usage in bytes
     */
    public long getNonHeapMemoryUsage() {
        return memoryBean.getNonHeapMemoryUsage().getUsed();
    }

    /**
     * Get the total available memory.
     *
     * @return The total available memory in bytes
     */
    public long getTotalMemory() {
        return runtime.totalMemory();
    }

    /**
     * Get the free memory.
     *
     * @return The free memory in bytes
     */
    public long getFreeMemory() {
        return runtime.freeMemory();
    }

    /**
     * Get the number of active threads.
     *
     * @return The number of active threads
     */
    public int getThreadCount() {
        return threadBean.getThreadCount();
    }

    /**
     * Get the peak thread count.
     *
     * @return The peak thread count
     */
    public int getPeakThreadCount() {
        return threadBean.getPeakThreadCount();
    }

    /**
     * Get the number of daemon threads.
     *
     * @return The number of daemon threads
     */
    public int getDaemonThreadCount() {
        return threadBean.getDaemonThreadCount();
    }

    /**
     * Get the total started thread count.
     *
     * @return The total started thread count
     */
    public long getTotalStartedThreadCount() {
        return threadBean.getTotalStartedThreadCount();
    }

    /**
     * Log the current system resource usage.
     */
    public void logResourceUsage() {
        log.info("System Resource Usage - CPU Load: {}%, Heap Memory: {}%, Thread Count: {}", 
                String.format("%.2f", getCpuLoad()),
                String.format("%.2f", getHeapMemoryPercentage()),
                getThreadCount());
    }
}
