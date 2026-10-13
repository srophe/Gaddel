(function () {
    const rotationInterval = 7000;

    function initializePartnerProjects() {
        const tile = document.getElementById('partner-projects');
        if (!tile || tile.dataset.rotationInitialized) {
            return;
        }

        const projects = Array.from(tile.querySelectorAll(':scope > .partner-project'));
        if (projects.length < 2) {
            return;
        }

        tile.dataset.rotationInitialized = 'true';
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        let currentIndex = 0;
        projects.forEach(function (project, index) {
            project.hidden = index !== currentIndex;
        });

        window.setInterval(function () {
            if (document.hidden || reducedMotion.matches || tile.matches(':hover') || tile.contains(document.activeElement)) {
                return;
            }

            projects[currentIndex].hidden = true;
            currentIndex = (currentIndex + 1) % projects.length;
            projects[currentIndex].hidden = false;
        }, rotationInterval);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePartnerProjects, { once: true });
    } else {
        initializePartnerProjects();
    }
}());