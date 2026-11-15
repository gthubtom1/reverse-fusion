package com.reversefusion;

public final class Answer {
    public static String answer(String value) {
        String normalized = value.trim().toUpperCase(java.util.Locale.ROOT);
        return new StringBuilder("rf:").append(normalized).toString();
    }
}
