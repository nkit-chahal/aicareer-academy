
(function () {
  var form = document.getElementById('inquiryForm');
  if (!form) return;

  var courseSelect = document.getElementById('course');
  var params = new URLSearchParams(window.location.search);
  var courseParam = params.get('course');
  if (courseParam && courseSelect) {
    for (var i = 0; i < courseSelect.options.length; i++) {
      if (courseSelect.options[i].value === courseParam) {
        courseSelect.selectedIndex = i;
        break;
      }
    }
  }

  var fields = {
    name: { el: document.getElementById('name'), err: document.getElementById('nameError'), msg: 'Please enter your name.' },
    phone: { el: document.getElementById('phone'), err: document.getElementById('phoneError'), msg: 'Please enter a valid phone number.' },
    email: { el: document.getElementById('email'), err: document.getElementById('emailError'), msg: 'Please enter a valid email address.' },
    experience: { el: document.getElementById('experience'), err: document.getElementById('experienceError'), msg: 'Please select your experience level.' },
    course: { el: courseSelect, err: document.getElementById('courseError'), msg: 'Please select a program.' }
  };

  function clearErrors() {
    Object.keys(fields).forEach(function (key) {
      var f = fields[key];
      if (f.err) f.err.textContent = '';
      if (f.el) f.el.classList.remove('invalid');
    });
  }

  function showError(key, message) {
    var f = fields[key];
    if (f.err) f.err.textContent = message || f.msg;
    if (f.el) f.el.classList.add('invalid');
  }

  function isValidPhone(val) {
    var digits = val.replace(/\D/g, '');
    return digits.length >= 10;
  }

  function isValidEmail(val) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
  }

  function courseLabel() {
    if (!courseSelect || courseSelect.selectedIndex < 0) return '';
    return courseSelect.options[courseSelect.selectedIndex].text;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearErrors();

    var name = fields.name.el.value.trim();
    var phone = fields.phone.el.value.trim();
    var email = fields.email.el.value.trim();
    var experience = fields.experience.el.value;
    var course = fields.course.el.value;
    var message = document.getElementById('message').value.trim();
    var valid = true;

    if (!name) { showError('name'); valid = false; }
    if (!phone || !isValidPhone(phone)) { showError('phone'); valid = false; }
    if (!email || !isValidEmail(email)) { showError('email'); valid = false; }
    if (!experience) { showError('experience'); valid = false; }
    if (!course) { showError('course'); valid = false; }
    if (!valid) {
      var firstInvalid = form.querySelector('.invalid');
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    var lines = [
      "Hi, I'd like to book a career call.",
      'Name: ' + name,
      'Phone: ' + phone,
      'Email: ' + email,
      'Experience: ' + experience,
      'Course: ' + courseLabel()
    ];
    if (message) lines.push('Message: ' + message);

    var url = 'https://wa.me/918708752385?text=' + encodeURIComponent(lines.join('\n'));
    window.open(url, '_blank');
  });
})();
