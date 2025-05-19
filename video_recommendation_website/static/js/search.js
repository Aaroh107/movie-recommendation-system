/**
 * Search functionality for the video recommendation website
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get search form and input
    const searchForm = document.querySelector('form[action*="search"]');
    const searchInput = searchForm ? searchForm.querySelector('input[name="q"]') : null;
    
    if (searchForm && searchInput) {
        // Add event listeners
        searchForm.addEventListener('submit', handleSearchSubmit);
        searchInput.addEventListener('input', handleSearchInput);
        
        // Initialize search highlighting if we're on the search results page
        if (window.location.pathname === '/search') {
            highlightSearchTerms();
        }
    }
});

/**
 * Handle search form submission
 * @param {Event} event - Form submit event
 */
function handleSearchSubmit(event) {
    const input = event.target.querySelector('input[name="q"]');
    
    // Only submit if the search term has at least 2 characters
    if (input && input.value.trim().length < 2) {
        event.preventDefault();
        alert('Please enter at least 2 characters to search');
    }
}

/**
 * Handle search input changes
 * @param {Event} event - Input event
 */
function handleSearchInput(event) {
    // You could implement search suggestions here
    const searchTerm = event.target.value.trim();
    
    if (searchTerm.length >= 3) {
        console.log('Search term entered:', searchTerm);
        // Here you could fetch search suggestions from backend
    }
}

/**
 * Highlight search terms in search results
 */
function highlightSearchTerms() {
    // Get the search query from URL
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    
    if (!query) return;
    
    // Create RegExp for the search term
    const searchTerms = query.split(' ').filter(term => term.length > 2);
    if (searchTerms.length === 0) return;
    
    // Get all video titles
    const videoTitles = document.querySelectorAll('.video-card .card-title');
    
    videoTitles.forEach(titleElement => {
        const originalText = titleElement.textContent;
        let highlightedText = originalText;
        
        searchTerms.forEach(term => {
            const regex = new RegExp(`(${term})`, 'gi');
            highlightedText = highlightedText.replace(regex, '<span class="text-warning">$1</span>');
        });
        
        if (highlightedText !== originalText) {
            titleElement.innerHTML = highlightedText;
        }
    });
}

/**
 * Track search analytics
 * @param {string} searchTerm - The search term 
 * @param {number} resultCount - Number of results found
 */
function trackSearchAnalytics(searchTerm, resultCount) {
    console.log(`Search analytics: term="${searchTerm}", results=${resultCount}`);
    // In a real application, you would send this data to your analytics system
}
