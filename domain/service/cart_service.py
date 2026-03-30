import logging

from shared.log.logger import REQUEST_ID_CTX
from a2a.envelope import A2AEnvelope

from infrastructure.adapter.http_client import send_message
from infrastructure.config.config import settings

from opentelemetry import trace

#---------------------------------
# Configure logging
#---------------------------------
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

WINDOWSIZE=settings.WINDOWSIZE

#---------------------------------
def _get_sub_agent_url(sub_agent: dict) -> str | None:
    supported_interfaces = sub_agent.get("supportedInterfaces", []) if isinstance(sub_agent, dict) else []
    if supported_interfaces:
        first_interface = supported_interfaces[0]
        if isinstance(first_interface, dict):
            return first_interface.get("url")

    return sub_agent.get("url") if isinstance(sub_agent, dict) else None

#---------------------------------
def cart_price_analysis(registry, product: dict) -> dict:
    with tracer.start_as_current_span("domain.service.cart_price_analysis"):
        logger.info("def.cart_price_analysis()")    

        print("------------------------------------")
        print(product)
        print("------------------------------------")

        if not product:
            logger.warning("No values enough provided for inventory inference.")
            return "false"
        
        headers = {"Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-Request-ID": REQUEST_ID_CTX.get()}

        data = []
        for item in product:
            sku = item.get("sku")
            if not sku:
                continue

            # -----------------------------------------------------
            # check and get the cart item data (service cart-item) 
            res_cart_item_window = send_message(f"{settings.URL_SERVICE_00}/cartItem/list/product?sku={sku}&window={WINDOWSIZE}",
                method="GET",
                headers=headers,
                timeout=settings.REQUEST_TIMEOUT)

            raw_items = res_cart_item_window.get("data", []) if isinstance(res_cart_item_window.get("data"), dict) else res_cart_item_window
            if isinstance(raw_items, dict):
                raw_items = raw_items.get("data", [])

            cart_quantities = []
            cart_prices = []

            for item in raw_items:
                quantity = item.get("quantity") if isinstance(item, dict) else getattr(item, "quantity", None)
                if quantity is not None:
                    cart_quantities.append(quantity)
                price = item.get("price") if isinstance(item, dict) else getattr(item, "price", None)
                if price is not None:
                    cart_prices.append(price)

            print("-------------quantities-----------------------")
            print(cart_quantities)
            print("-------------prices-----------------------")
            print(cart_prices)
            print("-------------prices-----------------------")

            # Calculate the PRICE stats using a2a stat
            sub_agent = registry.get("py-stat-inference-a2a.localhost")
            sub_agent_host = _get_sub_agent_url(sub_agent)
            sub_agent_name = sub_agent["name"]
            sub_agent_msg_type = "COMPUTE_STAT"
            
            envelope = A2AEnvelope(
                source_agent=settings.APP_NAME,
                target_agent=sub_agent_name,
                message_type=sub_agent_msg_type,
                payload={
                    "data": cart_prices,
                }
            )
            
            prices_stats = send_message(sub_agent_host,
                method="POST",
                headers=headers,
                body=envelope.model_dump() if hasattr(envelope, "model_dump") else envelope.dict(),
                timeout=settings.REQUEST_TIMEOUT)
            
            # extract features
            price_n_slope = (
                prices_stats.get("data", {})
                .get("payload", {})
                .get("data", {})
                .get("n_slope")
            ) if isinstance(prices_stats, dict) else None

            price_mean = (
                prices_stats.get("data", {})
                .get("payload", {})
                .get("data", {})
                .get("mean")
            ) if isinstance(prices_stats, dict) else None

            #------------------------------------------------------
            # Calculate the QUANTITY stats using a2a stat
            envelope = A2AEnvelope(
                source_agent=settings.APP_NAME,
                target_agent=sub_agent_name,
                message_type=sub_agent_msg_type,
                payload={
                    "data": cart_quantities,
                }
            )

            quantities_stats = send_message(sub_agent_host,
                method="POST",
                headers=headers,
                body=envelope.model_dump() if hasattr(envelope, "model_dump") else envelope.dict(),
                timeout=settings.REQUEST_TIMEOUT)
            
            quantity_n_slope = (
                quantities_stats.get("data", {})
                .get("payload", {})
                .get("data", {})
                .get("n_slope")
            ) if isinstance(quantities_stats, dict) else None

            quantity_mean = (
                quantities_stats.get("data", {})
                .get("payload", {})
                .get("data", {})
                .get("mean")
            ) if isinstance(quantities_stats, dict) else None

            #------------------------------------------------------

            if price_n_slope < -0.8 and quantity_n_slope > 0.8:
                action = "INCREASING PRICE"
            elif price_n_slope < -0.8 and quantity_n_slope < -0.8:
                action = "STOP SALES 10(MINUTES) - CHECK QUALITY"
            elif price_n_slope > 0.8 and quantity_n_slope > 0.8:
                action = "STOP SALES 10(MINUTES) - RUNOUT RISK"
            else:
                action = "STEADY PRICE"

            result = {
                "sku": sku,
                "action": action,
                "metadata": {  
                    "price_mean": price_mean,
                    "price_n_slope": price_n_slope,
                    "quantity_mean": quantity_mean,
                    "quantity_n_slope": quantity_n_slope,
                    "cart_quantities": cart_quantities,
                    "cart_prices": cart_prices,
                }
            }

            data.append(result)

        return {"data": data}

