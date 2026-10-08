package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class CarInventoryTest {
    @Test
    public void testCalculateTotalPrice() {
        CarInventory inventory = new CarInventory();
        assertEquals(12000, inventory.calculateTotalPrice(10000, 2000));
    }
}

