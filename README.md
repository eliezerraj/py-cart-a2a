## py-cart-a2a
py-cart-a2a

## diagram

![alt text](image.png)
    
    cart a2a

    participant agent
    participant cart-a2a
    participant cart-item
    participant stat-a2a

    agent->cart-a2a:GET /.well-known/agent-card.json
    agent<--cart-a2a:http 200 (JSON)\nagent_card

    alt CART_PRICE_ANALYSIS
        agent->cart-a2a:POST: /a2a/message\n(CART_PRICE_ANALYSIS)
        cart-a2a->cart-item:GET /cartItem/list/product?sku={sku}&window={WINDOWSIZE}
        cart-a2a<--cart-item:http 200 (JSON)\nqueryData
        cart-a2a->stat-a2a:POST: /a2a/message\n(COMPUTE_STAT)
        cart-a2a<--stat-a2a:http 200 (JSON)\nstat data
        agent<--cart-a2a:http 200 (JSON)
    end

## Endpoint

    curl --location 'http://localhost:8001/a2a/message' \
    --header 'Content-Type: application/json' \
    --data '{
        "source_agent": "user-postman",
        "target_agent": "inventory-agent",
        "message_type": "CART_PRICE_ANALYSIS",
        "payload": {
            "product": [ 
                {
                "sku": "cheese-fr-6"
                }
            ]
        }
    }'