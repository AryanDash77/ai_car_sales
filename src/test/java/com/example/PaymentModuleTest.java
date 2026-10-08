package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class PaymentModuleTest {
    @Test
    public void testCalculateDownPayment() {
        PaymentModule payment = new PaymentModule();
        assertEquals(2000.0, payment.calculateDownPayment(10000.0, 20.0), 0.001);
    }
}