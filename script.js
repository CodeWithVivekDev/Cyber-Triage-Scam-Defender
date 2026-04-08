document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Mouse Blob Tracker
    const blob = document.getElementById("blob");
    
    document.body.onpointermove = event => { 
        const { clientX, clientY } = event;
        // Move the blob smoothly using browser frames
        blob.animate({
            left: `${clientX}px`,
            top: `${clientY}px`
        }, { duration: 3000, fill: "forwards" });
    }

    // 2. 3D Tilt Effect for Cards
    const tiltElements = document.querySelectorAll('[data-tilt]');
    
    tiltElements.forEach(el => {
        el.addEventListener('mousemove', handleTilt);
        el.addEventListener('mouseleave', resetTilt);
        // Reset transition property on enter to snap to mouse quickly
        el.addEventListener('mouseenter', () => el.style.transition = 'none');
    });

    function handleTilt(e) {
        const el = this;
        const rect = el.getBoundingClientRect();
        
        // Calculate mouse position relative to the center of the card
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        // Calculate rotation amounts (Max 15 degrees)
        const maxTilt = 15;
        const rotateX = ((y - centerY) / centerY) * -maxTilt;
        const rotateY = ((x - centerX) / centerX) * maxTilt;
        
        // Custom scale if requested
        const scale = el.getAttribute('data-tilt-scale') || '1.05';

        // Apply 3D transform
        el.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(${scale}, ${scale}, ${scale})`;
    }

    function resetTilt() {
        const el = this;
        // Smoothly return to flat resting state
        el.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        el.style.transition = 'transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)';
    }
    
    // 3. Logo interactive bounce pulse
    const logo = document.querySelector('.logo');
    if(logo) {
        logo.addEventListener('mouseover', () => {
             logo.style.transform = 'translateZ(30px) scale(1.1) rotate(5deg)';
        });
        logo.addEventListener('mouseleave', () => {
             logo.style.transform = 'translateZ(0) scale(1) rotate(0deg)';
        });
    }
});
