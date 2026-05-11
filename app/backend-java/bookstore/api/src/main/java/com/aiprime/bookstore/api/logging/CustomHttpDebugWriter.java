package com.aiprime.bookstore.api.logging;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zalando.logbook.Correlation;
import org.zalando.logbook.HttpLogWriter;
import org.zalando.logbook.Precorrelation;

public class CustomHttpDebugWriter implements HttpLogWriter {
    private final Logger log;

    public CustomHttpDebugWriter(String loggerName) {
        log = LoggerFactory.getLogger(loggerName);
    }

    @Override
    public void write(final Precorrelation precorrelation, final String request) {
        this.log.debug(request);
    }

    @Override
    public void write(final Correlation correlation, final String response) {
        this.log.debug(response);
    }
}