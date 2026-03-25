from infrastructure.config.config import settings

AGENT_CARD = {
    "name": settings.APP_NAME,
    "description": "Cart agent handles cart item management and optimization tasks, providing real-time insights and recommendations to ensure efficient pricing.",
    "version": settings.VERSION,
    "provider": {
        "organization": "eliezer-junior Org.",
        "url": settings.URL_AGENT,
    },
    "documentationUrl": f"{settings.URL_AGENT}/info",
    "supportedInterfaces": [
        {
            "url": f"{settings.URL_AGENT}/a2a/message",
            "protocolBinding": "HTTP+JSON",
            "protocolVersion": "1.0",
        }        
    ],
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False,
        "extendedAgentCard": False,
    },
    "defaultInputModes": ["application/json"],
    "defaultOutputModes": ["application/json"],
    "skills": [
        {
            "id": "CART_PRICE_ANALYSIS",
            "name": "Price Analysis",
            "description": "Analyzes product pricing and quantity trends from cart item history.",
            "tags": ["pricing", "analytics"],
            "inputSchema": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sku": { "type": "string" }
                            },
                            "required": ["sku"]
                        }
                    }
                },
                "required": ["product"]
            },
            "examples": {"product": [{"sku": "coffee-12"}]},
            "inputModes": ["application/json"],
            "outputModes": ["application/json"],
        }
    ]
}