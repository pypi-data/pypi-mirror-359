"""
Refactored and efficient license management for Terraback CLI.
Centralized I/O, minimal repetition, maintainable structure, real-world tested.
"""

import os
import jwt
import json
import requests
import hashlib
import platform
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from cryptography.fernet import Fernet
import typer
import logging

# --- LOGGING ---
logger = logging.getLogger(__name__)

# --- CONSTANTS & PATHS ---
LICENSE_DIR = Path.home() / ".terraback"
LICENSE_PATH = LICENSE_DIR / "license.jwt"
TRIAL_PATH = LICENSE_DIR / "trial_info.json"
METADATA_PATH = LICENSE_DIR / "license_metadata.json"
VALIDATION_PATH = LICENSE_DIR / "license_validation.enc"
ENCRYPTION_KEY_PATH = LICENSE_DIR / ".validation_key"

TRIAL_DURATION_DAYS = 30

try:
    from terraback._build_info import BUILD_EDITION
except ImportError:
    BUILD_EDITION = "community"

API_BASE_URL = os.environ.get('TERRABACK_API_URL', 'https://jaejtnxq15.execute-api.us-east-1.amazonaws.com/prod')
ACTIVATION_ENDPOINT = f"{API_BASE_URL}/activate"
TRIAL_ACTIVATION_ENDPOINT = f"{API_BASE_URL}/v1/trial/activate"

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAl47KZZNZTWDLp2kD732a
5ijj4sXanQSiuRhIv5Bs9x8qNwSt4MvxYi0UU9OKfIftteITEPzwfDzRIxEdHJ97
HfN6qwlADHwnCK+88nvZjKkC767c4DpL56zltT4EnDEWLuNPRaXHiOswFyP5Gglw
Tgg7DUpMpSUnh/HpT93ZB6CajvSTn9vqZU8Y5n89QhHeTfdDpAfKTRtC4hsx/vk7
oSiEUUv+oi/WK5APJagqDDM/9/6J7zs4NCRGxy57JIFUM+rl1KKDn3/ht5oZ7eFl
AwLfRAoC4xjkRLslPIKuH4xp1KdpXzn2h2CC4izLytYh6vxQ70fjoa8VBuoXn8pd
0HkNRr67yvKsA1Y2YZH/QfKZvZS76Vg66p1rIajFpdTn6a79DRZ6V1NuX6a+/Hyy
DTzgjcsYKlwZUmYggerGT3HYeQitkTePkX6KFRwC62kF7MfFm0dNsJXBsK4IOvwY
WgGT01IS/NICEjedUgT04Lr8h2uC13V5ClkBrZpSUZFtzpsLXsaR4vy8jwwzZH2K
Ix95zMXEEF6ein5epVkRXlz7rDSbCxWAmE9Q8W4JLcFQrcOcKskzoN1bPtTXy30q
Ev5KTDWwxozgail7Cw8FgxjUD/LUYQX2xbRTObHsjwXKlOgCB6CYZkp9NhByU7xJ
aGFJVexH2FRpADyYw5Hx1ocCAwEAAQ==
-----END PUBLIC KEY-----"""

class Tier:
    COMMUNITY = "community"
    TRIAL = "trial"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ALL = [COMMUNITY, TRIAL, PROFESSIONAL, ENTERPRISE]

class ValidationSettings:
    OFFLINE_GRACE_DAYS = 14
    VALIDATION_INTERVAL_DAYS = 7
    MAX_OFFLINE_DAYS = 30

# --- UTILS ---
def _parse_api_gateway_response(resp: Dict[str, Any]) -> Dict[str, Any]:
    """Parse API Gateway proxy response format."""
    if 'body' in resp and isinstance(resp['body'], str):
        return json.loads(resp['body'])
    return resp

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _get_machine_fingerprint() -> str:
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> e) & 0xff) for e in range(0, 2*6, 2)][::-1])
    sysinfo = f"{platform.system()}-{platform.machine()}-{mac}"
    return hashlib.md5(sysinfo.encode()).hexdigest()

def _is_online() -> bool:
    urls = [API_BASE_URL, "https://api.github.com", "https://cloudflare.com", "https://google.com"]
    for url in urls:
        try:
            if requests.get(url, timeout=3).status_code < 500:
                return True
        except Exception:
            continue
    return False

def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text()) if path.exists() else None
    except Exception as e:
        logger.error(f"Failed to read JSON from {path}: {e}")
        return None

def _write_json(path: Path, data: Dict[str, Any]):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
    except Exception as e:
        logger.error(f"Failed to write JSON to {path}: {e}")
        raise

# --- ENCRYPTION ---
def _init_encryption():
    if ENCRYPTION_KEY_PATH.exists():
        with open(ENCRYPTION_KEY_PATH, 'rb') as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        ENCRYPTION_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(ENCRYPTION_KEY_PATH, 'wb') as f:
            f.write(key)
        os.chmod(ENCRYPTION_KEY_PATH, 0o600)
    return Fernet(key)

def _save_validation_data(data: Dict[str, Any]):
    try:
        cipher = _init_encryption()
        VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(VALIDATION_PATH, 'wb') as f:
            f.write(cipher.encrypt(json.dumps(data, default=str).encode()))
        os.chmod(VALIDATION_PATH, 0o600)
    except Exception as e:
        logger.error(f"Failed to save validation data: {e}")

def _load_validation_data() -> Optional[Dict[str, Any]]:
    if not VALIDATION_PATH.exists():
        return None
    try:
        cipher = _init_encryption()
        with open(VALIDATION_PATH, 'rb') as f:
            return json.loads(cipher.decrypt(f.read()).decode())
    except Exception as e:
        logger.error(f"Failed to load validation data: {e}")
        return None

# --- LICENSE/TRIAL HELPERS ---
def normalize_license_key(key: str) -> str:
    return key.upper().replace('-', '').replace(' ', '').strip()

def format_license_key(nkey: str) -> Optional[str]:
    return '-'.join([nkey[i:i+4] for i in range(0, 16, 4)]) if len(nkey) == 16 else None

def is_trial_expired(td: Dict[str, Any]) -> bool:
    try:
        return _now() > datetime.fromisoformat(td["end_date"])
    except Exception:
        return True

def get_trial_info() -> Optional[Dict[str, Any]]:
    td = _read_json(TRIAL_PATH)
    if td and td.get("machine_fingerprint") == _get_machine_fingerprint() and not is_trial_expired(td):
        td["days_remaining"] = max(0, (datetime.fromisoformat(td["end_date"]) - _now()).days)
        return td
    return None

def is_trial_active() -> bool:
    return bool(get_trial_info())

def get_license_info() -> Optional[Dict[str, Any]]:
    if LICENSE_PATH.exists():
        try:
            return _decode_and_validate(LICENSE_PATH.read_text().strip())
        except Exception:
            return None
    return None

def _decode_and_validate(jwt_token: str) -> Optional[Dict[str, Any]]:
    try:
        data = jwt.decode(jwt_token, PUBLIC_KEY, algorithms=["RS256"])
        if "tier" not in data or data["tier"] not in Tier.ALL:
            return None
        if 'exp' in data:
            try:
                data['expiry'] = datetime.fromtimestamp(data['exp']).strftime('%Y-%m-%d %H:%M:%S UTC')
            except Exception:
                data['expiry'] = 'Unknown'
        return data
    except jwt.ExpiredSignatureError:
        logger.debug("License has expired")
        return None
    except jwt.InvalidTokenError:
        logger.debug("Invalid license token")
        return None
    except Exception as e:
        logger.error(f"Failed to decode JWT: {e}")
        return None

# --- LICENSE/TRIAL API ENTRYPOINTS ---
def start_free_trial() -> bool:
    """Start a 30-day free trial with improved error handling."""
    # Enable debug logging if requested
    if os.environ.get('TERRABACK_DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
    
    trial_data = get_trial_info()
    if trial_data:
        typer.echo("Free trial is already active.")
        typer.echo(f"Days remaining: {trial_data.get('days_remaining', 0)}")
        return True
    
    if not _is_online():
        typer.secho("Error: Internet connection required to activate trial.", fg=typer.colors.RED)
        typer.echo("Please check your internet connection and try again.")
        typer.echo("\nTip: Set TERRABACK_DEBUG=1 environment variable for detailed connection logs")
        return False
    
    trial_id = str(uuid.uuid4())
    machine_fingerprint = _get_machine_fingerprint()
    payload = {"machine_fingerprint": machine_fingerprint, "trial_id": trial_id}
    
    # Debug logging
    logger.info(f"Machine fingerprint: {machine_fingerprint[:16]}...")
    logger.info(f"Payload: {payload}")
    
    try:
        typer.echo("Connecting to trial activation server...")
        logger.info(f"Sending request to {TRIAL_ACTIVATION_ENDPOINT}")
        
        # Add debug output in verbose mode
        if os.environ.get('TERRABACK_DEBUG'):
            typer.echo(f"Debug: Endpoint: {TRIAL_ACTIVATION_ENDPOINT}")
            typer.echo(f"Debug: Machine fingerprint: {machine_fingerprint[:16]}...")
            typer.echo(f"Debug: Payload: {json.dumps(payload, indent=2)}")
        
        resp = requests.post(
            TRIAL_ACTIVATION_ENDPOINT, 
            json=payload, 
            timeout=10, 
            headers={"Content-Type": "application/json", "User-Agent": f"Terraback-CLI/{BUILD_EDITION}"}
        )
        
        logger.info(f"Received response: {resp.status_code}")
        logger.debug(f"Response body: {resp.text[:500]}...")
        
        # Handle both direct responses and API Gateway proxy responses
        try:
            response_data = resp.json()
            
            # Check if this is an API Gateway proxy response with nested status
            if 'statusCode' in response_data and 'body' in response_data:
                actual_status = response_data['statusCode']
                data = _parse_api_gateway_response(response_data)
                
                # Override the HTTP status if proxy says it's an error
                if actual_status >= 400:
                    resp.status_code = actual_status
                    logger.info(f"API Gateway proxy returned status: {actual_status}")
            else:
                data = response_data
        except json.JSONDecodeError:
            typer.secho("Error: Server returned invalid JSON", fg=typer.colors.RED)
            logger.error(f"Invalid JSON response: {resp.text[:200]}")
            return False
        
        if resp.status_code == 200:
            raw_data = resp.json()
            data = _parse_api_gateway_response(raw_data)
            
            # Check if it's actually an error response
            if "error" in data:
                typer.secho(f"Error: {data.get('error', 'Unknown error')}", fg=typer.colors.RED)
                if "message" in data:
                    typer.echo(f"Details: {data['message']}")
                logger.error(f"Server returned error in 200 response: {data}")
                return False
            
            # Validate response data
            if "expires_at" not in data:
                typer.secho("Error: Invalid response from server (missing expiration date)", fg=typer.colors.RED)
                logger.error(f"Response missing expires_at: {data}")
                return False
            
            try:
                trial_end = datetime.fromisoformat(data["expires_at"])
            except (ValueError, TypeError) as e:
                typer.secho("Error: Invalid date format in server response", fg=typer.colors.RED)
                logger.error(f"Failed to parse expires_at: {data.get('expires_at')}: {e}")
                return False
            
            trial_data = {
                "trial_id": data.get("trial_id", trial_id),
                "machine_fingerprint": _get_machine_fingerprint(),
                "start_date": _now().isoformat(),
                "end_date": trial_end.isoformat(),
                "tier": Tier.TRIAL,
                "activated": True
            }
            
            _write_json(TRIAL_PATH, trial_data)
            typer.secho("✓ 30-day free trial activated!", fg=typer.colors.GREEN)
            typer.echo(f"Trial expires: {trial_end.strftime('%Y-%m-%d')}")
            return True
            
        elif resp.status_code == 409:
            data = _parse_api_gateway_response(resp.json())
            error_code = data.get("error", "unknown")
            message = data.get('message', 'Trial activation conflict')
            
            typer.secho(f"Trial activation failed: {message}", fg=typer.colors.YELLOW)
            
            if error_code == "trial_already_used":
                typer.echo("This machine has already used its free trial.")
            elif error_code == "active_license_exists":
                typer.echo("This machine already has an active license.")
            
            return False
            
        else:
            typer.secho(f"Error: Unable to activate trial (HTTP {resp.status_code})", fg=typer.colors.RED)
            
            # Try to parse error message
            try:
                error_data = _parse_api_gateway_response(resp.json())
                if "message" in error_data:
                    typer.echo(f"Server message: {error_data['message']}")
            except Exception:
                typer.echo(f"Server response: {resp.text[:200]}")
            
            return False
            
    except requests.exceptions.Timeout:
        typer.secho("Error: Connection to trial server timed out.", fg=typer.colors.RED)
        typer.echo("Please check your internet connection and try again.")
        return False
    except requests.exceptions.ConnectionError as e:
        typer.secho("Error: Could not connect to trial activation server.", fg=typer.colors.RED)
        typer.echo(f"Connection details: {str(e)[:200]}")
        return False
    except KeyError as e:
        typer.secho(f"Error: Invalid server response (missing field: {e})", fg=typer.colors.RED)
        logger.exception("KeyError during trial activation")
        return False
    except json.JSONDecodeError as e:
        typer.secho("Error: Server returned invalid JSON response", fg=typer.colors.RED)
        logger.error(f"JSON decode error: {e}")
        return False
    except Exception as ex:
        typer.secho(f"Unexpected error during trial activation: {type(ex).__name__}", fg=typer.colors.RED)
        logger.exception("Unexpected error during trial activation")
        typer.echo("Please try again or contact support if the issue persists.")
        return False

def activate_license(key: str) -> bool:
    """Activate a license with improved error handling."""
    key = key.strip()
    
    if not key:
        typer.secho("Error: License key cannot be empty", fg=typer.colors.RED)
        return False
    
    typer.echo("Contacting license server...")
    
    payload = {
        "license_key": key,
        "machine_fingerprint": _get_machine_fingerprint(),
        "platform": platform.system(),
        "hostname": platform.node()
    }
    
    trial_data = get_trial_info()
    if trial_data:
        payload.update({
            "from_trial": True, 
            "trial_id": trial_data.get("trial_id"), 
            "trial_end_date": trial_data.get("end_date")
        })
    
    try:
        resp = requests.post(
            ACTIVATION_ENDPOINT, 
            json=payload, 
            headers={"Content-Type": "application/json", "User-Agent": f"Terraback-CLI/{BUILD_EDITION}"}, 
            timeout=10
        )
        
        if resp.status_code == 200:
            data = _parse_api_gateway_response(resp.json())
            jwt_token = data.get('license_jwt') or data.get('jwt_token')
            
            if not jwt_token:
                typer.secho("Error: Invalid response from license server (no JWT token)", fg=typer.colors.RED)
                logger.error(f"No JWT in response: {data}")
                return False
            
            license_data = _decode_and_validate(jwt_token)
            if not license_data:
                typer.secho("Error: Failed to validate license token", fg=typer.colors.RED)
                return False
            
            LICENSE_PATH.parent.mkdir(parents=True, exist_ok=True)
            LICENSE_PATH.write_text(jwt_token)
            
            meta = {
                'email': license_data.get('email'),
                'expires_at': data.get('adjusted_expiry') or license_data.get('expiry'),
                'activated_at': datetime.utcnow().isoformat(),
                'friendly_key': format_license_key(normalize_license_key(key)),
                'effective_start': data.get('effective_start'),
                'from_trial': payload.get("from_trial"),
                'trial_id': payload.get("trial_id"),
            }
            _write_json(METADATA_PATH, meta)
            
            typer.secho("License activated successfully!", fg=typer.colors.GREEN, bold=True)
            if data.get("message"):
                typer.echo(data["message"])
            return True
            
        elif resp.status_code == 400:
            data = _parse_api_gateway_response(resp.json())
            error = data.get('error', 'Invalid license key format')
            typer.secho(f"Error: {error}", fg=typer.colors.RED)
            typer.echo("Please check your license key format (XXXX-XXXX-XXXX-XXXX)")
            return False
            
        elif resp.status_code == 403:
            data = _parse_api_gateway_response(resp.json())
            error = data.get('error', 'License validation failed')
            typer.secho(f"Error: {error}", fg=typer.colors.RED)
            return False
            
        elif resp.status_code == 404:
            typer.secho("Error: License key not found.", fg=typer.colors.RED)
            typer.echo("Please check that you've entered the correct key.")
            return False
            
        else:
            typer.secho(f"Error: Activation failed (HTTP {resp.status_code})", fg=typer.colors.RED)
            try:
                error_data = _parse_api_gateway_response(resp.json())
                if "message" in error_data:
                    typer.echo(f"Server message: {error_data['message']}")
            except Exception:
                pass
            return False
            
    except requests.exceptions.Timeout:
        typer.secho("Error: Connection to license server timed out.", fg=typer.colors.RED)
        typer.echo("Please check your internet connection and try again.")
        return False
    except requests.exceptions.ConnectionError:
        typer.secho("Error: Could not connect to license server.", fg=typer.colors.RED)
        typer.echo("Please check your internet connection and try again.")
        return False
    except Exception as e:
        typer.secho("License activation error.", fg=typer.colors.RED)
        logger.exception(f"Unexpected error: {e}")
        return False

# --- PERIODIC VALIDATION ---
def _check_clock_tampering(vdata: Optional[Dict[str, Any]]) -> bool:
    if not vdata:
        return False
    last_run = vdata.get('last_run')
    if last_run:
        try:
            diff = (datetime.fromisoformat(last_run) - datetime.utcnow()).total_seconds()
            return diff > 3600
        except Exception:
            pass
    return False

def _validate_online(license_key: str) -> Optional[Dict[str, Any]]:
    try:
        payload = {
            "license_key": license_key, 
            "machine_fingerprint": _get_machine_fingerprint(), 
            "validation_type": "periodic", 
            "timestamp": datetime.utcnow().isoformat()
        }
        resp = requests.post(
            ACTIVATION_ENDPOINT, 
            json=payload, 
            headers={"Content-Type": "application/json"}, 
            timeout=10
        )
        return _parse_api_gateway_response(resp.json()) if resp.status_code == 200 else None
    except Exception as e:
        logger.error(f"Online validation failed: {e}")
        return None

def _perform_periodic_validation() -> bool:
    vdata = _load_validation_data()
    now = datetime.utcnow()
    
    if _check_clock_tampering(vdata):
        if _is_online():
            meta = _read_json(METADATA_PATH)
            key = meta.get('friendly_key') if meta else None
            if key:
                srv = _validate_online(key)
                if srv:
                    vdata = {
                        'last_online_validation': now.isoformat(), 
                        'last_run': now.isoformat(), 
                        'validation_count': (vdata.get('validation_count', 0) + 1) if vdata else 1, 
                        'machine_fingerprint': _get_machine_fingerprint()
                    }
                    _save_validation_data(vdata)
                    return True
            typer.secho("Clock tampering detected. Please connect to internet for validation.", fg=typer.colors.YELLOW)
            return False
        typer.secho("Clock tampering detected. Internet connection required.", fg=typer.colors.RED)
        return False
    
    if not vdata:
        vdata = {
            'last_online_validation': now.isoformat(), 
            'last_run': now.isoformat(), 
            'validation_count': 0, 
            'machine_fingerprint': _get_machine_fingerprint()
        }
        _save_validation_data(vdata)
        return True
    
    try:
        last_online = datetime.fromisoformat(vdata['last_online_validation'])
        days_since = (now - last_online).days
    except Exception:
        days_since = ValidationSettings.MAX_OFFLINE_DAYS
    
    needs_validation = days_since >= ValidationSettings.VALIDATION_INTERVAL_DAYS
    if needs_validation:
        if _is_online():
            meta = _read_json(METADATA_PATH)
            key = meta.get('friendly_key') if meta else None
            if key and _validate_online(key):
                vdata.update({
                    'last_online_validation': now.isoformat(), 
                    'last_run': now.isoformat(), 
                    'validation_count': vdata.get('validation_count', 0) + 1
                })
                _save_validation_data(vdata)
                return True
            if days_since < ValidationSettings.OFFLINE_GRACE_DAYS:
                vdata['last_run'] = now.isoformat()
                _save_validation_data(vdata)
                typer.secho("License validation failed. Operating in grace period.", fg=typer.colors.YELLOW)
                return True
            typer.secho("License validation failed. Please check your license status.", fg=typer.colors.RED)
            return False
        if days_since >= ValidationSettings.MAX_OFFLINE_DAYS:
            typer.secho(f"License validation required. Maximum offline period ({ValidationSettings.MAX_OFFLINE_DAYS} days) exceeded.", fg=typer.colors.RED)
            return False
        elif days_since >= ValidationSettings.OFFLINE_GRACE_DAYS:
            typer.secho(f"Please connect to internet for license validation. Days remaining: {ValidationSettings.MAX_OFFLINE_DAYS - days_since}", fg=typer.colors.YELLOW)
        vdata['last_run'] = now.isoformat()
        _save_validation_data(vdata)
        return True
    
    vdata['last_run'] = now.isoformat()
    _save_validation_data(vdata)
    return True

# --- LICENSE STATE, DECORATORS & FEATURE CHECK ---
_license_cache = None
_license_checked = False

def get_active_license() -> Optional[Dict[str, Any]]:
    global _license_cache, _license_checked
    
    if is_trial_active():
        tinfo = get_trial_info()
        if tinfo:
            return {
                "tier": Tier.PROFESSIONAL, 
                "email": "Trial User", 
                "expiry": tinfo["end_date"], 
                "is_trial": True, 
                "days_remaining": tinfo["days_remaining"]
            }
    
    if _license_checked:
        if _license_cache and not _perform_periodic_validation():
            _license_cache = None
            _license_checked = False
            return None
        return _license_cache
    
    license_data = get_license_info()
    if license_data and _perform_periodic_validation():
        _license_cache = license_data
        _license_checked = True
        return license_data
    
    _license_cache = None
    _license_checked = True
    return None

def get_active_tier() -> str:
    if is_trial_active():
        return Tier.TRIAL
    if BUILD_EDITION.lower() != 'community':
        return BUILD_EDITION.lower()
    lic = get_active_license()
    if lic:
        return lic.get('tier', Tier.COMMUNITY)
    return Tier.COMMUNITY

def require_tier(required_tier: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tier = get_active_tier()
            allowed = {
                Tier.COMMUNITY: 0,
                Tier.TRIAL: 1,
                Tier.PROFESSIONAL: 1,
                Tier.ENTERPRISE: 2
            }
            if allowed.get(tier, -1) >= allowed.get(required_tier, 99):
                return func(*args, **kwargs)
            
            typer.secho(f"Error: This feature requires a '{required_tier.capitalize()}' license.", fg=typer.colors.RED, bold=True)
            typer.echo(f"Your current tier: {tier.capitalize()}")
            
            if required_tier in [Tier.PROFESSIONAL, Tier.TRIAL]:
                if not is_trial_active() and not TRIAL_PATH.exists():
                    typer.echo("Start your 30-day free trial: terraback trial start")
                else:
                    typer.echo("Upgrade at https://terraback.io/pricing")
            elif required_tier == Tier.ENTERPRISE:
                typer.echo("To upgrade, contact sales@terraback.io for Enterprise licensing.")
            else:
                typer.echo("To upgrade, visit https://terraback.io/pricing")
            
            typer.echo("Or use 'terraback license activate <key>' if you already have a license.")
            raise typer.Exit(code=1)
        return wrapper
    return decorator

require_professional = require_tier(Tier.PROFESSIONAL)
require_enterprise = require_tier(Tier.ENTERPRISE)
require_pro = require_professional

def check_feature_access(feature_tier: str) -> bool:
    allowed = {
        Tier.COMMUNITY: 0,
        Tier.TRIAL: 1,
        Tier.PROFESSIONAL: 1,
        Tier.ENTERPRISE: 2
    }
    return allowed.get(get_active_tier(), -1) >= allowed.get(feature_tier, 99)

def get_license_status() -> Dict[str, Any]:
    active_tier = get_active_tier()
    license_data = get_active_license()
    status = {
        'active_tier': active_tier,
        'has_license': license_data is not None or is_trial_active(),
        'license_valid': license_data is not None or is_trial_active(),
        'build_edition': BUILD_EDITION
    }
    
    if is_trial_active():
        trial_info = get_trial_info()
        if trial_info:
            status.update({
                'is_trial': True,
                'trial_id': trial_info.get("trial_id"),
                'expires': trial_info.get("end_date"),
                'days_remaining': trial_info.get("days_remaining", 0),
                'email': "Trial User",
                'tier': Tier.TRIAL,
            })
    elif license_data:
        status.update({
            'email': license_data.get('email'),
            'tier': license_data.get('tier'),
            'expires': license_data.get('expiry'),
            'order_id': license_data.get('order_id')
        })
        validation_data = _load_validation_data()
        if validation_data:
            try:
                last_online = datetime.fromisoformat(validation_data['last_online_validation'])
                days_since_online = (datetime.utcnow() - last_online).days
                status.update({
                    'days_since_online_validation': days_since_online,
                    'validation_count': validation_data.get('validation_count', 0),
                    'last_online_validation': validation_data.get('last_online_validation')
                })
            except (KeyError, ValueError):
                pass
        try:
            metadata = _read_json(METADATA_PATH)
            if metadata:
                status['friendly_key'] = metadata.get('friendly_key')
        except:
            pass
    else:
        status['can_start_trial'] = not bool(TRIAL_PATH.exists())
    
    return status

def force_license_refresh() -> bool:
    try:
        if not _is_online():
            typer.secho("Internet connection required for license refresh", fg=typer.colors.RED)
            return False
        
        metadata = _read_json(METADATA_PATH)
        if not metadata:
            typer.secho("No license found to refresh", fg=typer.colors.RED)
            return False
        
        license_key = metadata.get('friendly_key')
        if not license_key:
            typer.secho("Invalid license metadata", fg=typer.colors.RED)
            return False
        
        server_response = _validate_online(license_key)
        if server_response:
            current_time = datetime.utcnow()
            validation_data = _load_validation_data() or {}
            validation_data.update({
                'last_online_validation': current_time.isoformat(),
                'last_run': current_time.isoformat(),
                'validation_count': validation_data.get('validation_count', 0) + 1
            })
            _save_validation_data(validation_data)
            
            global _license_cache, _license_checked
            _license_cache = None
            _license_checked = False
            
            typer.secho("License refreshed successfully", fg=typer.colors.GREEN)
            return True
        else:
            typer.secho("License refresh failed - server validation unsuccessful", fg=typer.colors.RED)
            return False
    except Exception as e:
        typer.secho(f"Error during license refresh: {e}", fg=typer.colors.RED)
        return False

def get_validation_info() -> Dict[str, Any]:
    validation_data = _load_validation_data()
    current_time = datetime.utcnow()
    info = {
        'is_online': _is_online(),
        'current_time': current_time.isoformat(),
        'machine_fingerprint': _get_machine_fingerprint()[:8] + "...",
        'validation_settings': {
            'offline_grace_days': ValidationSettings.OFFLINE_GRACE_DAYS,
            'validation_interval_days': ValidationSettings.VALIDATION_INTERVAL_DAYS,
            'max_offline_days': ValidationSettings.MAX_OFFLINE_DAYS
        }
    }
    
    if validation_data:
        try:
            last_online = datetime.fromisoformat(validation_data['last_online_validation'])
            days_since_online = (current_time - last_online).days
            info.update({
                'last_online_validation': validation_data.get('last_online_validation'),
                'days_since_online': days_since_online,
                'validation_count': validation_data.get('validation_count', 0),
                'validation_status': 'valid' if days_since_online < ValidationSettings.MAX_OFFLINE_DAYS else 'expired'
            })
            if days_since_online >= ValidationSettings.VALIDATION_INTERVAL_DAYS:
                info['needs_validation'] = True
            if days_since_online >= ValidationSettings.OFFLINE_GRACE_DAYS:
                info['in_grace_period'] = True
        except (KeyError, ValueError):
            info['validation_data_error'] = True
    else:
        info['no_validation_data'] = True
    
    return info