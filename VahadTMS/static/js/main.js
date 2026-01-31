document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');

    // Scroll Effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.padding = '0.5rem 0';
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        } else {
            navbar.style.padding = '1rem 0';
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        }
    });

    // --- Auth & State Management ---

    // Check Login State on Load
    checkLoginState();

    // Handle Forms (Login / Register / General)
    // Handle Forms (Login / Register / General)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Skip forms that have their own inline submit handlers (like Payment)
        if (form.hasAttribute('onsubmit')) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const action = form.getAttribute('action');

            // Login Logic
            if (action && action.includes('login')) {
                const email = form.querySelector('input[name="email"]').value;
                // Mock Login with "Persistent" feel
                const user = { name: "Traveler", email: email, avatar: "images/profile_placeholder.png" };
                localStorage.setItem('vahad_user', JSON.stringify(user));
                alert('Login Successful! Welcome back.');
                window.location.href = 'index.html';
            }
            // Register Logic
            else if (action && action.includes('register')) {
                const name = form.querySelector('input[name="name"]').value;
                const email = form.querySelector('input[name="email"]').value;
                const city = form.querySelector('input[name="city"]').value;
                // Mock Register saving extra details
                const user = { name: name, email: email, city: city, avatar: "images/profile_placeholder.png" };
                localStorage.setItem('vahad_user', JSON.stringify(user));
                alert('Account Created Successfully! Welcome to VAHAD, ' + name);
                window.location.href = 'index.html';
            }
            // Booking Logic
            else if (window.location.pathname.includes('booking.html')) {
                if (!localStorage.getItem('vahad_user')) {
                    const proceed = confirm("You are not logged in. Proceed as Guest?");
                    if (!proceed) return;
                }
                alert('Booking Confirmed! Proceeding to payment...');
                window.location.href = 'payment.html';
            }
        });
    });

    // Search Logic
    window.searchDestinations = function () {
        const query = document.getElementById('navSearchInput').value.trim();
        if (query) {
            window.location.href = `destinations.html?search=${encodeURIComponent(query)}`;
        }
    }

    // Helper: Check Login State
    function checkLoginState() {
        const user = localStorage.getItem('vahad_user');
        const navLinks = document.querySelector('.nav-links');

        if (user && navLinks) {
            const userData = JSON.parse(user);

            // Remove Login/Register buttons
            const authBtns = document.querySelectorAll('.nav-btn, .nav-btn-highlight');
            authBtns.forEach(btn => btn.parentElement.remove()); // Remove the LI

            // Add Profile Section
            // Check if already added to avoid duplicates
            if (!document.getElementById('profile-nav-item')) {
                // Use a travel-themed default avatar if none exists
                const validAvatar = userData.avatar || 'https://cdn-icons-png.flaticon.com/512/4140/4140048.png'; // Tourist Icon

                const profileHtml = `
                    <li id="profile-nav-item" style="position: relative;">
                        <div class="profile-trigger" onclick="toggleProfileMenu()" style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                            <img src="${validAvatar}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary-color);">
                            <span style="font-weight: 600; color: var(--primary-color);">${userData.name.split(' ')[0]}</span>
                        </div>
                        <div id="profile-menu" class="profile-menu" style="display: none; position: absolute; top: 120%; right: 0; background: white; padding: 10px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); width: 150px; text-align: left; z-index: 1001;">
                            <a href="#" style="display: block; padding: 8px; color: #333; font-size: 0.9rem;">My Bookings</a>
                            <a href="#" onclick="changeAvatar()" style="display: block; padding: 8px; color: #333; font-size: 0.9rem;">Change Avatar</a>
                            <a href="#" style="display: block; padding: 8px; color: #333; font-size: 0.9rem;">Settings</a>
                            <div style="border-top: 1px solid #eee; margin: 5px 0;"></div>
                            <a href="#" onclick="logout()" style="display: block; padding: 8px; color: red; font-size: 0.9rem;">Logout</a>
                        </div>
                    </li>
                `;
                navLinks.insertAdjacentHTML('beforeend', profileHtml);
            }
        }
    }

    // Handle Search Box
    const searchBtn = document.querySelector('.search-btn');
    const searchInput = document.querySelector('.search-box input');
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) window.location.href = `destinations.html?search=${query}`;
        });
    }

    // Pre-fill Booking
    if (window.location.pathname.includes('booking.html')) {
        const urlParams = new URLSearchParams(window.location.search);
        const place = urlParams.get('place');
        if (place) {
            const select = document.querySelector('select');
            if (select) {
                let found = false;
                for (let i = 0; i < select.options.length; i++) {
                    if (select.options[i].text.includes(place)) {
                        select.selectedIndex = i;
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    const option = document.createElement('option');
                    option.text = place.replace(/%20/g, ' ');
                    option.selected = true;
                    select.add(option);
                }
            }
        }
    }
});

// Global functions for inline onclicks
function toggleProfileMenu() {
    const menu = document.getElementById('profile-menu');
    if (menu) menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

function changeAvatar() {
    const newAvatar = prompt("Enter URL for new Profile Logo (or leave empty for random):");
    if (newAvatar !== null) { // If not cancelled
        const user = JSON.parse(localStorage.getItem('vahad_user'));

        if (newAvatar.trim() !== "") {
            user.avatar = newAvatar;
        } else {
            // Generate a random project-related travel avatar if empty
            user.avatar = `https://cdn-icons-png.flaticon.com/512/4140/4140048.png`;
        }

        localStorage.setItem('vahad_user', JSON.stringify(user));
        alert("Profile Logo Updated!");
        window.location.reload();
    }
}

function logout() {
    const confirmLogout = confirm("Are you sure you want to logout?");
    if (confirmLogout) {
        localStorage.removeItem('vahad_user');
        alert('Logged out successfully');
        window.location.reload();
    }
}
