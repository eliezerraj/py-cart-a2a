# py-cart-a2a
py-cart-a2a

### Endpoint

    curl --location 'http://localhost:7100/a2a/message' \
    --header 'Content-Type: application/json' \
    --data '{
        "source_agent": "user-postman",
        "target_agent": "inventory-agent",
        "message_type": "PRICE_ANALYSIS",
        "payload": {
            "product": [ 
                {
                "sku": "coffee-100"
                },
                {
                "sku": "coffee-101"
                },
                {
                "sku": "coffee-102"
                },
                {
                "sku": "coffee-103"
                }
            ]
        }
    }'