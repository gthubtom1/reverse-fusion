package com.reversefusion;

public final class Answer {
    public static String answer(String value) {
        return "rf:" + value.trim().toUpperCase(java.util.Locale.ROOT);
    }
}
