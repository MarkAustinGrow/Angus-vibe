// Debug JavaScript file to test static file serving
console.log('Debug.js loaded successfully!');

// Create a visible indicator that the external JavaScript file is loaded
window.addEventListener('DOMContentLoaded', function() {
    var jsIndicator = document.createElement('div');
    jsIndicator.style.position = 'fixed';
    jsIndicator.style.top = '40px';
    jsIndicator.style.right = '10px';
    jsIndicator.style.padding = '5px 10px';
    jsIndicator.style.backgroundColor = 'blue';
    jsIndicator.style.color = 'white';
    jsIndicator.style.fontWeight = 'bold';
    jsIndicator.style.zIndex = '9999';
    jsIndicator.textContent = 'External JS Loaded';
    document.body.appendChild(jsIndicator);
    
    // Add click handlers to all buttons using direct DOM manipulation
    var buttons = document.querySelectorAll('button');
    buttons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            console.log('Button clicked via external JS:', button.id);
            alert('Button clicked via external JS: ' + button.id);
        });
    });
});
