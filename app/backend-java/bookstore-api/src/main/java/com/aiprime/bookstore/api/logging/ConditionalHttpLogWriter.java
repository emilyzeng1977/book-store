package com.aiprime.bookstore.api.logging;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.zalando.logbook.Correlation;
import org.zalando.logbook.HttpLogWriter;
import org.zalando.logbook.Precorrelation;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ConditionalHttpLogWriter implements HttpLogWriter {

    private final CustomHttpDebugWriter debugWriter = new CustomHttpDebugWriter("http.logger.full");
    private final CustomHttpErrorWriter errorWriter = new CustomHttpErrorWriter("http.logger.error");

    private static final ObjectMapper objectMapper = new ObjectMapper();

    // 暂存 correlationId -> request
    private final Map<String, String> pendingRequests = new ConcurrentHashMap<>();

    @Override
    public void write(Precorrelation precorrelation, String request) throws IOException {
        // 暂存 request，key 用 correlation id
        pendingRequests.put(precorrelation.getId(), request);
    }

    @Override
    public void write(Correlation correlation, String response) throws IOException {
        Integer status = parseStatusFromResponse(response);

        // 使用 correlation.getId() 取出之前存的 request
        String request = pendingRequests.remove(correlation.getId());

        if (status != null && status >= 400) {
            if (request != null) {
                errorWriter.write(precorrelationFromCorrelation(correlation), request);
            }
            errorWriter.write(correlation, response);
        } else {
            if (request != null) {
                debugWriter.write(precorrelationFromCorrelation(correlation), request);
            }
            debugWriter.write(correlation, response);
        }
    }

    /**
     * 从 Correlation 获取对应的 Precorrelation
     * 这里我们直接用 response writer 调用时，Logbook 内部会用 correlation 生成 request 相关信息
     * 如果你的 writer 不依赖 Precorrelation，可直接把 request 作为字符串写入
     */
    private Precorrelation precorrelationFromCorrelation(Correlation correlation) {
        // 如果 writer 接受 String request，直接返回 null 或自己封装即可
        return null;
    }

    private Integer parseStatusFromResponse(String response) {
        if (response == null || response.isEmpty()) return null;
        try {
            JsonNode node = objectMapper.readTree(response);
            if (node.has("status")) {
                return node.get("status").asInt();
            }
        } catch (IOException ignored) {}
        return null;
    }
}
