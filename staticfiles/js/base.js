document.querySelectorAll('[data-verify="static-ok"]').forEach(link => {
    fetch(link.href)
        .then(response => {
            if (!response.ok) {
                console.error(`Static file failed to load: ${link.href}`);
                link.disabled = true;
            }
        })
        .catch(error => console.error('Static file check error:', error));
});