document.documentElement.classList.add("motion-enabled");

(() => {
    const EXIT_DURATION = 160;
    let navigating = false;

    function prefersReducedMotion() {
        return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    function smoothNavigate(url) {
        if (!url || navigating) return;

        if (prefersReducedMotion()) {
            window.location.href = url;
            return;
        }

        navigating = true;
        document.documentElement.classList.add("motion-leaving");
        window.setTimeout(() => {
            window.location.href = url;
        }, EXIT_DURATION);
    }

    function smoothBack() {
        if (navigating) return;
        if (prefersReducedMotion()) {
            window.history.back();
            return;
        }

        navigating = true;
        document.documentElement.classList.add("motion-leaving");
        window.setTimeout(() => window.history.back(), EXIT_DURATION);
    }

    function replayMotion(element) {
        if (!element || prefersReducedMotion()) return;
        element.classList.remove("motion-panel-enter");
        void element.offsetWidth;
        element.classList.add("motion-panel-enter");
    }

    window.smoothNavigate = smoothNavigate;
    window.smoothBack = smoothBack;
    window.replayMotion = replayMotion;

    document.addEventListener("DOMContentLoaded", () => {
        requestAnimationFrame(() => {
            document.documentElement.classList.add("motion-ready");
        });

        document.addEventListener("click", (event) => {
            const link = event.target.closest("a[href]");
            if (!link || event.defaultPrevented || event.button !== 0) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            if (link.target === "_blank" || link.hasAttribute("download")) return;

            const target = new URL(link.href, window.location.href);
            if (target.origin !== window.location.origin) return;
            if (target.pathname === window.location.pathname && target.hash) return;

            event.preventDefault();
            smoothNavigate(target.href);
        });
    });

    window.addEventListener("pageshow", () => {
        navigating = false;
        document.documentElement.classList.remove("motion-leaving");
        requestAnimationFrame(() => document.documentElement.classList.add("motion-ready"));
    });
})();
