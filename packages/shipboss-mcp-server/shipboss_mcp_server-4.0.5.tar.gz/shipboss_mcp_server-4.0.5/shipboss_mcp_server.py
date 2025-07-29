#!/usr/bin/env python
"""
ShipBoss MCP Server – v4.0.5
• Uses official FastMCP SDK (≥1.2.0)
• Inline schemas handled by SDK; no manual JSON-RPC plumbing
• Parcel + freight endpoints
• Fixed logging configuration to use stderr
• Fixed dotenv dependency conflicts
"""

from __future__ import annotations
import os, asyncio, time, logging, typing as t, sys
import httpx
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP          # <-- only FastMCP

# Load environment variables from .env file
load_dotenv()

# ───────── config ─────────
API_TOKEN = os.getenv("SHIPBOSS_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Set SHIPBOSS_API_TOKEN env-var")

BASE_URL  = "https://ship.shipboss.io/api/public/v1"
TIMEOUT   = 20
MAX_RETRY = 3

# Configure logging to stderr explicitly to avoid interfering with stdio JSON-RPC
def setup_logging():
    """Setup logging configuration for MCP server"""
    # Clear any existing handlers to ensure clean slate
    logging.getLogger().handlers.clear()
    
    # Configure logging with explicit stderr output
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        stream=sys.stderr,  # Explicitly use stderr to avoid stdout interference
        force=True  # Override any existing configuration
    )
    
    # Ensure no handlers are writing to stdout
    for handler in logging.root.handlers:
        if hasattr(handler, 'stream') and handler.stream == sys.stdout:
            handler.stream = sys.stderr

mcp = FastMCP("shipboss")        # instance used for @mcp.tool()

# ───────── helper ─────────
async def post(endpoint: str, body: dict) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Authorization": f"Bearer {API_TOKEN}",
               "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(1, MAX_RETRY + 1):
            resp = await client.post(url, json=body, headers=headers)
            if resp.status_code == 429:
                await asyncio.sleep(int(resp.headers.get("Retry-After", "1")) or 1)
                continue
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "success":
                return data["data"]
            raise RuntimeError(data.get("message", "ShipBoss API error"))
        raise RuntimeError("Exhausted retries")

# ───────── helper functions ─────────
def parse_address(address_string: str) -> dict:
    """Parse a simple address string into components.
    Supports two formats:
    1. 'Street, City, State ZIP, Country' (e.g., '123 Main St, New York, NY 10001, US')
    2. 'Street, City, State, ZIP, Country' (e.g., '10 cottage ave, long branch, NJ, 07740, US')
    
    Country code is REQUIRED (US, CA, etc.)
    """
    parts = [p.strip() for p in address_string.split(',')]
    
    if len(parts) < 4:
        raise ValueError("Address must include country code: 'Street, City, State ZIP, Country' (e.g., '123 Main St, New York, NY 10001, US')")
    
    # Extract basic components
    street = parts[0]
    city = parts[1]
    
    # Handle different formats
    if len(parts) == 4:
        # Format: 'Street, City, State ZIP, Country'
        state_zip = parts[2].strip().split()
        if len(state_zip) < 1:
            raise ValueError("State/Province is required")
        
        state = state_zip[0]
        zip_code = state_zip[1] if len(state_zip) > 1 else ""
        country = parts[3].strip().upper()
        
    elif len(parts) >= 5:
        # Format: 'Street, City, State, ZIP, Country'
        state = parts[2].strip()
        zip_code = parts[3].strip()
        country = parts[4].strip().upper()
        
    else:
        raise ValueError("Invalid address format")
    
    # Validate required fields
    if not state:
        raise ValueError("State/Province is required")
    if not country:
        raise ValueError("Country code is required (e.g., 'US', 'CA', 'MX')")
    
    # Validate common country codes
    valid_countries = ['US', 'CA', 'MX', 'GB', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE', 'CH', 'AT', 'DK', 'SE', 'NO', 'FI', 'PL', 'CZ']
    if country not in valid_countries:
        # Don't fail, just warn via the country field - ShipBoss API will validate
        pass
    
    return {
        "address_1": street,
        "city": city,
        "state": state,
        "zip": zip_code,
        "country": country
    }

def auto_detect_package_type(weight: float, length: float | None, width: float | None, height: float | None) -> str:
    """Auto-detect best package type based on dimensions and weight"""
    length = length or 0
    width = width or 0
    height = height or 0
    max_dim = max(length, width, height)
    
    if weight <= 0.5 and max_dim <= 12:
        return "ENVELOPE"
    elif weight <= 1 and max_dim <= 15:
        return "PAK"
    elif max_dim <= 8:
        return "BOX_SM"
    elif max_dim <= 12:
        return "BOX_MD"
    elif max_dim <= 18:
        return "BOX_LG"
    elif max_dim <= 24:
        return "BOX_XL"
    else:
        return "CUSTOMER_PACKAGING"

# ───────── service name helpers ─────────
def _normalize_service_name(carrier: str, svc: str) -> str:
    """Translate common shorthand service aliases into the exact names expected
    by the ShipBoss API so that end-users can pass convenient values like
    "GROUND" instead of "UPS Ground".
    """
    lookup = {
        "UPS": {
            "GROUND": "UPS Ground",
            "EXPRESS": "UPS Worldwide Express",
            "2DAY": "UPS Second Day Air",
            "NEXT_DAY": "UPS Next Day Air"
        },
        "FedEx": {
            "GROUND": "FedEx Ground",
            "HOME_DELIVERY": "FedEx Home Delivery",
            "2DAY": "FedEx 2Day",
            "OVERNIGHT": "FedEx Priority Overnight"
        },
        "DHL": {
            "EXPRESS_WORLDWIDE": "Express Worldwide"
        }
    }

    # Exact match first (case sensitive). If already correct, just return.
    if carrier in lookup and svc in lookup[carrier].values():
        return svc

    # Upper-case key for mapping, strip spaces/underscores for robustness
    key = svc.upper().replace(" ", "_")
    return lookup.get(carrier, {}).get(key, svc)  # fall back to original

# ───────── tools ─────────
@mcp.tool()
async def ping() -> dict:
    """Health-check: returns {'ok': true}"""
    return {"ok": True}

@mcp.tool()
async def get_parcel_rates(
    origin: str, 
    destination: str, 
    weight_pounds: float, 
    ship_date: str,
    dimensions_inches: list[float] | None = None,
    package_type: str | None = None
) -> dict:
    """Get parcel shipping rates.
    
    Args:
        origin: Origin address as string (e.g. "123 Main St, New York, NY 10001, US")
        destination: Destination address as string (e.g. "456 Oak Ave, Los Angeles, CA 90210, US") 
        weight_pounds: Package weight in pounds
        ship_date: Ship date in YYYY-MM-DD format
        dimensions_inches: Optional [length, width, height] in inches
        package_type: Optional package type (ENVELOPE, BOX_SM, BOX_MD, BOX_LG, BOX_XL, PAK, CUSTOMER_PACKAGING)
    """
    # Parse addresses
    from_addr = parse_address(origin)
    to_addr = parse_address(destination)
    
    # Build package data
    package = {"weight": weight_pounds, "quantity": 1}
    if dimensions_inches:
        if len(dimensions_inches) >= 3:
            package["length"] = dimensions_inches[0]
            package["width"] = dimensions_inches[1] 
            package["height"] = dimensions_inches[2]
    
    # Build request data
    data = {
        "addresses": {"from": from_addr, "to": to_addr},
        "packages": [package],
        "ship_date": ship_date
    }
    
    # Auto-detect or use provided package type
    if package_type:
        data["package_type"] = package_type
    else:
        length = dimensions_inches[0] if dimensions_inches and len(dimensions_inches) > 0 else None
        width = dimensions_inches[1] if dimensions_inches and len(dimensions_inches) > 1 else None
        height = dimensions_inches[2] if dimensions_inches and len(dimensions_inches) > 2 else None
        data["package_type"] = auto_detect_package_type(weight_pounds, length, width, height)
    
    return await post("get-rates", data)

@mcp.tool()
async def create_parcel_label(
    origin: str,
    destination: str, 
    weight_pounds: float,
    ship_date: str,
    carrier: Literal["FedEx", "UPS", "DHL"],
    service_name: str,
    dimensions_inches: list[float] | None = None,
    package_type: str | None = None,
    label_type: str = "PDF",
    **extra_data
) -> dict:
    """Create parcel shipping label.
    
    Args:
        origin: Origin address as string (e.g. "123 Main St, New York, NY 10001, US")
        destination: Destination address as string (e.g. "456 Oak Ave, Los Angeles, CA 90210, US")
        weight_pounds: Package weight in pounds
        ship_date: Ship date in YYYY-MM-DD format
        carrier: Shipping carrier (FedEx, UPS, or DHL)
        service_name: Service level (e.g. "GROUND", "EXPRESS", "2DAY")
        dimensions_inches: Optional [length, width, height] in inches
        package_type: Optional package type (ENVELOPE, BOX_SM, BOX_MD, BOX_LG, BOX_XL, PAK, CUSTOMER_PACKAGING)
        label_type: Label format (PDF, FOUR_BY_SIX, FOUR_BY_SIX_DOC_TAB)
        from_* / to_* keyword args: Use prefixes ``from_`` and ``to_`` to provide
            contact fields that belong to the sender or recipient address,
            e.g. ``from_name``, ``from_phone``, ``to_contact_name``, ``to_email``.
            These will automatically be merged into the corresponding address
            objects before the request is sent to ShipBoss.
    """
    # Parse addresses
    from_addr = parse_address(origin)
    to_addr = parse_address(destination)
    
    # Build package data
    package = {"weight": weight_pounds, "quantity": 1}
    if dimensions_inches:
        if len(dimensions_inches) >= 3:
            package["length"] = dimensions_inches[0]
            package["width"] = dimensions_inches[1]
            package["height"] = dimensions_inches[2]
    
    # Build request data
    data = {
        "addresses": {"from": from_addr, "to": to_addr},
        "packages": [package],
        "ship_date": ship_date,
        "carrier": carrier,
        # Translate common shorthand service markers (e.g., "GROUND") to the
        # exact service names expected by ShipBoss.
        "service_name": _normalize_service_name(carrier, service_name),
        "label_type": label_type,
    }

    # Backward-compatibility: if caller passed a single JSON string via parameter
    # named ``extra_data`` (common misunderstanding), parse it so that its keys
    # participate in the enrichment/merge logic below.
    if isinstance(extra_data.get("extra_data"), str):
        try:
            import json
            parsed_extra = json.loads(extra_data.pop("extra_data"))
            extra_data.update(parsed_extra)
        except Exception:
            # Ignore parsing errors – let raw string go through as was before
            pass

    # ── enrich addresses with contact details supplied via **extra_data ──
    # Accept keyword arguments prefixed with ``from_`` or ``to_`` to populate
    # the corresponding address dictionaries. Example:
    # create_parcel_label(..., from_name="Sarah", from_phone="2125550123", to_name="John", to_phone="3105550456")
    from_extras: dict[str, t.Any] = {}
    to_extras: dict[str, t.Any] = {}

    # Collect and strip the prefix so that e.g. ``from_name`` -> {"name": ...}
    for key, value in list(extra_data.items()):  # list() so we can mutate extra_data
        if key.startswith("from_"):
            attr = key[len("from_"):]
            from_extras[attr] = value
            extra_data.pop(key)
        elif key.startswith("to_"):
            attr = key[len("to_"):]
            to_extras[attr] = value
            extra_data.pop(key)

    # Merge into parsed address dicts
    from_addr.update(from_extras)
    to_addr.update(to_extras)

    # ShipBoss create-label endpoint requires at minimum a phone number and either
    # ``name`` or ``contact_name`` on both sender & recipient records. To reduce
    # friction during early testing, provide sensible defaults if the caller did
    # not supply them. These defaults should be overridden in production usage.
    def ensure_minimum_fields(addr: dict, role: str) -> None:
        if not (addr.get("name") or addr.get("contact_name")):
            addr["name"] = f"{role.title()} Name"
        if not addr.get("phone"):
            addr["phone"] = "0000000000"

    ensure_minimum_fields(from_addr, "sender")
    ensure_minimum_fields(to_addr, "recipient")

    # Auto-detect or use provided package type
    if package_type:
        data["package_type"] = package_type
    else:
        length = dimensions_inches[0] if dimensions_inches and len(dimensions_inches) > 0 else None
        width = dimensions_inches[1] if dimensions_inches and len(dimensions_inches) > 1 else None
        height = dimensions_inches[2] if dimensions_inches and len(dimensions_inches) > 2 else None
        data["package_type"] = auto_detect_package_type(weight_pounds, length, width, height)

    # Merge extra data
    data.update(extra_data)

    return await post("create-label", data)

@mcp.tool()
async def track_parcel(carrier: Literal["FedEx", "UPS", "DHL"], tracking_number: str) -> dict:
    """Track parcel shipment.
    
    Args:
        carrier: Shipping carrier (FedEx, UPS, or DHL)
        tracking_number: Package tracking number
    """
    data = {
        "carrier": carrier,
        "tracking_number": tracking_number
    }
    return await post("track", data)

# ───────── additional parcel tools ─────────
@mcp.tool()
async def create_pickup(
    origin: str,
    pickup_date: str,
    ready_time: str,
    close_time: str,
    carrier: Literal["FedEx", "UPS", "DHL"],
    quantity: int,
    total_weight: float,
    pickup_service_name: str | None = None,
    package_type: str | None = None,
    pickup_destination_country: str | None = None,
    test: bool | None = None,
    **extra_data
) -> dict:
    """Create a pickup to a given location.

    Args:
        origin: Pickup address as string (e.g. "123 Main St, New York, NY 10001, US")
        pickup_date: YYYY-MM-DD pickup date
        ready_time: HH:MM time the packages are ready
        close_time: HH:MM latest pickup time
        carrier: Carrier performing pickup (FedEx, UPS, DHL)
        quantity: Number of packages
        total_weight: Total weight in pounds
        pickup_service_name: Optional service name (required for UPS/FedEx)
        package_type: Optional package type (UPS only – Package or Letter)
        pickup_destination_country: Optional destination country code (UPS only)
        test: When true, use ShipBoss sandbox environment
    """
    data: dict[str, t.Any] = {
        "address": parse_address(origin),
        "pickup_date": pickup_date,
        "ready_time": ready_time,
        "close_time": close_time,
        "carrier": carrier,
        "quantity": quantity,
        "total_weight": total_weight,
    }

    # Optional fields
    if pickup_service_name:
        data["pickup_service_name"] = pickup_service_name
    if package_type:
        data["package_type"] = package_type
    if pickup_destination_country:
        data["pickup_destination_country"] = pickup_destination_country
    if test is not None:
        data["test"] = test

    # Merge extra data
    data.update(extra_data)

    return await post("create-pickup", data)


@mcp.tool()
async def cancel_pickup(
    carrier: Literal["FedEx", "UPS", "DHL"],
    confirmation_number: str,
    test: bool | None = None
) -> dict:
    """Cancel an existing pickup.

    Args:
        carrier: Carrier that was scheduled (FedEx, UPS, DHL)
        confirmation_number: Confirmation / pickup ID to cancel
        test: When true, use ShipBoss sandbox environment
    """
    data: dict[str, t.Any] = {
        "carrier": carrier,
        "confirmation_number": confirmation_number,
    }
    if test is not None:
        data["test"] = test

    return await post("cancel-pickup", data)

# ───────── freight tools ─────────
@mcp.tool()
async def get_freight_rates(
    origin: str,
    destination: str,
    weight_pounds: float,
    length_inches: float,
    width_inches: float,
    height_inches: float,
    quantity: int,
    commodity: str,
    freight_class: float,
    package_type: Literal["PLT", "CTN", "CRT", "DRM", "CON", "BDL", "CYL", "OTH"] = "PLT",
    ship_date: str | None = None,
    test: bool | None = None
) -> dict:
    """Get freight shipping rates.

    Args:
        origin: Origin address as string (domestic – e.g. "3500 Sunset Ave, Ocean, NJ, 07712, US")
        destination: Destination address as string (domestic)
        weight_pounds: Weight of a single freight piece
        length_inches: Length in inches
        width_inches: Width in inches
        height_inches: Height in inches
        quantity: Number of identical freight pieces
        commodity: Description of the goods
        freight_class: NMFC freight class (e.g. 60, 85, 125)
        package_type: Freight package type (default PLT)
        ship_date: Optional pickup date in YYYY-MM-DD format
        test: When true, use ShipBoss sandbox environment
    """
    from_addr = parse_address(origin)
    to_addr = parse_address(destination)

    package: dict[str, t.Any] = {
        "weight": weight_pounds,
        "length": length_inches,
        "width": width_inches,
        "height": height_inches,
        "quantity": quantity,
        "commodity": commodity,
        "freight_class": freight_class,
    }

    data: dict[str, t.Any] = {
        "addresses": {"from": from_addr, "to": to_addr},
        "packages": [package],
        "package_type": package_type,
    }
    if ship_date:
        data["pickup"] = {"date": ship_date}
    if test is not None:
        data["test"] = test

    return await post("get-freight-rates", data)


@mcp.tool()
async def create_freight_label(
    quote_id: str,
    sender_phone: str | None = None,
    receiver_phone: str | None = None,
    pickup_ready_time: str | None = None,
    pickup_close_time: str | None = None,
    delivery_date: str | None = None,
    delivery_ready_time: str | None = None,
    delivery_close_time: str | None = None,
    label_email_recipient: Literal["SENDER", "RECEIVER", "CUSTOM"] | None = None,
    custom_email_address: str | None = None,
    **extra_data
) -> dict:
    """Create a freight shipping label from a previously obtained quote_id.

    Args:
        quote_id: Quote identifier returned by get_freight_rates
        sender_phone: Optional sender phone number (overrides data from rates request)
        receiver_phone: Optional receiver phone
        pickup_ready_time: Optional pickup ready HH:MM
        pickup_close_time: Optional pickup close HH:MM
        delivery_date: Optional delivery window date YYYY-MM-DD
        delivery_ready_time: Optional delivery ready HH:MM
        delivery_close_time: Optional delivery close HH:MM
        label_email_recipient: Where to email label (SENDER, RECEIVER, CUSTOM)
        custom_email_address: Email for CUSTOM recipient
    """
    data: dict[str, t.Any] = {
        "quote_id": quote_id,
    }

    # Optional nested structures
    if pickup_ready_time or pickup_close_time:
        data["pickup"] = {}
        if pickup_ready_time:
            data["pickup"]["ready_time"] = pickup_ready_time
        if pickup_close_time:
            data["pickup"]["close_time"] = pickup_close_time

    if delivery_date or delivery_ready_time or delivery_close_time:
        data["delivery_window"] = {}
        if delivery_date:
            data["delivery_window"]["date"] = delivery_date
        if delivery_ready_time:
            data["delivery_window"]["ready_time"] = delivery_ready_time
        if delivery_close_time:
            data["delivery_window"]["close_time"] = delivery_close_time

    if label_email_recipient:
        data["label_email_recipient"] = label_email_recipient
        if label_email_recipient == "CUSTOM" and custom_email_address:
            data["custom_email_address"] = custom_email_address

    # Optional address phones – cannot parse full address here because quote already has them
    if sender_phone or receiver_phone:
        data["addresses"] = {}
        if sender_phone:
            data["addresses"]["from"] = {"phone": sender_phone}
        if receiver_phone:
            data.setdefault("addresses", {}).setdefault("to", {})["phone"] = receiver_phone

    # Merge extra data
    data.update(extra_data)

    return await post("create-freight-label", data)


@mcp.tool()
async def track_freight(tracking_number: str, test: bool | None = None) -> dict:
    """Track a freight shipment by tracking number.

    Args:
        tracking_number: Freight tracking number
        test: When true, use ShipBoss sandbox environment
    """
    data: dict[str, t.Any] = {"tracking_number": tracking_number}
    if test is not None:
        data["test"] = test

    return await post("track-freight", data)

# ───────── main ─────────
def main() -> None:
    """Entry point for the shipboss-mcp-server console script."""
    setup_logging()  # Configure logging to stderr
    
    # Ensure stdout/stderr are properly flushed before starting JSON-RPC
    # This prevents any leftover pip installation output from interfering
    sys.stdout.flush()
    sys.stderr.flush()
    
    # Ensure we're in a clean state for JSON-RPC communication
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout.buffer.flush()
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr.buffer.flush()
    
    mcp.run(transport="stdio")     # SDK handles JSON-RPC/stdio

if __name__ == "__main__":
    main()
