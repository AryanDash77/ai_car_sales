package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class CustomerModuleTest {
    @Test
    public void testCalculateLoyaltyPoints() {
        CustomerModule customer = new CustomerModule();
        assertEquals(200, customer.calculateLoyaltyPoints(2));
    }
}