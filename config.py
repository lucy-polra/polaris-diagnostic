import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY", "")
TENANT_ID            = os.getenv("AZURE_TENANT_ID", "")
CLIENT_ID            = os.getenv("AZURE_CLIENT_ID", "")
CLIENT_SECRET        = os.getenv("AZURE_CLIENT_SECRET", "")
SHAREPOINT_SITE_ID   = os.getenv("SHAREPOINT_SITE_ID", "")
SHAREPOINT_DRIVE_ID  = os.getenv("SHAREPOINT_DRIVE_ID", "")
SHAREPOINT_LIST_ID   = os.getenv("SHAREPOINT_LIST_ID", "")
APP_PASSWORD         = os.getenv("APP_PASSWORD", "polariscloud2026")
