document.addEventListener('DOMContentLoaded', function () {
    // Select all radio buttons and forms
    const radioButtons = document.querySelectorAll('input[name="action"]');
    const forms = {
        "add-student": document.getElementById('add-student-form'),
        "delete-student": document.getElementById('delete-student-form'),
        "change-student-class": document.getElementById('change-student-class-form'),
        "change-teacher-timeslot": document.getElementById('change-teacher-timeslot-form')
    };

    // Function to hide all forms
    function hideAllForms() {
        for (let key in forms) {
            if (forms.hasOwnProperty(key)) {
                forms[key].style.display = 'none';
            }
        }
    }

    // Event listener for each radio button
    radioButtons.forEach(button => {
        button.addEventListener('change', function() {
            hideAllForms(); // First, hide all forms
            // Show the form corresponding to the checked radio button
            if (this.checked) {
                forms[this.value].style.display = 'block';
            }
        });
    });

    // Initially hide all forms except the one for the checked radio button
    hideAllForms();
    const checkedRadioButton = document.querySelector('input[name="action"]:checked');
    if (checkedRadioButton) {
        forms[checkedRadioButton.value].style.display = 'block';
    }

    const promoSelect = document.getElementById('student-promo');
    const englishCourseSelect = document.getElementById('english-course');
    const addSecondLanguageCheckbox = document.getElementById('add-second-language');
    const addSecondLanguage = document.getElementById('add-language');
    const secondLanguageSection = document.getElementById('second-language-section');
    const studentLv2 = document.getElementById('student-lv2');
    const lv2Course = document.getElementById('lv2-course');

    promoSelect.addEventListener('change', (event) => {
        studentLv2.value = "";
        lv2Course.value = "";
        let promo = event.target.value;
        promo = promo.substring(0, 2);
        if (promo) {
            fetch(`/groups/${promo}/ANG`)
                .then(response => response.json())
                .then(groups => {
                    // Clear existing options
                    englishCourseSelect.innerHTML = '<option value="">Select English Course</option>';
                    
                    // Add new options
                    groups.forEach(group => {
                        const groupName = group.ID_GROUP;
                        const studentCount = group.student_count;
                        const courseName = group.ID_COURSE;
                        // Create and append option element
                        const option = document.createElement('option');
                        option.value = courseName;
                        option.textContent = `${groupName} (${studentCount} students)`;
                        englishCourseSelect.appendChild(option);
                    });
                })
        } else {
            englishCourseSelect.innerHTML = '<option value="">Select English Course</option>';
        }

        const toggleSecondLanguageSection = () => {
            const promoValue = promoSelect.value;
            if (promoValue === '1AFG' || promoValue === '2AFG' || promoValue === '3AFG') {
                secondLanguageSection.style.display = 'block';
                studentLv2.style.display = 'block';
                lv2Course.style.display = 'block';
                addSecondLanguage.style.display = 'none';
            } else if (promoValue === '1ABEE' || promoValue === '2ABEE') {
                secondLanguageSection.style.display = 'none';
                studentLv2.value = "";
                lv2Course.value = "";
            } else if (promoValue === '1AFT' || promoValue === '2AFT') {
                secondLanguageSection.style.display = 'block';
                addSecondLanguage.style.display = 'block';
                studentLv2.style.display = addSecondLanguageCheckbox.checked ? 'block' : 'none';
                lv2Course.style.display = addSecondLanguageCheckbox.checked ? 'block' : 'none';
            } else if (promoValue === 'Promo'){
                secondLanguageSection.style.display = 'none';
            }
        };

        promoSelect.addEventListener('change', toggleSecondLanguageSection);
        addSecondLanguageCheckbox.addEventListener('change', toggleSecondLanguageSection);

        // Appeler la fonction au chargement pour définir l'état initial
        toggleSecondLanguageSection()

    });

    const lv2Select = document.getElementById('student-lv2');
    const lv2CourseSelect = document.getElementById('lv2-course');

    lv2Select.addEventListener('change', (event) => {
        let lv2 = event.target.value;
        if (lv2 === 'Spanish') { lv2 = 'ESP'; }
        if (lv2 === 'German') { lv2 = 'ALL'; }
        if (lv2 === 'Chinese') { lv2 = 'CHI'; }
        let promo = document.getElementById('student-promo').value;
        const english_course = document.getElementById('english-course').value;
    
        fetch(`/timeslot?course=${english_course}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
                const timeslot = data.timeslot;
    
                if (lv2 && promo) {
                    fetch(`/groups/${promo}/${lv2}`)
                        .then(response => response.json())
                        .then(groupsLV2 => {
                            lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
                            groupsLV2.forEach(groupLV2 => {
                                const groupName = groupLV2.ID_GROUP;
                                const studentCount = groupLV2.student_count;
                                const timeslot2 = groupLV2.ID_AVAILABILITY;
                                const courseName = groupLV2.ID_COURSE;
                                const option = document.createElement('option');
                                option.value = courseName;
                                option.textContent = `${groupName} (${studentCount} students)`;
                                if (timeslot === timeslot2) {
                                    option.disabled = true;
                                }
                                lv2CourseSelect.appendChild(option);
                                });
                        });
                } else {
                    lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
                }
            })
            .catch(error => console.error('Fetch Error:', error));
    });

    document.getElementById('add-student-form-inner').addEventListener('submit', (event) => {
        event.preventDefault();
        let lv2_student = document.getElementById('student-lv2').value;
        if(lv2_student==='Spanish'){
            lv2_student = 'ESPAGNOL'
        }
        if(lv2_student==='German'){
            lv2_student = 'ALLEMAND'
        }
        if(lv2_student==='Chinese'){
            lv2_student = 'CHINOIS'
        }
        if(lv2_student===''){
            lv2_student = 'None'
        }

        const data = {
            email: document.getElementById('student-email').value,
            name: document.getElementById('student-name').value,
            surname: document.getElementById('student-firstname').value,
            school_year: document.getElementById('student-promo').value,
            lv1: 'ANGLAIS',
            lv2: lv2_student,
            reducedExam: document.getElementById('student-reduced-exam').checked
        };

        fetch('/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response =>{
            console.log("Response status: ", response.status);
            return response.json();
        })
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                const data_english = {
                    english: document.getElementById('english-course').value,
                    email: document.getElementById('student-email').value
                };
        
                fetch('/add2', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data_english),
                })
                .then(response =>{
                    console.log("Response status: ", response.status);
                    return response.json();
                })
                .then(data2 => {
                    console.log(data2);
                    if (data2.status === 'success') {
                        if(document.getElementById('lv2-course').value !== ''){
                            const data_lv2 = {
                                lv2: document.getElementById('lv2-course').value,
                                email: document.getElementById('student-email').value
                            };
        
                            fetch('/add3', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(data_lv2),
                            })
                            .then(response =>{
                                console.log("Response status: ", response.status);
                                return response.json();
                            })
                        }
                        alert("Student added successfully!");
                    } else {
                        alert("Error: " + data2.message);
                    }
                })
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
        
    });
      
    const searchStudent = document.getElementById('student-search-input');
    const studentSelect = document.getElementById('mySelectDelete');
    var buttonDelete = document.getElementById('delete-student-button');

    searchStudent.addEventListener('change', (event) => {
        let studentSearched = event.target.value;
        studentSearched = studentSearched.toLowerCase();
        fetch('/students')
            .then(response => response.json())
            .then(students => {
                // Clear the select options
                studentSelect.innerHTML = '';
                let defaultOption = document.createElement('option');
                defaultOption.value = "";
                defaultOption.text = "Select a Student";
                studentSelect.add(defaultOption);
                let addedEmails = {};
                students.forEach(student => {
                    console.log(student);
                    nameStudent = student.Surname.toLowerCase()
                    if(nameStudent.startsWith(studentSearched) && !addedEmails[student.Email]) {
                            let option = document.createElement('option');
                            option.value = student.Email;
                            option.text = student.Name + ' ' + student.Surname;
                            studentSelect.add(option);
                            addedEmails[student.Email] = true;
                        
                    }
                });
            });
    });

    const studentDetails = document.getElementById('student-details');

    studentSelect.addEventListener('change', (event) => {
        let studentEmail = event.target.value;
        console.log(studentEmail);
        fetch(`/students`)
            .then(response => response.json())
            .then(students => {
                let student = students.find(s => s.Email === studentEmail);
                console.log(student);
                if (student) {
                    studentDetails.style.display = 'block';
                    document.getElementById('student-name-delete').textContent = student.Surname;
                    document.getElementById('student-firstname-delete').textContent = student.Name;
                    document.getElementById('student-promo-delete').textContent = student.Class;
                    document.getElementById('student-email-delete').textContent = student.Email;
                    buttonDelete.removeAttribute('disabled');
                }
                if (!student) {
                    studentDetails.style.display = 'none';
                    buttonDelete.setAttribute('disabled', 'disabled');
                }
            });
    });

    buttonDelete.addEventListener('click', function() {
        const emailToDelete = studentSelect.value;
        fetch('/deleteStudent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: emailToDelete
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // La suppression a réussi
                alert('Student deleted successfully!');
                studentDetails.style.display = 'none';
                buttonDelete.setAttribute('disabled', 'disabled');
                searchStudent.value = '';
                selectedStudent.value = '';
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

});
