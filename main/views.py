import base64
import json

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from fido2.webauthn import (
    AttestationObject,
    AuthenticatorData,
    CollectedClientData,
    PublicKeyCredentialRpEntity,
    PublicKeyCredentialDescriptor
)
from fido2.server import Fido2Server

from .models import Student, AttendanceRecord

rp = PublicKeyCredentialRpEntity(id="e268-102-91-71-60.ngrok-free.app", name="Demo ExamAuth")
server = Fido2Server(rp)

# --- Home page (same as your index.html) ---
def home(request):
    return render(request, "index.html")

from fido2 import cbor

# --- Fingerprint Registration ---
@csrf_exempt
def register_fingerprint(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")

        try:
            student = Student.objects.get(user__username=username)
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student not found."}, status=404)

        state = request.session.get("fido2_registration_state")
        if not state:
            return JsonResponse({"error": "No registration state found."}, status=400)

        # Decode credential
        credential = data.get("credential")
        attestation = credential["response"]
        client_data = CollectedClientData(base64.b64decode(attestation["clientDataJSON"]))
        att_obj = AttestationObject(base64.b64decode(attestation["attestationObject"]))

        auth_data = server.register_complete(
            state,
            client_data,
            att_obj,
        )
        public_key_bytes = cbor.encode(auth_data.credential_data.public_key)

        # Store credential data
        student.fingerprint_credential = {
            "id": credential["id"],
            "public_key": base64.b64encode(public_key_bytes).decode(),
            "sign_count": auth_data.counter,
        }
        student.save()
        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "Invalid request"}, status=400)

import base64

def b64encode_bytes(obj):
    if isinstance(obj, dict):
        return {k: b64encode_bytes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [b64encode_bytes(i) for i in obj]
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode()
    else:
        return obj

@csrf_exempt
def fingerprint_login_begin(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        try:
            student = Student.objects.get(user__username=username)
        except Student.DoesNotExist:
            return JsonResponse({"success": False, "message": "Student not found"})

        credential_data = student.fingerprint_credential
        if not credential_data:
            return JsonResponse({"success": False, "message": "No fingerprint registered"})

        # Create credential descriptor for authentication
        credential_id = base64.b64decode(credential_data["id"])
        
        allow_credentials = [
            PublicKeyCredentialDescriptor(
                type="public-key",
                id=credential_id
            )
        ]

        # Begin authentication
        auth_data, state = server.authenticate_begin(allow_credentials)
        request.session["fido2_authentication_state"] = state

        # Convert to dict and base64-encode bytes fields
        if hasattr(auth_data, "dict"):
            options = auth_data.dict()
        else:
            options = dict(auth_data)
        
        # Properly encode the response
        publicKey = options["publicKey"]
        if isinstance(publicKey["challenge"], bytes):
            publicKey["challenge"] = base64.b64encode(publicKey["challenge"]).decode()
        
        # Encode credential IDs in allowCredentials
        if "allowCredentials" in publicKey:
            for cred in publicKey["allowCredentials"]:
                if isinstance(cred["id"], bytes):
                    cred["id"] = base64.b64encode(cred["id"]).decode()

        return JsonResponse(options, safe=False)
    
    return JsonResponse({"error": "Invalid request"}, status=400)
# --- Fingerprint Login ---
from fido2.webauthn import PublicKeyCredentialDescriptor
from fido2 import cbor
from fido2.webauthn import AttestedCredentialData

@csrf_exempt
def fingerprint_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        assertion = data.get("assertion")

        try:
            student = Student.objects.get(user__username=username)
        except Student.DoesNotExist:
            return JsonResponse({"success": False, "message": "Student not found"})

        credential_data = student.fingerprint_credential
        if not credential_data:
            return JsonResponse({"success": False, "message": "No fingerprint registered"})

        credential_id = base64.b64decode(credential_data["id"])
        public_key_cbor = base64.b64decode(credential_data["public_key"])
        sign_count = credential_data["sign_count"]
        
        state = request.session.get("fido2_authentication_state")
        if not state:
            return JsonResponse({"error": "No authentication state found."}, status=400)

        try:
            # Decode the assertion data
            client_data = CollectedClientData(base64.b64decode(assertion["response"]["clientDataJSON"]))
            authenticator_data = AuthenticatorData(base64.b64decode(assertion["response"]["authenticatorData"]))
            signature = base64.b64decode(assertion["response"]["signature"])

            # Decode the public key from CBOR
            public_key = cbor.decode(public_key_cbor)
            
            # Create a credential object that the server expects
            credential = AttestedCredentialData.create(
                aaguid=b'\x00' * 16,  # Default AAGUID
                credential_id=credential_id,
                public_key=public_key
            )
            
            # Create the expected credentials list
            credentials = [credential]

            # Verify the assertion with the correct method signature
            server.authenticate_complete(
                state,
                credentials,
                credential_id,
                client_data,
                authenticator_data,
                signature
            )

            # Update sign count
            student.fingerprint_credential["sign_count"] = authenticator_data.counter
            student.save()

            # Eligibility check
            eligible_courses = AttendanceRecord.objects.filter(
                student=student, attendance_percentage__gte=75
            )
            if eligible_courses.exists():
                auth_login(request, student.user)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "message": "Not eligible for exam access"})

        except Exception as e:
            print(f"Authentication error: {e}")
            return JsonResponse({"success": False, "message": f"Authentication failed: {str(e)}"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def fingerprint_login_begin(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        try:
            student = Student.objects.get(user__username=username)
        except Student.DoesNotExist:
            return JsonResponse({"success": False, "message": "Student not found"})

        credential_data = student.fingerprint_credential
        if not credential_data:
            return JsonResponse({"success": False, "message": "No fingerprint registered"})

        # Create credential descriptor for authentication
        credential_id = base64.b64decode(credential_data["id"])
        public_key_cbor = base64.b64decode(credential_data["public_key"])
        public_key = cbor.decode(public_key_cbor)
        
        # Create AttestedCredentialData object
        credential = AttestedCredentialData.create(
            aaguid=b'\x00' * 16,  # Default AAGUID
            credential_id=credential_id,
            public_key=public_key
        )
        
        credentials = [credential]

        # Begin authentication
        auth_data, state = server.authenticate_begin(credentials)
        request.session["fido2_authentication_state"] = state

        # Convert to dict and base64-encode bytes fields
        if hasattr(auth_data, "dict"):
            options = auth_data.dict()
        else:
            options = dict(auth_data)
        
        # Properly encode the response
        publicKey = options["publicKey"]
        if isinstance(publicKey["challenge"], bytes):
            publicKey["challenge"] = base64.b64encode(publicKey["challenge"]).decode()
        
        # Encode credential IDs in allowCredentials
        if "allowCredentials" in publicKey:
            for cred in publicKey["allowCredentials"]:
                if isinstance(cred["id"], bytes):
                    cred["id"] = base64.b64encode(cred["id"]).decode()

        return JsonResponse(options, safe=False)
    
    return JsonResponse({"error": "Invalid request"}, status=400)
# --- Student Dashboard ---
@login_required
def dashboard(request):
    student = request.user.student
    eligible_courses = AttendanceRecord.objects.filter(
        student=student, attendance_percentage__gte=75
    ).select_related("course")

    return render(request, "dashboard.html", {"student": student, "eligible_courses": eligible_courses})
@csrf_exempt
def register_fingerprint_begin(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        try:
            student = Student.objects.get(user__username=username)
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student not found."}, status=404)

        registration_data, state = server.register_begin(
            {
                "id": username.encode(),
                "name": username,
                "displayName": student.user.get_full_name() or username,
            },
            user_verification="preferred"
        )
        request.session["fido2_registration_state"] = state

        # Convert registration_data to a dict
        if hasattr(registration_data, "dict"):
            options = registration_data.dict()
        else:
            options = dict(registration_data)

        # Only base64-encode bytes fields
        publicKey = options["publicKey"]
        if isinstance(publicKey["challenge"], bytes):
            publicKey["challenge"] = base64.b64encode(publicKey["challenge"]).decode()
        if isinstance(publicKey["user"]["id"], bytes):
            publicKey["user"]["id"] = base64.b64encode(publicKey["user"]["id"]).decode()

        return JsonResponse(options, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)
from .models import Exam, ExamQuestion
from django.contrib.auth.decorators import login_required

@login_required
def exam_questions(request, slug):
    exam = Exam.objects.get(slug=slug)
    questions = exam.questions.all()
    return render(request, "exam_questions.html", {"exam": exam, "questions": questions})