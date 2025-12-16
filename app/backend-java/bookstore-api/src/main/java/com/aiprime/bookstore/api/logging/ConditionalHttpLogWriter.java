package com.aiprime.bookstore.api.logging;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import datadog.trace.api.CorrelationIdentifier;
import org.zalando.logbook.Correlation;
import org.zalando.logbook.HttpLogWriter;
import org.zalando.logbook.Precorrelation;

import java.io.IOException;

public class ConditionalHttpLogWriter implements HttpLogWriter {

    private final CustomHttpDebugWriter debugWriter =
            new CustomHttpDebugWriter("http.logger.full");
    private final CustomHttpErrorWriter errorWriter =
            new CustomHttpErrorWriter("http.logger.error");

    private static final ObjectMapper objectMapper = new ObjectMapper();

    // =======================
    // request
    // =======================
    @Override
    public void write(Precorrelation precorrelation, String request) throws IOException {
        String enrichedRequest = injectTraceId(request);
        debugWriter.write(precorrelation, enrichedRequest);
    }

    // =======================
    // response
    // =======================
    @Override
    public void write(Correlation correlation, String response) throws IOException {
        Integer status = parseStatusFromResponse(response);
        String enrichedResponse = injectTraceId(response);

        if (status != null && status >= 400) {
            errorWriter.write(correlation, enrichedResponse);
        } else {
            debugWriter.write(correlation, enrichedResponse);
        }
    }

    // =======================
    // helpers
    // =======================

    private String injectTraceId(String json) {
        if (json == null || json.isEmpty()) {
            return json;
        }

        try {
            JsonNode root = objectMapper.readTree(json);

            if (root.isObject()) {
                ObjectNode obj = (ObjectNode) root;

                String traceId = CorrelationIdentifier.getTraceId();
                if (traceId != null && !traceId.isBlank()) {
                    obj.put("dd.trace_id", traceId);
                }

                return objectMapper.writeValueAsString(obj);
            }
        } catch (Exception ignored) {
            // 非 JSON，直接原样返回
        }

        return json;
    }

    private Integer parseStatusFromResponse(String response) {
        if (response == null || response.isEmpty()) {
            return null;
        }

        try {
            JsonNode node = objectMapper.readTree(response);
            if (node.has("status")) {
                return node.get("status").asInt();
            }
        } catch (Exception ignored) {}

        return null;
    }
}
