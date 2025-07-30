from playwright.async_api import async_playwright

async def launch_browser_context(browser_context_config: dict):
    print(f"Launching browser with config: {browser_context_config}")  # Debugging

    playwright = await async_playwright().start()

    mode = browser_context_config.get('mode', 'cdp')  # Default to cdp

    if mode == 'cdp':
        cdp_url = browser_context_config.get('cdp_url', 'http://localhost:9222')

        if not cdp_url.startswith("http://") and not cdp_url.startswith("ws://"):
            cdp_url = f"http://{cdp_url}"

        print(f"Connecting over CDP to {cdp_url}")
        browser = await playwright.chromium.connect_over_cdp(cdp_url)

        if not browser.contexts:
            raise Exception(f"No browser contexts found at {cdp_url}. Is Chrome running with remote debugging?")

        context = browser.contexts[0]
        return context

    elif mode == 'launch':
        launch_options = browser_context_config.get('launch_options', {})
        print(f"Launching new Chromium browser with options: {launch_options}")
        browser = await playwright.chromium.launch(**launch_options)
        context_options = browser_context_config.get('context_options', {})
        context = await browser.new_context(**context_options)
        return context

    else:
        raise Exception("🚫 Only 'cdp' and 'launch' modes are supported in the packaged binary. Make sure you are passing --browser-mode cdp or launch and providing browser_context in the HTTP request.")