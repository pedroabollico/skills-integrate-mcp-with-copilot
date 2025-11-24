# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.

## Managing Activities

Activities are stored in the `activities.json` file, which can be safely edited by teachers without modifying any Python code. This makes it easy to add, remove, or update activities.

### Editing Activities

To modify activities, simply edit the `activities.json` file. Each activity has the following structure:

```json
{
  "Activity Name": {
    "description": "Description of the activity",
    "schedule": "When the activity meets",
    "max_participants": 20,
    "participants": ["email1@mergington.edu", "email2@mergington.edu"]
  }
}
```

### Example: Adding a New Activity

To add a new activity, add a new entry to the JSON file:

```json
{
  "Science Club": {
    "description": "Conduct experiments and explore scientific concepts",
    "schedule": "Wednesdays, 3:00 PM - 4:30 PM",
    "max_participants": 15,
    "participants": []
  }
}
```

After editing the file, restart the server for changes to take effect.

**Note:** Make sure the JSON file is valid. You can use online JSON validators if you're unsure about the syntax.
