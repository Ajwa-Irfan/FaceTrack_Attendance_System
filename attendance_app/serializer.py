from .models import *
from rest_framework import serializers
import base64
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        user = authenticate(email=email, username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid Credentials")
        
        data['user'] = user
        return data


class MemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'face_file', 'image_url', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None
    
class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source = 'member.name', read_only=True)
    time = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ["id", "member_name", "date", "check_in", "check_out", "time"]

    def get_time(self, obj):
        # Agar check_in ho tu wo dikhayega, warna check_out
        if obj.check_in:
            return obj.check_in.strftime("%H:%M:%S")
        elif obj.check_out:
            return obj.check_out.strftime("%H:%M:%S")
        return "-"

class CamerDeviceserializer(serializers.ModelSerializer):
    class Meta:
        model = CameraDevice
        fields = ['id', 'name', 'ip_stream_link', 'location', 'is_active']

class RecognitionLogSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source = 'member.name', read_only = True)
    camera_name = serializers.CharField(source = 'camera.name', read_only = True)

    class Meta:
        model = RecognitionLog
        fields = ['id', 'member', 'member_name', 'detected_at', 'recognized', 'camera', 'camera_name', 'confidence']

class FaceRecognitionInputSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, value):
        return value