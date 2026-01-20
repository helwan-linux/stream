# Drop-in Resource Saver Layer
# Does not modify your original code

RESOURCE_SAVER = True

def apply_engine_saver(engine):
    if not RESOURCE_SAVER:
        return engine

    # --- attach search cache ---
    engine._search_cache = {}

    original_search = engine.search
    def cached_search(query, platform="All"):
        key = (query, platform)
        if key in engine._search_cache:
            return engine._search_cache[key]
        result = original_search(query, platform)
        engine._search_cache[key] = result
        return result
    engine.search = cached_search

    # --- simplify stream url ---
    original_get_stream = engine.get_stream_url
    def single_try_stream(url, requested_quality="best"):
        return original_get_stream(url, requested_quality)
    engine.get_stream_url = single_try_stream

    return engine


def apply_ui_saver(window):
    if not RESOURCE_SAVER:
        return window

    import time
    window._last_update = 0
    original_update = window.update_progress

    def throttled_update(percent, speed):
        now = time.time()
        if now - window._last_update < 0.2:
            return
        window._last_update = now
        original_update(percent, speed)

    window.update_progress = throttled_update
    return window

