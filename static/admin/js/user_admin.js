// Only to be run on the user admin page to control visibility of create/edit fields + display related groups for school admins
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
    fetchSchoolGroups(schoolField.value);

    roleField.addEventListener('change', toggleSchoolField);
    schoolField.addEventListener('change', function() {
        fetchSchoolGroups(this.value);
    });

}); //end of DOMContentLoaded

