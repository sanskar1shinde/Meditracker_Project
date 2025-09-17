package com.example.meditracker.controller;

import com.example.meditracker.service.SchedularTimingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/scheduler")
public class SchedularTimingController {

    @Autowired
    private SchedularTimingService service;

    @PostMapping("/start")
    public ResponseEntity<String> startScheduler(@RequestParam Integer delayInSeconds) {
        service.start(delayInSeconds);
        return ResponseEntity.ok("✅ Scheduler will start after " + delayInSeconds + " seconds.");
    }

    @PostMapping("/stop")
    public ResponseEntity<String> stopScheduler() {
        return ResponseEntity.ok(service.stop());
    }

    @PostMapping("/update")
    public ResponseEntity<String> updateScheduler(@RequestParam Integer delayInSeconds) {
        service.stop();
        service.start(delayInSeconds);
        return ResponseEntity.ok("✅ Scheduler updated to start after " + delayInSeconds + " seconds.");
    }

    @GetMapping("/status")
    public ResponseEntity<String> getStatus() {
        return ResponseEntity.ok(service.getStatus());
    }
}
