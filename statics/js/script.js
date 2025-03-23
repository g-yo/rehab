document.addEventListener("DOMContentLoaded", function() {
    const header = document.querySelector(".header");
    const searchBar = document.querySelector(".search-bar");

    window.addEventListener("scroll", function() {
        if (window.scrollY > 50) {
            header.classList.add("scrolled");
            searchBar.style.paddingRight = "0"; // Remove padding when scrolled
        } else {
            header.classList.remove("scrolled");
            searchBar.style.paddingRight = "20%"; // Add padding when not scrolled
        }
    });
});
// Add this to your existing script.js file

document.addEventListener("DOMContentLoaded", function() {
    // Existing code...

    // Animate the wave on page load
    const wave = document.querySelector('.wave');
    wave.style.transform = 'translateY(100%)';
    wave.style.transition = 'transform 1s ease-in-out';

    setTimeout(() => {
        wave.style.transform = 'translateY(0)';
    }, 100);
});
function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    obj.style.animation = `countUp ${duration}ms ease-out forwards`;
    
    const stepTime = Math.abs(Math.floor(duration / (end - start)));
    let current = start;
    
    const timer = setInterval(() => {
      current += 1;
      obj.textContent = current;
      if (current === end) {
        clearInterval(timer);
        if (end >= 20) obj.textContent = '20+';
      }
    }, stepTime);
  }
  
  window.onload = function() {
    animateValue('projects', 0, 20, 4000);
    animateValue('clients', 0, 15, 4000);
    animateValue('team', 0, 20, 4000);
    animateValue('internships', 0, 20, 4000);
  };

  document.addEventListener('DOMContentLoaded', function() {
    const overlay = document.getElementById('overlay');
    const closeButton = document.getElementById('close-button');

    closeButton.addEventListener('click', function() {
        overlay.style.display = 'none';
        document.querySelector('.main-content').style.display = 'block';
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const borderedText = document.getElementById('borderedText');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function() {
        const scrollTop = window.scrollY;
        
        if (scrollTop > lastScrollTop) {
            // Scrolling down
            const newSize = Math.max(20, borderedText.offsetHeight - 2);
            borderedText.style.fontSize = newSize + 'px';
        } else {
            // Scrolling up
            const newSize = Math.min(100, borderedText.offsetHeight + 2);
            borderedText.style.fontSize = newSize + 'px';
        }

        lastScrollTop = scrollTop;
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const testimonials = document.querySelectorAll(".testimonial");
    let currentTestimonial = 0;

    function showTestimonial(index) {
        testimonials.forEach((testimonial, i) => {
            testimonial.classList.remove("active");
            testimonial.style.opacity = 0;
        });
        testimonials[index].classList.add("active");
        testimonials[index].style.opacity = 1;
    }

    function showNextTestimonial() {
        currentTestimonial = (currentTestimonial + 1) % testimonials.length;
        showTestimonial(currentTestimonial);
    }

    setInterval(showNextTestimonial, 5000); // 5 seconds interval
});

    function showSpecifyField() {
        var relationship = document.getElementById("id_guider_relationship");
        var specifyField = document.getElementById("other-specify");
        if (relationship.value === "other") {
            specifyField.style.display = "block";
        } else {
            specifyField.style.display = "none";
        }
    }
    document.getElementById("id_guider_relationship").addEventListener("change", showSpecifyField);
