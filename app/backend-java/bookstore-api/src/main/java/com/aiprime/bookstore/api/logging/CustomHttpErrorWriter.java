package com.aiprime.bookstore.api.logging;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zalando.logbook.Correlation;
import org.zalando.logbook.HttpLogWriter;
import org.zalando.logbook.HttpRequest;
import org.zalando.logbook.HttpResponse;
import org.zalando.logbook.Precorrelation;

public class CustomHttpErrorWriter implements HttpLogWriter {
    private final Logger log;

    public CustomHttpErrorWriter(String loggerName) {
        log = LoggerFactory.getLogger(loggerName);
    }

    public boolean isActive() {
        return this.log.isErrorEnabled();
    }

    public void write(final Precorrelation precorrelation, final String request) {
        this.log.error(request);
    }

    public void write(final Correlation correlation, final String response) {
        this.log.error(response);
    }
}