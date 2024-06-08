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
    const secondLanguageSection = document.getElementById('second-language-section');
    const studentLv2 = document.getElementById('student-lv2');
    const lv2Course = document.getElementById('lv2-course');

    promoSelect.addEventListener('change', (event) => {
        let promo = event.target.value;
        promo = promo.substring(0, 2);
        if (promo) {
            fetch(`/groups/${promo}/ANG`)
                .then(response => response.json())
                .then(courses => {
                    // Clear existing options
                    englishCourseSelect.innerHTML = '<option value="">Select English Course</option>';
                    
                    // Add new options
                    courses.forEach(course => {
                        const className = course.course_id;
                        const studentCount = course.student_count;
                        // Create and append option element
                        const option = document.createElement('option');
                        option.value = className;
                        option.textContent = `${className} (${studentCount} students)`;
                        englishCourseSelect.appendChild(option);
                    });
                })
        } else {
            englishCourseSelect.innerHTML = '<option value="">Select English Course</option>';
        }

        const toggleSecondLanguageSection = () => {
            const promoValue = promoSelect.value;
            if (promoValue === '1A' || promoValue === '2A' || promoValue === '3A') {
                secondLanguageSection.style.display = 'block';
                studentLv2.style.display = 'block';
                lv2Course.style.display = 'block';
                addSecondLanguageCheckbox.style.display = 'none';
            } else if (promoValue === '1ABEE' || promoValue === '2ABEE' || promoValue === '3ABEE') {
                secondLanguageSection.style.display = 'none';
                studentLv2.value = "";
                lv2Course.value = "";
            } else if (promoValue === '1AFT' || promoValue === '2AFT') {
                secondLanguageSection.style.display = 'block';
                addSecondLanguageCheckbox.style.display = 'block';
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
        let promo = document.getElementById('student-promo').value.substring(0, 2);
        const english_course = document.getElementById('english-course').value;
    
        fetch(`/timeslot?course=${english_course}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
                const timeslot_last = data.timeslot[data.timeslot.length - 1];
    
                if (lv2 && promo) {
                    fetch(`/groups/${promo}/${lv2}`)
                        .then(response => response.json())
                        .then(courses => {
                            lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
                            courses.forEach(course => {
                                const className = course.course_id;
                                const studentCount = course.student_count;
    
                                fetch(`/timeslot?course=${className}`)
                                    .then(response => response.json())
                                    .then(timeslot2Data => {
                                        const timeslot2_last = timeslot2Data.timeslot[timeslot2Data.timeslot.length - 1];
                                        const option = document.createElement('option');
                                        option.value = className;
                                        option.textContent = `${className} (${studentCount} students)`;
                                        if (timeslot_last === timeslot2_last) {
                                            option.disabled = true;
                                        }
                                        lv2CourseSelect.appendChild(option);
                                    });
                            });
                        });
                } else {
                    lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
                }
            })
            .catch(error => console.error('Fetch Error:', error));
    });
    


    document.getElementById('add-student-form-inner').addEventListener('submit', (event) => {
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
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Student added successfully!");
            } else {
                alert("Error: " + data.message);
            }
        })
    });

    document.getElementById('add-student-form-inner').addEventListener('submit', (event) => {
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
    });

    document.getElementById('add-student-form-inner').addEventListener('submit', (event) => {
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
        }
    });
})