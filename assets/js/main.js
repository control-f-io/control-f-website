// FAQ Accordion
document.addEventListener('DOMContentLoaded', function() {
  const faqQuestions = document.querySelectorAll('.faq-question');

  faqQuestions.forEach(function(question) {
    question.addEventListener('click', function() {
      const faqItem = this.parentElement;
      const isOpen = faqItem.classList.contains('open');

      // Toggle current item
      if (isOpen) {
        faqItem.classList.remove('open');
        this.setAttribute('aria-expanded', 'false');
      } else {
        faqItem.classList.add('open');
        this.setAttribute('aria-expanded', 'true');
      }
    });
  });
});
