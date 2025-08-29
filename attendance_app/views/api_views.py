from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from attendance_app.serializer import *
from attendance_app.models import *
from django.utils.timezone import now
import face_recognition, cv2, pickle, datetime
from face_utils.encoding import get_face_encoding
from face_utils.matcher import match_face
from face_utils.attendance import mark_attendance
from face_utils.build_known_faces import build_known_faces
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone


class LoginView(APIView):
    def post(self, request):
        serialzier = LoginSerializer(data = request.data)
        if serialzier.is_valid():
            user = serialzier.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'access': str(access_token),
                'refresh': str(refresh)
            })
        return Response(serialzier.errors, status=404)

class MemberCreateView(APIView):
    def get(self, request):
        member = Member.objects.all()
        serilaizer = MemberSerializer(member, many=True, context={'request': request})
        return Response(serilaizer.data)
    
    def post(self, request):
        serializer = MemberSerializer(data = request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({"error": "❌ Invalid data", "details": serializer.errors}, status=400)
        
        member = serializer.save()
            
        image_path = member.face_file.path
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            member.delete()
            return Response(
                {"error": "❌ No face found in the image. Please upload a clearer photo."},
                status=400
            )
        new_encoding = encodings[0]
        for existing in Member.objects.exclude(encoding=None):
            existing_encoding = pickle.loads(existing.encoding)
            match = face_recognition.compare_faces(
                [existing_encoding], new_encoding, tolerance=0.6
            )[0]
            if match:
                member.delete()
                return Response(
                    {"error": "❌ This face already exists in the system."},
                    status=400
                )
        member.encoding = pickle.dumps(new_encoding)
        member.save()
        build_known_faces()
        return Response({"detail": "Member added successfully."}, status=201)

class FaceRecognitionView(APIView):
    def post(self, request):
        serializer = FaceRecognitionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_path = "temp.jpg"
        try:
            # Save uploaded image
            with open(temp_path, "wb+") as f:
                for chunk in serializer.validated_data["image"].chunks():
                    f.write(chunk)

            # Detect multiple encodings
            unknown_encodings = get_face_encoding(temp_path)  # 👈 ye ab list return karega
            if not unknown_encodings or len(unknown_encodings) == 0:
                RecognitionLog.objects.create(
                    recognized=False,
                    confidence=0.0,
                    error="No face detected"
                )
                return Response(
                    {"detail": "No face detected in image"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Load known encodings from pickle
            try:
                with open("known_faces.pkl", "rb") as f:
                    known_data = pickle.load(f)
                    known_encodings = known_data["encodings"]
                    member_ids = known_data["members"]
            except Exception as e:
                return Response(
                    {"error": "System configuration error", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            results = []
            unknown_count = 0

            # Loop through each detected face
            for unknown_encoding in unknown_encodings:
                match_index, confidence = match_face(
                    unknown_encoding,
                    known_encodings,
                    tolerance=0.40
                )

                if match_index is not None and confidence > 0.5:
                    try:
                        member = Member.objects.get(id=member_ids[match_index])
                        mark_attendance(member, confidence=confidence)

                        results.append({
                            "status": "recognized",
                            "member_id": member.id,
                            "name": member.name,
                            "confidence": round(confidence, 2)
                        })
                    except Member.DoesNotExist:
                        unknown_count += 1
                        RecognitionLog.objects.create(
                            recognized=False,
                            confidence=0.0,
                            error="Matched ID not found in DB"
                        )
                    
                else:
                    unknown_count += 1
                    results.append({
                        "status": "unknown",
                        "confidence": 0.0
                    })

            return Response({
                "recognized": results,
                "unknown_count": unknown_count
            })

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TodayAttendanceView(APIView):
   def get(self, request):
      today = timezone.localdate()
      attendance = Attendance.objects.filter(date=today)
      serializer = AttendanceSerializer(attendance, many=True)
      return Response(serializer.data)
   
class LiveAttendanceView(APIView):
   def get(self, request):
      today = timezone.localdate()
      attendance = Attendance.objects.filter(date=today).order_by('-check_in')[:5]
      serializer = AttendanceSerializer(attendance, many=True)
      return Response(serializer.data)
   
class RecognitionLogListView(APIView):
   def get(self, request):
      log = RecognitionLog.objects.order_by('-detected_at')[:10]
      serializer = RecognitionLogSerializer(log, many=True)
      return Response(serializer.data)