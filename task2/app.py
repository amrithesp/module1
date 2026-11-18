
from flask import Flask, request, render_template_string, jsonify
from pathlib import Path
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)

HTML_FILE = Path(__file__).parent / "inside_task_3.html"

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024


@app.get("/")
def registration_form():
    html = HTML_FILE.read_text(encoding="utf-8")
    return render_template_string(html)


def validate_registration(form, files):
    # Client-side and server-side rules are deliberately duplicated:
    # browser checks can be disabled or bypassed, so the server must
    # independently enforce every rule before accepting untrusted data.

    errors = {}

    # Reject unexpected fields instead of silently accepting them.
    allowed_fields = {
        "fullname", "age", "email", "phone",
        "password", "role", "interests", "form_id"
    }

    unexpected = set(form.keys()) - allowed_fields
    if unexpected:
        errors["form"] = "Unexpected form fields were submitted."

    # 1. Hidden-field tampering check.
    if form.get("form_id") != "registration_v1":
        errors["form_id"] = "Invalid form identifier."

    # 2. Full name: 2–50 English letters and spaces.
    fullname = form.get("fullname", "").strip()

    if not 2 <= len(fullname) <= 50:
        errors["fullname"] = "Name must contain 2–50 characters."
    elif not re.fullmatch(r"[A-Za-z][A-Za-z ]{1,49}", fullname):
        errors["fullname"] = (
            "Use English letters and spaces; start with a letter."
        )

    # 3. Age: integer from 18 to 100.
    age = form.get("age", "")

    if not re.fullmatch(r"[0-9]+", age):
        errors["age"] = "Age must be a whole number."
    elif not 18 <= int(age) <= 100:
        errors["age"] = "Age must be between 18 and 100."

    # 4. Email: basic format check and maximum length.
    email = form.get("email", "").strip()

    if len(email) > 254:
        errors["email"] = "Email must not exceed 254 characters."
    elif not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", email
    ):
        errors["email"] = "Enter a valid email address."

    # 5. Phone: exactly 10 digits.
    phone = form.get("phone", "")

    if not re.fullmatch(r"[0-9]{10}", phone):
        errors["phone"] = "Phone must contain exactly 10 digits."

    # 6. Password: 8–20 characters.
    # Never return or display the submitted password.
    password = form.get("password", "")

    if not 8 <= len(password) <= 20:
        errors["password"] = (
            "Password must contain 8–20 characters."
        )

    # 7. Role: only allowed values.
    role = form.get("role", "")

    if role not in {"student", "teacher"}:
        errors["role"] = "Select a valid role."

    # 8. Interests: only allowed values.
    interests = form.getlist("interests")
    allowed_interests = {"coding", "music", "sports"}

    if len(interests) != len(set(interests)):
        errors["interests"] = "Duplicate interests are not allowed."
    elif not set(interests).issubset(allowed_interests):
        errors["interests"] = "One or more interests are invalid."

    # 9. File upload: required, correct type and maximum 2 MB.
    uploaded_file = files.get("profilepic")

    if uploaded_file is None or not uploaded_file.filename:
        errors["profilepic"] = "A profile picture is required."
    else:
        filename = secure_filename(uploaded_file.filename)

        if not filename:
            errors["profilepic"] = "Invalid filename."
        else:
            # Read at most 2 MB + 1 byte to detect oversized files.
            content = uploaded_file.stream.read(MAX_FILE_SIZE + 1)
            uploaded_file.stream.seek(0)

            if len(content) > MAX_FILE_SIZE:
                errors["profilepic"] = (
                    "Profile picture must be 2 MB or smaller."
                )
            elif content.startswith(b"\x89PNG\r\n\x1a\n"):
                pass  # PNG signature detected.
            elif (
                content.startswith(b"\xff\xd8\xff")
                and content.endswith(b"\xff\xd9")
            ):
                pass  # JPEG signature detected.
            else:
                errors["profilepic"] = (
                    "Upload a valid PNG or JPEG image."
                )

    return errors


@app.post("/register")
def register():
    errors = validate_registration(request.form, request.files)

    if errors:
        return jsonify({
            "status": "rejected",
            "errors": errors
        }), 400

    # This demonstration validates the form but does not create
    # an account, store the password, or save the uploaded file.
    return jsonify({
        "status": "accepted",
        "message": "All registration fields passed validation."
    }), 200


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(error):
    return jsonify({
        "status": "rejected",
        "errors": {
            "profilepic": "The uploaded request is too large."
        }
    }), 413


if __name__ == "__main__":
    app.run(debug=True)
