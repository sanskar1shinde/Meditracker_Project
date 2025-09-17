package com.example.meditracker.service;

import com.example.meditracker.repository.SchedularTimingRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.concurrent.*;

@Service
public class SchedularTimingService {

    @Autowired
    private SchedularTimingRepository repository;

    private ScheduledExecutorService executorService;
    private ScheduledFuture<?> scheduledFuture;

    public void start(int delayInSeconds) {
        stop();
        executorService = Executors.newSingleThreadScheduledExecutor();

        scheduledFuture = executorService.scheduleAtFixedRate(() -> {
            try {
                System.out.println("⏱ Running insert at: " + LocalDateTime.now());
                repository.insertRandomData();
            } catch (Exception e) {
                e.printStackTrace();  // critical!
                System.err.println("❌ Exception in scheduler: " + e.getMessage());
            }
        }, delayInSeconds, delayInSeconds, TimeUnit.SECONDS);
    }


    public String stop() {
        String status = "⚠️ No active scheduler to stop.";

        if (scheduledFuture != null && !scheduledFuture.isCancelled()) {
            scheduledFuture.cancel(true);
            status = "✅ Scheduled task cancelled.";
        }

        if (executorService != null && !executorService.isShutdown()) {
            executorService.shutdownNow();
            status += "\n🛑 Executor service shut down.";
        }

        scheduledFuture = null;
        executorService = null;
        System.out.println(status);
        return status;
    }


    public boolean isRunning() {
        if (executorService == null || executorService.isShutdown()) {
            return false;
        }

        return scheduledFuture != null &&
                !scheduledFuture.isCancelled() &&
                !scheduledFuture.isDone();
    }


    public String getStatus() {
        if (isRunning()) {
            return "✅ Scheduler is currently running.";
        } else if (executorService == null) {
            return "⏳ Scheduler has not been initialized yet.";
        } else if (executorService.isShutdown()) {
            return "🛑 Scheduler was shut down.";
        } else {
            return "⚠️ Scheduler is not currently running.";
        }
    }
}
