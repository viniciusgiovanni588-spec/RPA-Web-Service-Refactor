const sidebarScrollTimeouts = new WeakMap();

document.querySelectorAll('.liquid-sidebar').forEach((sidebar) => {
    sidebar.addEventListener('scroll', () => {
        sidebar.classList.add('is-scrolling');
        clearTimeout(sidebarScrollTimeouts.get(sidebar));

        const timeout = setTimeout(() => {
            sidebar.classList.remove('is-scrolling');
            sidebarScrollTimeouts.delete(sidebar);
        }, 700);

        sidebarScrollTimeouts.set(sidebar, timeout);
    }, { passive: true});
});
