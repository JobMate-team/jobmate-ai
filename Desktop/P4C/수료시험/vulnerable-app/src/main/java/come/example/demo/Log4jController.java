package com.example.demo;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class Log4jController {

    private static final Logger logger = LogManager.getLogger(Log4jController.class);

    @GetMapping("/log")
    @ResponseBody
    public String logInput(@RequestParam String input) {
        logger.info("User input: {}", input);
        return "Logged: " + input;
    }
}
