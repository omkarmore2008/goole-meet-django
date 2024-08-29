# Google-Meet-Django

Basic google session creation and meeting link generate


## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

This guide provides the necessary steps to set up and start a Dockerized Django project.

## Prerequisites

Before you start, make sure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Project Setup

### 1. Clone the Repository

First, clone the repository to your local machine:


        $ git clone https://github.com/omkarmore2008/goole-meet-django.git
        $ cd goole-meet-django

### 2. setting up environment variable
        $ cp .env.example .env


### 3. Build and Start the Containers

        $ sudo docker compose -f docker-compose.local.yml up --build

### 4. Bash to djago contianer and apply migrations


        $ docker exec -it google_meet_local_django bash
        $ python manage.py makemigrations
        $ python manage.py migrate

### 5. Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

#### Running tests with pytest

      $ pytest

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

# Google Calendar API Integration Setup

This guide will walk you through the setup process for integrating Google Calendar API with your project, including creating OAuth 2.0 Client IDs and enabling the necessary API services.

## Prerequisites

- Google account
- Access to Google Cloud Console
- Basic understanding of API integration and OAuth 2.0

## Step 1: Create a Project in Google Cloud Console

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the **Select a project** dropdown at the top.
3. Click on **New Project**.
4. Enter your project name and click **Create**.

## Step 2: Set Up OAuth 2.0 Credentials

1. In the Google Cloud Console, go to the [Credentials page](https://console.cloud.google.com/apis/credentials).
2. Click on **Create Credentials** and select **OAuth 2.0 Client IDs**.
3. You may need to configure the OAuth consent screen if you haven't done so already:
   - Go to the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
   - Select your user type and fill out the required fields.
   - Add the scopes you need (e.g., `https://www.googleapis.com/auth/calendar`).
   - Save and continue through the consent screen configuration.
 
###### &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Creating OAuth Client ID with Required Attributes

4. After configuring the consent screen, go back to the **Credentials** page.
5. Click **Create Credentials** > **OAuth 2.0 Client ID**.
6. Set the following required attributes:
   - **Application Type**: Select **Web application**.
   - **Name**: Provide a name for your OAuth client, such as `My Calendar Integration`.
   - **Authorized redirect URIs**: Add the redirect URIs your application will use. For local development, you might use `http://localhost:8000/api/calendar/callback`. For production, ensure that you use your application's domain.

7. Click **Create**.
8. Download the generated JSON file (often named `credentials.json`) and save it securely in your project directory.

## Step 4: Integrate Google Calendar API in Your Application

1. Set up the `.env.local.django` file:

   Create a `.env.local.django` file in the root directory of your project and add the following keys:

    ```
    SCOPES=["https://www.googleapis.com/auth/calendar"]
    CREDS_JSON=credentials.json
    ```

2. Now, you can use the credentials to access the Google Calendar API and perform various operations like creating, updating, or fetching events.

## Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [OAuth 2.0 Overview](https://developers.google.com/identity/protocols/oauth2)
- [Python Quickstart for Google Calendar API](https://developers.google.com/calendar/quickstart/python)

## Troubleshooting

If you encounter issues, check the following:

- Ensure your OAuth 2.0 Client IDs JSON file is correctly configured.
- Verify that your redirect URIs match what is set in your Google Cloud Console.
- Make sure the necessary API services are enabled in your project.

## License

This project is licensed under the MIT License.
