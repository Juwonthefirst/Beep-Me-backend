from rest_framework import serializers

class LoginSerializer(serializers.Serializer): 
	username = serializers.CharField(max_length = 60, allow_blank = True)
	email = serializers.EmailField(allow_blank= True)
	password = serializers.CharField(write_only = True)
	
	def validate(self, attrs):
		username = attrs.get("username")
		email = attrs.get("email")
		
		if not(email or username):
			raise serializers.ValidationError("username or email has to be present")
			
		return attrs