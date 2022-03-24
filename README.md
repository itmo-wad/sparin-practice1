# Practice 1

This is my submission of Practice

I created a simple application with authentication and authorization on `/profile` and `/upload` methods. All users are saved in the MongoDB database and their passwords are hashed using PBKDF2 with SHA-256 and 260000 iterations. Also, I used WTForms for simple validation of forms in registration and login pages

- [x] Create a flask app which connects to MongoDB and runs at ‘http://localhost:5000’
- [x] Authentication
- [x] Implement image upload feature
- [ ] Implement notebook at ‘/notebook’
- [ ] Implement chat bot at ‘/chatbot’

## Prerequisites

Running MongoDB on localhost:27017 with created database `practice-1` and collection `users`  

## Run

`python src/app.py`

## Credits

Medvedtiskov Yuriy Sergeevich (ISU 208364 / N41503c)
