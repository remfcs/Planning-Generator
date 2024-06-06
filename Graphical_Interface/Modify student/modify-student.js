document.addEventListener('DOMContentLoaded', function () {
    const promoSelect = document.getElementById('student-promo');
    const englishCourseSelect = document.getElementById('english-course');

    promoSelect.addEventListener('change', (event) => {
        const promo = event.target.value;
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
        const promo = document.getElementById('student-promo').value;
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
        const data = {
            email: document.getElementById('student-email').value,
            name: document.getElementById('student-name').value,
            surname: document.getElementById('student-firstname').value,
            school_year: document.getElementById('student-promo').value,
            lv1: 'ANG',
            lv2: document.getElementById('student-lv2').value,
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


})