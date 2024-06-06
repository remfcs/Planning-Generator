document.addEventListener('DOMContentLoaded', function () {
    const promoSelect = document.getElementById('student-promo');
    const englishCourseSelect = document.getElementById('english-course');

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
        if (lv2 && promo) {
            fetch(`/groups/${promo}/${lv2}`)
                .then(response => response.json())
                .then(courses => {
                    console.log('Courses fetched:', courses);
                    // Clear existing options
                    lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
                    
                    // Add new options
                    courses.forEach(course => {
                        const option = document.createElement('option');
                        option.value = course;
                        option.textContent = course;
                        lv2CourseSelect.appendChild(option);
                    });
                })
        } else {
            lv2CourseSelect.innerHTML = '<option value="">Select LV2 Course</option>';
        }
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