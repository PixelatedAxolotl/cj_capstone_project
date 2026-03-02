// Only to be run on the user admin page to control visibility of create/edit fields
document.addEventListener('DOMContentLoaded', function() {
    const roleField = document.getElementById('id_role');
    const schoolField = document.getElementById('id_school');
    const schoolRow = schoolField.closest('.form-row');

    // Create a container for displaying groups
    const groupsContainer = document.createElement('div');
    groupsContainer.id = 'school-groups-container';
    groupsContainer.style.marginTop = '8px';
    schoolRow.appendChild(groupsContainer);

    function toggleSchoolField() {
        if (roleField.value === 'school_admin') {
            schoolRow.style.display = '';
        } else {
            schoolRow.style.display = 'none';
            schoolField.value = '';
            groupsContainer.innerHTML = '';
        }
    }

    toggleSchoolField();
    roleField.addEventListener('change', toggleSchoolField);
}); //end of DOMContentLoaded