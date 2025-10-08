from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from usuario.models import Usuario

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = (
            'username', 'email', 'first_name', 'last_name', 
            'password', 'password_confirm', 'phone', 'date_of_birth'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = Usuario.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Adicionar claims customizados
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        # token['is_verified'] = user.is_verified
        
        return token

    def validate(self, attrs):
        # Permitir login com email ou username
        username = attrs.get('username')
        password = attrs.get('password')
        
        if '@' in username:
            # Tentar autenticar com email
            try:
                user_obj = Usuario.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                raise serializers.ValidationError('Credenciais inválidas.')
        
        attrs['username'] = username
        data = super().validate(attrs)
        
        return data

# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = '__all__'
#         read_only_fields = ('user',)

# class UserProfileSerializer(serializers.ModelSerializer):
#     profile = ProfileSerializer(read_only=True)
#     full_name = serializers.ReadOnlyField()

#     class Meta:
#         model = Usuario
#         fields = (
#             'id', 'username', 'email', 'first_name', 'last_name',
#             'full_name',
#             'is_verified', 'created_at', 'updated_at'
#         )
#         read_only_fields = ('id', 'created_at', 'updated_at', 'is_verified')

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("As novas senhas não coincidem.")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

