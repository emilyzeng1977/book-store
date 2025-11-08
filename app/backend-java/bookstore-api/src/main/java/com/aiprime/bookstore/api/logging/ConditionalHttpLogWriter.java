package com.aiprime.bookstore.api.logging;

import org.zalando.logbook.Correlation;
import org.zalando.logbook.HttpLogWriter;
import org.zalando.logbook.Precorrelation;

import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ConditionalHttpLogWriter implements HttpLogWriter {
    private final CustomHttpDebugWriter debugWriter = new CustomHttpDebugWriter("http.logger.full");
    private final CustomHttpErrorWriter errorWriter = new CustomHttpErrorWriter("http.logger.error");

    private static final Pattern TEXT_STATUS_PATTERN = Pattern.compile("HTTP/\\d\\.\\d\\s+(\\d{3})");

    @Override
    public void write(Precorrelation precorrelation, String request) throws IOException {
        // 不输出
    }

    @Override
    public void write(Correlation correlation, String response) throws IOException {
        Integer status = parseStatusFromResponse(response);

        if (status != null && status >= 400) {
            errorWriter.write(correlation, response);
        } else {
            debugWriter.write(correlation, response);
        }
    }

    private Integer parseStatusFromResponse(String response) {
        if (response == null || response.isEmpty()) {
            return null;
        }

        Matcher matcher = TEXT_STATUS_PATTERN.matcher(response);
        if (matcher.find()) {
            try {
                return Integer.parseInt(matcher.group(1));
            } catch (NumberFormatException ignored) {}
        }
        return null;
    }
}