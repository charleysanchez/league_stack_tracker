document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('detail');
    const dropdownContent = document.getElementById('dropdown');

    toggleButton.addEventListener('click', function () {
        // Toggle the "hidden" class to show/hide the dropdown content
        dropdownContent.classList.toggle('hidden');
    });
});