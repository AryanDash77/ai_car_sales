package com.example;

public class PaymentModule {
    public double calculateDownPayment(double carPrice, double percentage) {
        return carPrice * (percentage / 100.0);
    }
}