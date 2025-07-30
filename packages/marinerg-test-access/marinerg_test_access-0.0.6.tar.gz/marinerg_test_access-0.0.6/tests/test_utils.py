from functools import partial

import PIL

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import PortalMember, AccessCall, AccessApplication


def setup_access_call():
    coordinator = PortalMember.objects.get(username="access_call_coordinator")
    access_call_board_member = PortalMember.objects.get(
        username="access_call_board_member"
    )

    access_call = AccessCall.objects.create(
        title="Test access call",
        description="Description of access call",
        status="OPEN",
        closing_date="2024-11-11",
        coordinator=coordinator,
        board_chair=access_call_board_member,
    )

    access_call.board_members.set([access_call_board_member])

    add_group_permissions(
        "consortium_admins", AccessCall, ["change_accesscall", "add_accesscall"]
    )
    return access_call


def setup_application(call, applicant="test_applicant"):
    applicant = PortalMember.objects.get(username=applicant)
    AccessApplication.objects.create(applicant=applicant, call=call)
