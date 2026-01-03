// API Base URL
const API_BASE_URL = '/api';

// Function to fetch train schedules
async function fetchSchedules() {
  try {
    const response = await fetch(`${API_BASE_URL}/schedules`);
    if (!response.ok) {
      throw new Error('Failed to fetch schedules');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching schedules:', error);
    return [];
  }
}

// Update all booking links on page
async function updateBookingLinks() {
  // Fetch schedules first
  const schedules = await fetchSchedules();

  if (!schedules || schedules.length === 0) {
    console.log('No schedules available to link to booking page');
    return;
  }

  // Check if user is logged in
  const isLoggedIn = localStorage.getItem('token') !== null;

  // Get first schedule ID for default booking link
  const firstScheduleId = schedules[0].id;

  // Set destination based on login status
  const destination = isLoggedIn ? `booking.html?train_id=${firstScheduleId}` : 'login.html';

  // Update main booking button if exists
  const mainBookBtn = document.getElementById('mainBookBtn');
  if (mainBookBtn) {
    mainBookBtn.href = destination;
  }

  // Update sidebar booking link
  const sidebarBookingLinks = document.querySelectorAll('.sidebar a[href="booking.html"]');
  sidebarBookingLinks.forEach(link => {
    link.href = destination;
  });

  // Update any other booking links with class 'booking-link'
  const bookingLinks = document.querySelectorAll('a.booking-link');
  bookingLinks.forEach(link => {
    link.href = destination;
  });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
  updateBookingLinks();
}); 