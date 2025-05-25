document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.querySelector('.hamburger');
    const leftNav = document.querySelector('.leftNav');
    const body = document.body;

    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        leftNav.classList.toggle('active');
        body.style.overflow = leftNav.classList.contains('active') ? 'hidden' : 'auto';
    });

    // Close menu when clicking on links
    document.querySelectorAll('.nav-item a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            leftNav.classList.remove('active');
            body.style.overflow = 'auto';
        });
    });
});