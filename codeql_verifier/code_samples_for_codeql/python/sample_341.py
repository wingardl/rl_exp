
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
    
    // Get the market price for the given symbol
    float market_price = get_market_price(symbol);
    
    // If an error occurred, return 0
    if (market_price == -1) {
        return 0.0f;
    }
    
    // Calculate the sale value
    sale_value = market_price * quantity;
    
    return sale_value;
}
