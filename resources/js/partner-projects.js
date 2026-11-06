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
        const indicator = tile.querySelector('.partner-dots');
        const dots = Array.from(indicator.querySelectorAll('.partner-dot'));
        let currentIndex = 0;
        let rotationTimer = null;

        function showProject(index) {
            currentIndex = (index + projects.length) % projects.length;
            projects.forEach(function (project, projectIndex) {
                project.hidden = projectIndex !== currentIndex;
            });
            dots.forEach(function (dot, dotIndex) {
                dot.classList.toggle('active', dotIndex === currentIndex);
            });
            indicator.setAttribute('aria-label', 'Partner project ' + (currentIndex + 1) + ' of ' + projects.length);
        }

        function startRotation() {
            if (rotationTimer !== null) {
                window.clearInterval(rotationTimer);
            }
            rotationTimer = window.setInterval(function () {
                if (document.hidden || reducedMotion.matches || tile.matches(':hover') || tile.contains(document.activeElement)) {
                    return;
                }

                showProject(currentIndex + 1);
            }, rotationInterval);
        }

        showProject(currentIndex);
        tile.querySelector('.partner-previous').addEventListener('click', function () {
            showProject(currentIndex - 1);
            startRotation();
        });
        tile.querySelector('.partner-next').addEventListener('click', function () {
            showProject(currentIndex + 1);
            startRotation();
        });

        startRotation();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePartnerProjects, { once: true });
    } else {
        initializePartnerProjects();
    }
}());