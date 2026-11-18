
const form = document.querySelector("form");

const steps = [
  document.getElementById("step-1"),
  document.getElementById("step-2"),
  document.getElementById("step-3")
];

let currentStep = 0;

// Display one step at a time.
function showStep(index) {
  steps.forEach((step, i) => {
    step.hidden = i !== index;
  });

  currentStep = index;

  const heading = steps[index].querySelector("h2");
  heading.setAttribute("tabindex", "-1");
  heading.focus();
}

// Find the error message belonging to a field.
function getErrorElement(field) {
  if (field.name === "role") {
    return document.getElementById("error-role");
  }

  if (field.name === "interests") {
    return document.getElementById("error-interests");
  }

  return document.getElementById(`error-${field.id}`);
}

// Validate every field in a step using HTML's native
// constraint-validation rules.
function validateStep(step) {
  const fields = [
    ...step.querySelectorAll("input, select, textarea")
  ];

  const invalidFields = [];
  const handledGroups = new Set();

  fields.forEach(field => {
    if (field.type === "hidden" || field.disabled) {
      return;
    }

    // Clear previous error state.
    field.setAttribute("aria-invalid", "false");

    const errorElement = getErrorElement(field);

    if (errorElement) {
      errorElement.textContent = "";
    }

    if (field.checkValidity()) {
      return;
    }

    invalidFields.push(field);

    const groupName =
      field.type === "radio" || field.type === "checkbox"
        ? field.name
        : null;

    // Display a group error only once.
    if (groupName && handledGroups.has(groupName)) {
      return;
    }

    if (groupName) {
      handledGroups.add(groupName);
    }

    const groupFields = groupName
      ? fields.filter(item => item.name === groupName)
      : [field];

    groupFields.forEach(item => {
      item.setAttribute("aria-invalid", "true");

      if (errorElement) {
        item.setAttribute(
          "aria-describedby",
          errorElement.id
        );
      }
    });

    if (errorElement) {
      errorElement.textContent = field.validationMessage;
    }
  });

  if (invalidFields.length > 0) {
    const firstInvalid = invalidFields[0];

    // Focus the first invalid field.
    firstInvalid.focus();

    // Display the browser's native validation message too.
    firstInvalid.reportValidity();

    return false;
  }

  return true;
}

// Next button on Step 1.
document.getElementById("next-1").addEventListener("click", () => {
  if (validateStep(steps[0])) {
    showStep(1);
  }
});

// Back button on Step 2.
document.getElementById("back-2").addEventListener("click", () => {
  showStep(0);
});

// Next button on Step 2.
document.getElementById("next-2").addEventListener("click", () => {
  if (validateStep(steps[1])) {
    showStep(2);
  }
});

// Back button on Step 3.
document.getElementById("back-3").addEventListener("click", () => {
  showStep(1);
});

// Check every step before the form is submitted.
form.addEventListener("submit", event => {
  for (let i = 0; i < steps.length; i++) {
    if (!validateStep(steps[i])) {
      event.preventDefault();
      showStep(i);

      // Focus again after making the invalid step visible.
      const invalidField = steps[i].querySelector(
        '[aria-invalid="true"]'
      );

      if (invalidField) {
        invalidField.focus();
      }

      return;
    }
  }
});

// Start at Step 1.
showStep(0);
