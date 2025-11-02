package com.aiprime.bookstore.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class BookstoreApplication {
	@GetMapping("/")
	public String index() {
		return "Welcome to Bookstore API!";
	}

	@GetMapping("/health")
	public String health() {
		return "Health Check OK";
	}

	public static void main(String[] args) {
		SpringApplication.run(BookstoreApplication.class, args);
	}
	@GetMapping("/hello")
	public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {
		return String.format("Hello %s!", name);
	}
}
