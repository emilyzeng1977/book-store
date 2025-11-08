package com.aiprime.bookstore.api.logging;

import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.filter.ForwardedHeaderFilter;
import org.zalando.logbook.Logbook;
import org.zalando.logbook.core.DefaultSink;
import org.zalando.logbook.json.JsonHttpLogFormatter;
import org.zalando.logbook.servlet.LogbookFilter;

import static org.zalando.logbook.core.Conditions.*;

@Configuration
public class LogbookConfiguration {

    @Bean
    public Logbook logbook() {
        return Logbook.builder()
                .condition(exclude(
                        requestTo("/actuator/**"),
                        requestTo("/health"),
                        requestTo("/favicon.ico")
                ))
                .sink(new DefaultSink(
                        new JsonHttpLogFormatter(),
                        new ConditionalHttpLogWriter()
                ))
                .build();
    }

    @Bean
    public FilterRegistrationBean<ForwardedHeaderFilter> forwardedHeaderFilter() {
        FilterRegistrationBean<ForwardedHeaderFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new ForwardedHeaderFilter());
        registration.setOrder(0); // 必须在 LogbookFilter 之前
        return registration;
    }

    @Bean
    public FilterRegistrationBean<LogbookFilter> logbookFilter(Logbook logbook) {
        FilterRegistrationBean<LogbookFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new LogbookFilter(logbook));
        registration.addUrlPatterns("/*");
        registration.setOrder(1); // 在 ForwardedHeaderFilter 之后
        return registration;
    }
}