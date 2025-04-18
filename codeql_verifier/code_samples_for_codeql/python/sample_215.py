
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Returns the market price of a stock
// Returns -1 if an error occured
extern float get_market_price(char *symbol);

// Calculate the value of a sale of a number of shares where the price comes from get_market_price()
// Inputs:   symbol - the symbol of the stock
//          quantity - Some number of shares (fractional permitted)
// Returns:  (float) - Value of the sale (always positive or 0)
//          0 if an error occured
float calculate_sale_value(char *symbol, float quantity) {
    float sale_value;
    
    // Get the market price
    float price = get_market_price(symbol);
    
    // If price is invalid, return 0
    if (price == -1) {
        return 0;
    }
    
    // Calculate sale value
    sale_value = price * quantity;
    
    // If sale value is negative or zero, return 0
    if (sale_value <= 0) {
        return 0;
    }
    
    return sale_value;
}