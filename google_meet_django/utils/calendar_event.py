import datetime
import uuid

from django.conf import settings

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from google_meet_django.users.models import ServiceToken



def generate_redirect_uri(request):
    hostname = request.META.get("HTTP_HOST")
    return f"http://{hostname}/api/calendar/callback"


def generate_token(user_email):
    creds = None
    service_token = ServiceToken.objects.get(
        user__email=user_email, provider=settings.SERVICE_PROVIDER
    )
    if service_token:
        if service_token.token:
            creds = Credentials.from_authorized_user_info(
                service_token.token, settings.SCOPES
            )
    else:
        return None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(settings.CREDS_JSON, settings.SCOPES)
            creds = flow.run_local_server(port=0)
            service_token.token = creds.to_json()
            service_token.save()
    return creds


def fetch_calendar_events(user_email):
    try:
        creds = generate_token(user_email=user_email)
        if creds:
            service = build("calendar", "v3", credentials=creds)
            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            return events
        return None
    except Exception as error:
        print(f"An error occurred: {str(error)}")
        return None


def create_event(session_data):
    try:
        creds = generate_token(user_email=session_data["host_user"].email)
        if creds:
            service = build("calendar", "v3", credentials=creds)
            event = {
                "summary": session_data["name"],
                "start": {
                    "dateTime": session_data["start_time"].isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": session_data["end_time"].isoformat(),
                    "timeZone": "UTC",
                },
                "attendees": [
                    {"email": attendee.email} for attendee in session_data["attendee"]
                ],
            }
            event = service.events().insert(calendarId="primary", body=event).execute()
            return event
        return None
    except Exception as e:
        print("Error:", str(e))
        return None
