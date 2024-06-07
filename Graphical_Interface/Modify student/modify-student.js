document.addEventListener('DOMContentLoaded', function () {
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
                        const option = document.createElement('option');
                        option.value = course;
                        option.textContent = course;
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
        if(lv2==='Spanish'){
            lv2 = 'ESP'
        }
        if(lv2==='German'){
            lv2 = 'ALL'
        }
        if(lv2==='Chinese'){
            lv2 = 'CHI'
        }
        let promo = document.getElementById('student-promo').value;
        promo = promo.substring(0, 2);
        const english_course = document.getElementById('english-course').value;
        fetch(`/timeslot?course=${english_course}`)
            .then(response => response.json())
            .then(timeslot => {
                if (lv2 && promo) {
                    fetch(`/groups/${promo}/${lv2}`)
                        .then(response => response.json())
                        .then(courses => {
                            // Clear existing options
                            lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
                            
                            // Add new options
                            courses.forEach(course => {
                                const timeslot_last = timeslot.substring(timeslot.length - 1);
                                fetch(`/timeslot?course=${course}`)
                                    .then(response => response.json())
                                    .then(timeslot2 => {
                                        const timeslot2_last = timeslot2.substring(timeslot2.length - 1);
                                        const option = document.createElement('option');
                                        option.value = course;
                                        option.textContent = course;            
                                        if (timeslot_last === timeslot2_last) {
                                            option.disabled = true;
                                        }        
                                        lv2CourseSelect.appendChild(option);
                                    })
                            });
                        })
                } else {
                    lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
                }
            })
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
        .catch((error) => {
            console.error('Error:', error);
            alert("Error: An error occurred while adding the student.");
        });
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
    });
})