import hashlib
import json
import os

CACHE_FILE = "storage/cache_index.json"


def load_cache():
    # If file doesn't exist → return empty cache
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            content = f.read().strip()

            # If file is empty → return empty dict
            if not content:
                return {}

            return json.loads(content)

    except Exception:
        # If JSON is corrupted → reset safely
        return {}


def save_cache(cache):
    os.makedirs("storage", exist_ok=True)

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def generate_cache_key(prev_layer, instruction, workdir, env, extra=""):
    key_data = f"{prev_layer}-{instruction}-{workdir}-{env}-{extra}"
    return hashlib.sha256(key_data.encode()).hexdigest()


def get_cached_layer(cache_key):
    cache = load_cache()
    return cache.get(cache_key)


def store_cache(cache_key, layer_digest):
    cache = load_cache()
    cache[cache_key] = layer_digest
    save_cache(cache)