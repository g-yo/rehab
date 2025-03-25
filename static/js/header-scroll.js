// Header scroll behavior
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('.header');
    if (!header) return; // Exit if no header is found
    
    let lastScrollTop = 0;
    let headerHeight = header.offsetHeight;
    
    // Set initial position and transition
    header.style.position = 'fixed';
    header.style.top = '0';
    header.style.width = '100%';
    header.style.zIndex = '1000';
    header.style.transition = 'transform 0.3s ease-in-out';
    
    // Add padding to body to prevent content jump
    document.body.style.paddingTop = headerHeight + 'px';
    
    // Handle window resize to update header height
    window.addEventListener('resize', function() {
        headerHeight = header.offsetHeight;
        document.body.style.paddingTop = headerHeight + 'px';
    });
    
    window.addEventListener('scroll', function() {
        let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        
        // Scrolling down
        if (currentScroll > lastScrollTop && currentScroll > headerHeight) {
            header.style.transform = 'translateY(-100%)';
        } 
        // Scrolling up
        else if (currentScroll < lastScrollTop) {
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
    }, false);
});
